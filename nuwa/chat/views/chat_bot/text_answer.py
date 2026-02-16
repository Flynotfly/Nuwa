import json

import requests
from django.conf import settings
from django.http import StreamingHttpResponse
from ollama import Client as OllamaClient
from openai import OpenAI
from rest_framework import status
from rest_framework.response import Response

from chat.models import Chat, Message
from chat.views.chat_bot.utils import (MessageData,
                                       append_text_messages_from_history,
                                       save_messages)
from chat.providers import MODELS


def generate_text_answer(
        chat: Chat,
        previous_message: Message | None,
        is_user_message: bool,
        user_input: str | None,
        user,
        received_at,
        is_stream: bool = False,
        is_return_response: bool = True,
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
    if is_stream:
        return handle_stream_response(
            messages=messages,
            chat=chat,
            user=user,
            previous_message=previous_message,
            user_input=user_input,
            is_user_message=is_user_message,
            received_at=received_at,
        )
    else:
        return handle_common_response(
            messages=messages,
            chat=chat,
            user=user,
            previous_message=previous_message,
            user_input=user_input,
            is_user_message=is_user_message,
            received_at=received_at,
            is_return_response=is_return_response,
        )


def handle_stream_response(
        messages: list,
        chat: Chat,
        user,
        previous_message: Message | None,
        user_input: str | None,
        is_user_message: bool,
        received_at,
):
    def event_stream():
        collected_chunks = []
        meta_info = {}
        try:
            stream, meta_info = generate_text(
                messages=messages,
                stream=True,
                **MODELS["text_answer"],
            )
            for chunk in stream:
                collected_chunks.append(chunk)
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'detail': str(e)})}\n\n"
            return
        ai_response = "".join(collected_chunks)
        returned_messages = handle_save_messages(
            chat=chat,
            user=user,
            previous_message=previous_message,
            user_input=user_input,
            ai_response=ai_response,
            is_user_message=is_user_message,
            received_at=received_at,
            meta_info=meta_info
        )
        yield f"data: {json.dumps({'type': 'done', 'messages': returned_messages})}\n\n"
    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


def handle_common_response(
        messages: list,
        chat: Chat,
        user,
        previous_message: Message | None,
        user_input: str | None,
        is_user_message: bool,
        received_at,
        is_return_response: bool,
):
    try:
        ai_response, meta_info = generate_text(messages=messages, **MODELS["text_answer"])
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
    return handle_save_messages(
        chat=chat,
        user=user,
        previous_message=previous_message,
        user_input=user_input,
        ai_response=ai_response,
        is_user_message=is_user_message,
        received_at=received_at,
        meta_info=meta_info,
        is_return_response=is_return_response,
    )


def handle_save_messages(
        chat: Chat,
        user,
        previous_message: Message | None,
        user_input: str | None,
        ai_response: str,
        is_user_message: bool,
        received_at,
        meta_info,
        is_return_response: bool = False,
):
    ai_response = ai_response.strip()
    ai_message_data = MessageData(
        role="assistant",
        media_type="text",
        message=ai_response,
        info=meta_info,
    )
    if is_user_message:
        user_message_data = MessageData(
            role="user",
            media_type="text",
            message=user_input,
            conducted=received_at,
        )
        messages_to_send = [
            user_message_data,
            ai_message_data,
        ]
    else:
        messages_to_send = [ai_message_data]
    returned_messages = save_messages(
        chat=chat,
        user=user,
        previous_message=previous_message,
        messages=messages_to_send,
    )
    if is_return_response:
        return Response(
            {"messages": returned_messages},
            status=status.HTTP_200_OK,
        )
    return returned_messages


def generate_text(
        messages: list,
        provider: str,
        model: str,
        think: str | None = None,
        stream: bool = False,
):
    if stream:
        match provider:
            case "ollama-cloud":
                return generate_with_ollama_cloud_stream(
                    messages=messages,
                    model=model,
                    think=think,
                )
            case "openrouter":
                return generate_with_openrouter_stream(
                    messages=messages,
                    model=model,
                    think=think
                )
    match provider:
        case "ollama-cloud":
            return generate_with_ollama_cloud(
                messages=messages,
                model=model,
                think=think,
            )
        case "openrouter":
            return generate_with_openrouter(
                messages=messages,
                model=model,
                think=think,
            )


ollama_cloud_client = OllamaClient(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + settings.OLLAMA_API_KEY},
)


def generate_with_ollama_cloud(
        messages: list,
        model: str,
        think: str | None = None,
):
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    if think:
        payload["think"] = think
    response = ollama_cloud_client.chat(**payload)
    content = response.message.content
    return (
        content,
        {
            "provider": "Ollama cloud",
            "model": payload["model"],
            "think": think,
        },
    )


def generate_with_ollama_cloud_stream(
        messages: list,
        model: str,
        think: str | None,
):
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
    }
    if think:
        payload["think"] = think
    meta_info = {
        "provider": "Ollama cloud",
        "model": model,
        "think": think,
    }

    def stream_generator():
        for chunk in ollama_cloud_client.chat(**payload):
            content = chunk.message.content
            if content:
                yield content

    return stream_generator(), meta_info


openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_KEY,
)


def generate_with_openrouter(
    messages: list,
    model: str,
    think: str | None = None,
):
    payload = {
        "model": model,
        "messages": messages,
    }
    if think:
        payload["think"] = think
    response = openrouter_client.chat.completions.create(**payload)
    content = response.choices[0].message.content
    return (
        content,
        {
            "provider": "Openrouter",
            "model": payload["model"],
            "think": think,
        },
    )


def generate_with_openrouter_stream(
        messages: list,
        model: str,
        think: str | None,
):
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
    }
    if think:
        payload["reasoning"] = {"effort": think}
    meta_info = {
        "provider": "Openrouter",
        "model": payload["model"],
        "think": think,
    }

    def stream_generator():
        stream = openrouter_client.chat.completions.create(**payload)
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return stream_generator(), meta_info
