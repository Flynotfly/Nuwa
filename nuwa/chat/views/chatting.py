import base64
import json
import os
import random
import time
import requests

from django.conf import settings
from django.utils import timezone
from ollama import Client
from openai import OpenAI
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Chat, Message
from chat.utils import update_chat_structure, generate_image
from chat.serializers.message import MessageSerializer

client = Client(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + settings.OLLAMA_API_KEY},
)

# client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key=settings.OPENROUTER_KEY,
# )
model = "qwen3-next:80b"
# model = "cognitivecomputations/dolphin-mistral-24b-venice-edition:free"


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

        chat = Chat.objects.filter(pk=chat_id, owner=self.request.user).first()
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
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "think": "low",
        }
        try:
            response = client.chat(**payload)
                # response = client.chat.completions.create(model=model, messages=messages)
            ai_response = response.message.content
                # ai_response = response.choices[0].message.content
            # ai_response = "Hello user!"
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
        message_history = [] if not previous_message_id else all_message_ids
        user_message = Message.objects.create(
            owner=self.request.user,
            chat=chat,
            role="user",
            media_type="text",
            message=user_message,
            conducted=timezone.now(),
            history=message_history,
        )
        structure = update_chat_structure(
            chat.structure,
            previous_message_id if previous_message_id else None,
            user_message.pk,
            user_message.history,
        )
        ai_history = message_history + [user_message.pk]
        ai_message = Message.objects.create(
            owner=self.request.user,
            chat=chat,
            role="assistant",
            media_type="text",
            message=ai_response,
            conducted=timezone.now(),
            history=ai_history,
        )
        chat.last_message = ai_message
        chat.last_message_text = ai_message.message
        chat.last_message_datetime = ai_message.conducted
        chat.structure = update_chat_structure(
            structure,
            user_message.pk,
            ai_message.pk,
            ai_message.history,
        )
        chat.save()
        user_serializer = MessageSerializer(user_message)
        ai_serializer = MessageSerializer(ai_message)
        return Response(
            {
                "user_message": user_serializer.data,
                "ai_message": ai_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class GenerateImageView(APIView):
    def post(self, request):
        chat_id = request.data.get("chat_id")
        previous_message_id = request.data.get("previous_message_id")
        if not chat_id:
            return Response(
                {"error": "chat_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        chat = Chat.objects.filter(pk=chat_id, owner=self.request.user).first()
        if not chat:
            return Response(
                {"error": "Chat id is invalid"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        system_prompt = ("Write positive promt for ai image generator. "
                         "It should containts keywords or key phrases separates by comma. "
                         "Do not write anything else. "
                         "You will be given prompt defenition and chat "
                         "history beetwen user and character. "
                         "take into account the character's condition posture and "
                         "clothes at the end of the dialogue."
                         "Character definition: "
                         ""
                         "")
        system_prompt = system_prompt + chat.system_prompt
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
            ).order_by("-conducted")[:50]
            history = reversed(list(history))
            for message in history:
                if message.media_type != "text":
                    continue
                messages.append({"role": message.role, "content": message.message})
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "think": "medium",
        }
        try:
            response = client.chat(**payload)
            positive_prompt = response.message.content
            print("positive prompt: ", positive_prompt)
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

        try:
            result = generate_image(
                positive_prompt=positive_prompt
            )
            return Response(result, status=status.HTTP_200_OK)

        except FileNotFoundError:
            return Response(
                {"error": "Workflow file not found"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except requests.RequestException as e:
            return Response(
                {"error": "Failed to communicate with ComfyUI", "detail": str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except TimeoutError:
            return Response(
                {"error": "ComfyUI generation timed out"},
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except Exception as e:
            return Response(
                {"error": "Image generation failed", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )