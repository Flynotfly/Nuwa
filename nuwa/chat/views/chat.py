import base64
import json
import os
import random
import time
import uuid

import requests
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from ollama import Client
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Character

client = Client(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + settings.OLLAMA_API_KEY},
)
model = "qwen3-next:80b"


class ChatBotView(APIView):
    def post(self, request):
        user_message = request.data.get("message")
        character_id = request.data.get("character_id")
        print(f"message: {user_message}")
        if not user_message:
            return Response(
                {"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        if not character_id:
            return Response(
                {"error": "Character_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        character = Character.objects.filter(pk=character_id).first()
        if not character:
            return Response(
                {"error": "Character id is invalid"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        system_prompt = character.system_prompt
        messages = [{"role": "system", "content": system_prompt}]

        history = request.data.get("history", [])
        if not isinstance(history, list):
            return Response(
                {"error": "'history' must be a list of message objects."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        valid_roles = {"user", "assistant"}
        for msg in history:
            if not isinstance(msg, dict):
                return Response(
                    {
                        "error": "Each message in 'history' must be an object with 'role' and 'content'."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            role = msg.get("role")
            content = msg.get("content")
            if (
                role not in valid_roles
                or not isinstance(content, str)
                or not content.strip()
            ):
                return Response(
                    {
                        "error": "Each history message must have a 'role' "
                        "('user' or 'assistant') and non-empty 'content'."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        messages.extend(history)
        messages.append({"role": "user", "content": user_message.strip()})

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "think": "low",
        }
        try:
            response = client.chat(**payload)
            ai_response = response.message.content
            print(f"Answer: {ai_response}")
            return Response({"response": ai_response}, status=status.HTTP_200_OK)
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
