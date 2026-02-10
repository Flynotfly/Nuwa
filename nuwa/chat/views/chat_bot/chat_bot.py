import base64

import requests
from django.core.files.base import ContentFile
from django.utils import timezone
from openai import OpenAI
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Chat, Message
from chat.serializers.message import MessageSerializer
from chat.utils import generate_image, update_chat_structure
from chat.views.chat_bot.text_answer import generate_text_answer


ALLOWED_ANSWER_TYPES = {
    "detect",
    "text",
    "image",
    "video"
}


class ChatBotView(APIView):
    def post(self, request):
        received_at = timezone.now()

        user_input = request.data.get("message", None)
        chat_id = request.data.get("chat_id")
        previous_message_id = request.data.get("previous_message_id", None)
        is_user_message = request.data.get("is_user_message", False)
        answer_type = request.data.get("answer_type", "detect")

        if user_input is not None:
            user_input = user_input.strip()
        if not chat_id:
            return Response(
                {"error": "chat_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if answer_type not in ALLOWED_ANSWER_TYPES:
            return Response(
                {"error": f"Wrong 'answer_type'. Allowed answer types: {ALLOWED_ANSWER_TYPES}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if is_user_message == "false":
            is_user_message = False
        elif is_user_message == "true":
            is_user_message = True
        elif is_user_message == "True" or is_user_message == "False":
            is_user_message = bool(is_user_message)
        if is_user_message is not False and is_user_message is not True:
            return Response(
                {"error": "Wrong 'is_user_message'. Allowed only boolean type."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if is_user_message and not user_input:
            return Response(
                {"error": "As 'is_user_message' is true, 'user_message' should be provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        chat_id = int(chat_id)
        chat = Chat.objects.filter(pk=chat_id, owner=self.request.user).first()
        if not chat:
            return Response(
                {"error": "Chat id is invalid"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if previous_message_id:
            previous_message_id = int(previous_message_id)
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

        if answer_type == "detect":
            ...

        match answer_type:
            case "text":
                return generate_text_answer(
                    chat,
                    previous_message if previous_message_id else None,
                    is_user_message,
                    user_input,
                    self.request.user,
                    received_at
                )
            case "image":
                ...
            case "video":
                ...


class GenerateImageView(APIView):
    def post(self, request):
        chat_id = request.data.get("chat_id")
        previous_message_id = request.data.get("previous_message_id", None)
        user_message = request.data.get("message", None)
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
        system_prompt = (
            "Write positive promt for ai image generator. "
            "It should containts keywords or key phrases separates by comma. "
            "Do not write anything else. "
            "You will be given prompt defenition and chat "
            "history beetwen user and character. "
            "take into account the character's condition posture and "
            "clothes at the end of the dialogue."
            ""
        )
        system_prompt_user_specific = (
            "The user wants to focus especially on these details. "
            "Use the details, clothes, pose, and more from the following sentence:"
            ""
        )
        system_prompt_continue = "Character definition: " "" ""
        if user_message:
            system_prompt = (
                system_prompt
                + system_prompt_user_specific
                + user_message.strip()
                + system_prompt_continue
            )
        else:
            system_prompt = system_prompt + system_prompt_continue
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
            result = generate_image(positive_prompt=positive_prompt)

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

            message_history = [] if not previous_message_id else all_message_ids
            new_message = Message.objects.create(
                owner=request.user,
                chat=chat,
                role="assistant",
                media_type="image",
                message="",
                conducted=timezone.now(),
                history=message_history,
                is_active=True,
                info={
                    "model": "realismByStableYogi_sd15V9",
                    "positive_prompt": positive_prompt,
                },
            )
            chat.last_message = new_message
            print(
                f"{chat.structure=}, {previous_message_id=}, {new_message.pk=}, {new_message.history=}"
            )
            chat.structure = update_chat_structure(
                chat.structure,
                previous_message_id if previous_message_id else None,
                new_message.pk,
                new_message.history[:-1] if len(message_history) > 0 else [],
            )
            chat.save()
            new_message.media.save(filename, image_content, save=True)
            serialzier = MessageSerializer(new_message)
            return Response(
                {"messages": [serialzier.data]}, status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": "Failed to save image", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
