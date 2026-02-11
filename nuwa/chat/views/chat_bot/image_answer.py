import base64
import json
import os
import random
import time

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from chat.models import Chat, Message
from chat.serializers.message import MessageSerializer
from chat.utils import update_chat_structure
from chat.views.chat_bot.text_answer import generate_with_ollama_cloud
from chat.views.chat_bot.utils import (MessageData,
                                       append_text_messages_from_history,
                                       save_messages,
                                       update_chat_info_with_single_message,
                                       update_chat_info_with_two_messages)


def generate_image_answer(
    chat: Chat,
    previous_message: Message | None,
    is_user_message: bool,
    user_input: str | None,
    user,
    received_at,
):
    try:
        positive_prompt, posotive_promt_meta = get_positive_prompt(
            chat=chat,
            previous_message=previous_message,
            user_input=user_input,
            user=user,
        )
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
        result, result_meta = generate_with_comfy_ui(positive_prompt=positive_prompt)
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
    try:
        image_data = base64.b64decode(result["image_base64"])
        image_content = ContentFile(image_data)
        filename = result.get("filename")
        message_history = []
        if previous_message:
            prev_message_history = previous_message.history
            message_history = list(prev_message_history) + [previous_message.pk]
        ai_message_data = MessageData(
            role="assistant",
            media_type="image",
            info={
                "generation_info": result_meta,
                "prompt_generation_info": posotive_promt_meta,
            },
            filename=filename,
            media_content=image_content,
        )
        if is_user_message:
            user_message_data = MessageData(
                role="user",
                media_type="text",
                message=user_input,
                conducted=received_at,
            )
            user_message, ai_message = save_messages(
                chat=chat,
                user=user,
                history=message_history,
                messages=[
                    user_message_data,
                    ai_message_data,
                ],
            )
            update_chat_info_with_two_messages(
                chat=chat,
                message_1=user_message,
                message_2=ai_message,
                message_with_text=user_message,
                previous_message=previous_message,
            )
            user_serializer = MessageSerializer(user_message)
            ai_serializer = MessageSerializer(ai_message)
            returned_messages = [
                user_serializer.data,
                ai_serializer.data,
            ]
        else:
            [ai_message] = save_messages(
                chat=chat,
                user=user,
                history=message_history,
                messages=[ai_message_data]
            )
            ai_message = Message.objects.create(
                owner=user,
                chat=chat,
                role="assistant",
                media_type="image",
                message="",
                conducted=timezone.now(),
                history=message_history,
                info={
                    "generation_info": result_meta,
                    "prompt_generation_info": posotive_promt_meta,
                },
            )
            ai_message.media.save(filename, image_content, save=True)
            update_chat_info_with_single_message(
                chat=chat,
                message=ai_message,
                message_with_text=False,
                previous_message=previous_message,
            )
            ai_serializer = MessageSerializer(ai_message)
            returned_messages = [ai_serializer.data]
        return Response(
            {
                "messages": returned_messages,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"error": "Failed to save image", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


SYSTEM_PROMT_START = (
    "Write positive promt for ai image generator. "
    "It should containts keywords or key phrases separates by comma. "
    "Do not write anything else. "
    "You will be given prompt defenition and chat "
    "history beetwen user and character. "
    "take into account the character's condition posture and "
    "clothes at the end of the dialogue."
    ""
)
SYSTEM_PROMPT_USER_SPECIFIC = (
    "The user wants to focus especially on these details. "
    "Use the details, clothes, pose, and more from the following sentence:"
    ""
)
SYSTEM_PROMPT_CONTINUE = "Character definition: " "" ""


def get_positive_prompt(
    chat: Chat,
    previous_message: Message | None,
    user_input: str | None,
    user,
):
    if user_input:
        system_prompt = (
            SYSTEM_PROMT_START
            + SYSTEM_PROMPT_USER_SPECIFIC
            + user_input
            + SYSTEM_PROMPT_CONTINUE
            + chat.system_prompt
        )
    else:
        system_prompt = SYSTEM_PROMT_START + SYSTEM_PROMPT_CONTINUE + chat.system_prompt
    messages = [{"role": "system", "content": system_prompt}]
    if previous_message:
        append_text_messages_from_history(
            messages=messages,
            previous_message=previous_message,
            chat=chat,
            user=user,
        )
    return generate_with_ollama_cloud(
        messages=messages,
        think="medium",
    )


COMFY_WORKFLOW_PATH = os.path.join(
    settings.BASE_DIR, "workflows", "test_character.json"
)
COMFY_URL = "http://127.0.0.1:8188"


def generate_with_comfy_ui(positive_prompt):
    positive_prompt = "Stable_Yogis_SD1.5_Positives, " + positive_prompt
    with open(COMFY_WORKFLOW_PATH, "r") as f:
        workflow = json.load(f)
    seed = random.randint(0, 999_999_999_999_999)
    workflow["3"]["inputs"]["seed"] = seed
    workflow["6"]["inputs"]["text"] = positive_prompt
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

                    image_base64 = base64.b64encode(img_resp.content).decode("utf-8")

                    return (
                        {
                            "image_base64": image_base64,
                            "filename": filename,
                        },
                        {
                            "model": "realismByStableYogi_sd15V9",
                            "positive_prompt": positive_prompt,
                            "negative_prompt": "Stable_Yogis_SD1.5_Negatives",
                            "seed": seed,
                        },
                    )
                else:
                    raise ValueError("Workflow completed but no image found in outputs")

        except requests.RequestException as e:
            pass

        time.sleep(retry_interval)

    raise TimeoutError("ComfyUI image generation timed out")
