import requests

from django.conf import settings
from django.utils import timezone
from ollama import Client as OllamaClient
from rest_framework import status
from rest_framework.response import Response

from chat.models import Chat, Message
from chat.serializers.message import MessageSerializer
from chat.utils import update_chat_structure


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
        message_history_ids = previous_message.history
        all_message_ids = list(message_history_ids) + [previous_message.pk]
        history = Message.objects.filter(
            owner=user,
            pk__in=all_message_ids,
            chat=chat
        ).order_by("-conducted")[:30]
        history = reversed(list(history))
        for message in history:
            if message.media_type != "text":
                continue
            messages.append({"role": message.role, "content": message.message})
    if user_input:
        messages.append({"role": "user", "content": user_input})
    try:
        ai_response, meta_info = generate_with_ollama_cloud(messages)
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
        structure = update_chat_structure(
            chat.structure,
            previous_message.pk if previous_message else None,
            user_message.pk,
            user_message.history[:-1] if len(user_message.history) > 0 else [],
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
        chat.structure = update_chat_structure(
            structure,
            user_message.pk,
            ai_message.pk,
            user_message.history,
        )

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
        chat.structure = update_chat_structure(
            chat.structure,
            previous_message.pk if previous_message else None,
            ai_message.pk,
            ai_message.history[:-1] if len(ai_message.history) > 0 else [],
        )

    chat.last_message = ai_message
    chat.last_message_text = ai_message.message
    chat.last_message_datetime = ai_message.conducted
    chat.save()
    ai_serializer = MessageSerializer(ai_message)

    if is_user_message:
        user_serializer = MessageSerializer(user_message)
        returned_messages = [
            user_serializer.data,
            ai_serializer.data,
        ]
    else:
        returned_messages = [
            ai_serializer.data
        ]

    return Response(
        {
            "messages": returned_messages
        },
        status=status.HTTP_200_OK,
    )


ollama_cloud_client = OllamaClient(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + settings.OLLAMA_API_KEY},
)


def generate_with_ollama_cloud(messages: list):
    payload = {
        "model": "qwen3-next:80b",
        "messages": messages,
        "stream": False,
        "think": "low"
    }
    response = ollama_cloud_client.chat(**payload)
    return (
        response.message.content,
        {
            "provider": "ollame_cloud",
            "model": "qwen3-next:80b",
            "think": "low",
        },
    )
