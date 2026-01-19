import base64
import json
import os
import random
import time
import uuid

import requests
from django.utils import timezone
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from ollama import Client
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Character, Message, Chat

client = Client(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + settings.OLLAMA_API_KEY},
)
model = "qwen3-next:80b"


class ChatBotView(APIView):
    def post(self, request):
        user_message = request.data.get("message")
        chat_id = request.data.get("chat_id")
        previous_message_id = request.data.get("previous_message_id", None)

        print(f"User message: {user_message}")
        if not user_message:
            return Response(
                {"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        if not chat_id:
            return Response(
                {"error": "chat_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_message = user_message.strip()

        chat = Chat.objects.filter(
            pk=chat_id,
            owner=self.request.user
        ).first()
        if not chat:
            return Response(
                {"error": "Chat id is invalid"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        system_prompt = chat.system_prompt
        messages = [{"role": "system", "content": system_prompt}]

        if previous_message_id:
            previous_message = Message.objects.filter(
                pk=previous_message_id,
                owner=self.request.user,
                chat=chat,
            ).first()
            if not previous_message:
                return Response(
                    {"error": "Previous_message_id is invalid"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            message_history_ids = previous_message.history
            all_message_ids = list(message_history_ids) + [previous_message.pk]
            history = Message.objects.filter(
                owner=self.request.user,
                pk__in=all_message_ids,
                chat=chat,
            ).order_by("-conducted")[:30]
            history = reversed(list(history))
            for message in history:
                if message.media_type != "text":
                    continue
                messages.append({"role": message.role, "content": message.message})

        messages.append({"role": "user", "content": user_message})
        message_history = [] if not previous_message_id else all_message_ids
        user_message = Message.objects.create(
            owner=self.request.user,
            chat=chat,
            role="user",
            media_type="text",
            message=user_message,
            conducted=timezone.now(),
            history=message_history
        )
        chat.last_message = user_message
        chat.last_message_text = user_message.message
        chat.last_message_datetime = user_message.conducted
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "think": "low",
        }
        try:
            response = client.chat(**payload)
            ai_response = response.message.content
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": "Failed to reach AI service", "detail": str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except Exception as e:
            return Response(
                {"error": "AI generation failed", "detail": str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        ai_response = ai_response.strip()
        print(f"Answer: {ai_response}")
        message_history.append(user_message.pk)
        ai_message = Message.objects.create(
            owner=self.request.user,
            chat=chat,
            role="assistant",
            media_type="text",
            message=ai_response,
            conducted=timezone.now(),
            history=message_history,
        )
        chat.last_message = ai_message
        chat.last_message_text = ai_message.message
        chat.last_message_datetime = ai_message.conducted
        return Response({
            "response": ai_response,
            "message_id": ai_message.pk,
        }, status=status.HTTP_200_OK)


COMFY_WORKFLOW_PATH = os.path.join(
    settings.BASE_DIR, "workflows", "test_character.json"
)
COMFY_URL = "http://127.0.0.1:8188"


class GenerateImageView(APIView):
    def post(self, request):
        with open(COMFY_WORKFLOW_PATH, "r") as f:
            workflow = json.load(f)
        seed = random.randint(0, 999_999_999_999_999)
        workflow["3"]["inputs"]["seed"] = seed
        payload = {
            "prompt": workflow,
        }
        response = requests.post(
            f"{COMFY_URL}/api/prompt",
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
        response_data = response.json()
        prompt_id = response_data["prompt_id"]
        print(f"Prompt submitted. ID: {prompt_id}")

        max_retries = 60
        retry_interval = 1

        for _ in range(max_retries):
            try:
                history_resp = requests.get(
                    f"{COMFY_URL}/api/history/{prompt_id}", timeout=5
                )
                history_resp.raise_for_status()
                history = history_resp.json()

                if prompt_id in history:
                    prompt_data = history[prompt_id]
                    outputs = prompt_data.get("outputs", {})

                    # Look for SaveImage node output (node "9" in your case)
                    if "9" in outputs and "images" in outputs["9"]:
                        image_info = outputs["9"]["images"][0]
                        filename = image_info["filename"]
                        subfolder = image_info.get("subfolder", "")
                        type_ = image_info.get("type", "output")

                        # Fetch the actual image
                        img_resp = requests.get(
                            f"{COMFY_URL}/view",
                            params={
                                "filename": filename,
                                "type": type_,
                                "subfolder": subfolder,
                            },
                            timeout=10,
                        )
                        img_resp.raise_for_status()

                        image_base64 = base64.b64encode(img_resp.content).decode(
                            "utf-8"
                        )

                        return Response(
                            {
                                "image_base64": image_base64,
                                "filename": filename,
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        return Response(
                            {
                                "error": "Workflow completed but no image found in outputs"
                            },
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )

            except requests.RequestException as e:
                pass

            time.sleep(retry_interval)

        return Response(
            {"error": "ComfyUI generation timed out"},
            status=status.HTTP_504_GATEWAY_TIMEOUT,
        )

        # except FileNotFoundError:
        #     return Response(
        #         {"error": "Workflow file not found"},
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )
        # except requests.exceptions.RequestException as e:
        #     return Response(
        #         {"error": "Failed to communicate with ComfyUI", "detail": str(e)},
        #         status=status.HTTP_502_BAD_GATEWAY
        #     )
        # except Exception as e:
        #     return Response(
        #         {"error": "Image generation failed", "detail": str(e)},
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )
