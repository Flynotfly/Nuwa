import time

import requests
import os
import json
import random
import uuid

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from ollama import Client

from chat.models import Character


client = Client(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + settings.OLLAMA_API_KEY}
)
model = "qwen3-next:80b"


class ChatBotView(APIView):
    def post(self, request):
        user_message = request.data.get("message")
        character_id = request.data.get("character_id")
        print(f"message: {user_message}")
        if not user_message:
            return Response(
                {"error": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST
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
                status=status.HTTP_400_BAD_REQUEST
            )
        valid_roles = {"user", "assistant"}
        for msg in history:
            if not isinstance(msg, dict):
                return Response(
                    {"error": "Each message in 'history' must be an object with 'role' and 'content'."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            role = msg.get("role")
            content = msg.get("content")
            if role not in valid_roles or not isinstance(content, str) or not content.strip():
                return Response(
                    {
                        "error": "Each history message must have a 'role' "
                                 "('user' or 'assistant') and non-empty 'content'."},
                    status=status.HTTP_400_BAD_REQUEST
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
            return Response(
                {"response": ai_response},
                status=status.HTTP_200_OK
            )
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": "Failed to reach AI service", "detail": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )

        except Exception as e:
            return Response(
                {"error": "AI generation failed", "detail": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )


WEBHOOK_STORE = {}
COMFY_WORKFLOW_PATH = os.path.join(settings.BASE_DIR, "workflows", "test_character.json")
COMFY_URL = "http://127.0.0.1:8188"
WEBHOOK_BASE_URL = "http://127.0.0.1:8000"


@method_decorator(csrf_exempt, name='dispatch')
class ComfyWebhookReceiver(APIView):
    def post(self, request):
        payload = request.data
        print(f"received: {payload}")
        prompt_id = payload.get("id")
        images = payload.get("images", [])
        filenames = payload.get("filenames", [])

        if prompt_id and images:
            # Store first base64 image
            WEBHOOK_STORE[prompt_id] = {
                "image_base64": images[0],
                "filename": filenames[0],
                "received": True,
            }
            return Response({"status": "ok"}, status=200)
        return Response({"error": "Invalid payload"}, status=400)


class GenerateImageView(APIView):
    def post(self, request):
        with open(COMFY_WORKFLOW_PATH, "r") as f:
            workflow = json.load(f)
        seed = random.randint(0, 999_999_999_999_999)
        workflow["3"]["inputs"]["seed"] = seed
        prompt_id = str(uuid.uuid4())
        payload = {
            "id": prompt_id,
            "prompt": workflow,
            "webhook_v2": f"{WEBHOOK_BASE_URL}/comfy-webhook",
        }
        response = requests.post(
            f"{COMFY_URL}/prompt",
            json=payload,
            timeout=15,
        )
        response.raise_for_status()

        for _ in range(60):
            if prompt_id in WEBHOOK_STORE:
                result = WEBHOOK_STORE.pop(prompt_id)
                return Response({
                    "image_base64": result["image_base64"],
                    "filename": result["filename"],
                }, status=status.HTTP_200_OK)
            time.sleep(1)

        return Response(
            {"error": "Webhook timed out"},
            status=status.HTTP_504_GATEWAY_TIMEOUT
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
