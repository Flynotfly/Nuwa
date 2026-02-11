import requests
from django.conf import settings
from django.utils import timezone
from ollama import Client as OllamaClient
from openai import OpenAI
from rest_framework import status
from rest_framework.response import Response

from chat.models import Chat, Message
from chat.serializers.message import MessageSerializer
from chat.utils import update_chat_structure
from chat.views.chat_bot.utils import append_text_messages_from_history, update_chat_info_with_single_message, update_chat_info_with_two_messages


def generate_text_answer(
    chat: Chat,
    previous_message: Message | None,
    is_user_message: bool,
    user_input: str | None,
    user,
    received_at,
):
    system_prompt = chat.system_prompt
    messages = [{"role": "system", "content": system_prompt}]
    if previous_message:
        append_text_messages_from_history(
            messages=messages,
            previous_message=previous_message,
            chat=chat,
            user=user,
        )
    if user_input:
        messages.append({"role": "user", "content": user_input})
    try:
        ai_response, meta_info = generate_with_ollama_cloud(messages=messages)
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
    message_history = [] if not previous_message else all_message_ids
    if is_user_message:
        user_message = Message.objects.create(
            owner=user,
            chat=chat,
            role="user",
            media_type="text",
            message=user_input,
            conducted=received_at,
            history=message_history,
        )
        ai_history = message_history + [user_message.pk]
        ai_message = Message.objects.create(
            owner=user,
            chat=chat,
            role="assistant",
            media_type="text",
            message=ai_response,
            conducted=timezone.now(),
            history=ai_history,
            info=meta_info,
        )
        update_chat_info_with_two_messages(
            chat=chat,
            message_1=user_message,
            message_2=ai_message,
            message_with_text=ai_message,
            previous_message=previous_message,
        )
        user_serializer = MessageSerializer(user_message)
        ai_serializer = MessageSerializer(ai_message)
        returned_messages = [
            user_serializer.data,
            ai_serializer.data,
        ]
    else:
        ai_message = Message.objects.create(
            owner=user,
            chat=chat,
            role="assistant",
            media_type="text",
            message=ai_response,
            conducted=timezone.now(),
            history=message_history,
            info=meta_info,
        )
        update_chat_info_with_single_message(
            chat=chat,
            message=ai_message,
            message_with_text=True,
            previous_message=previous_message,
        )
        ai_serializer = MessageSerializer(ai_message)
        returned_messages = [ai_serializer.data]
    return Response(
        {"messages": returned_messages},
        status=status.HTTP_200_OK,
    )


ollama_cloud_client = OllamaClient(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + settings.OLLAMA_API_KEY},
)


def generate_with_ollama_cloud(
    messages: list,
    model: str | None = None,
    think: str | None = None,
):
    payload = {
        "model": model if model is not None else "qwen3-next:80b",
        "messages": messages,
        "stream": False,
        "think": think if think is not None else "low",
    }
    response = ollama_cloud_client.chat(**payload)
    content = response.message.content
    return (
        content,
        {
            "provider": "Ollama cloud",
            "model": payload["model"],
            "think": payload["think"],
        },
    )


openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_KEY,
)


def generate_with_openrouter(
    messages: list,
    model: str | None = None,
):
    payload = {
        "model": (
            model
            if model is not None
            else "cognitivecomputations/dolphin-mistral-24b-venice-edition:free"
        ),
        "messages": messages,
    }
    response = openrouter_client.chat.completions.create(**payload)
    content = response.choices[0].message.content
    return (
        content,
        {
            "provider": "Openrouter",
            "model": payload["model"],
        },
    )
