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
        if not user_message:
            return Response(
                {"error": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
            "stream": False,
            "think": "medium",
        }
        try:
            response = client.chat(**payload)
            ai_response = response.message.content
            return Response(
                {"response": ai_response},
                status=status.HTTP_200_OK
            )
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": "Failed to reach AI service", "detail": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )
