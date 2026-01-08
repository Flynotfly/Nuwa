import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from ollama import Client

client = Client(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + settings.OLLAMA_API_KEY}
)
model = "qwen3-next:80b"


class ChatBotView(APIView):
    def post(self, request):
        user_message = request.data.get("message")
        print(f"message: {user_message}")
        if not user_message:
            return Response(
                {"error": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        scenario = request.data.get("scenario", "").strip()
        personality = request.data.get("personality", "").strip()
        example_dialogs = request.data.get("example_dialogs", "").strip()

        system_parts = []
        if scenario:
            system_parts.append(f"Scenario: {scenario}")
        if personality:
            system_parts.append(f"Personality: {personality}")
        if example_dialogs:
            system_parts.append(f"Example dialog:\n{example_dialogs}")

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

        messages = []
        if system_parts:
            system_prompt = "\n\n".join(system_parts)
            messages.append({"role": "system", "content": system_prompt})

        messages.extend(history)
        messages.append({"role": "user", "content": user_message.strip()})

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "think": "medium",
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
