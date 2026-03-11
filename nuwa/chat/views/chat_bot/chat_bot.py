from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Chat, Message
from chat.views.chat_bot.detect import detect_answer_type
from chat.views.chat_bot.image_answer import generate_image_answer
from chat.views.chat_bot.text_answer import generate_text_answer
from chat.views.chat_bot.detect import ALLOWED_ANSWER_TYPES


class ChatBotView(APIView):
    def post(self, request):
        received_at = timezone.now()

        user_input = request.data.get("message", None)
        chat_id = request.data.get("chat_id")
        previous_message_id = request.data.get("previous_message_id", None)
        is_user_message = request.data.get("is_user_message", False)
        stream = request.data.get("stream", False)
        answer_type = request.data.get("answer_type", "detect")

        if user_input is not None:
            user_input = user_input.strip()
        if not chat_id:
            return Response(
                {"error": "chat_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if answer_type not in ALLOWED_ANSWER_TYPES and answer_type != "detect":
            return Response(
                {
                    "error": f"Wrong 'answer_type'. Allowed answer types: {ALLOWED_ANSWER_TYPES} and 'detect'."
                },
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

        if stream == "false":
            stream = False
        elif stream == "true":
            stream = True
        elif stream == "True" or stream == "False":
            stream = bool(stream)
        if stream is not False and stream is not True:
            return Response(
                {"error": "Wrong 'stream'. Allowed only boolean type."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if is_user_message and not user_input:
            return Response(
                {
                    "error": "As 'is_user_message' is true, 'message' should be provided."
                },
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
            if user_input:
                answer_type = detect_answer_type(user_input)
            else:
                answer_type = "text"

        match answer_type:
            case "text":
                return generate_text_answer(
                    chat=chat,
                    previous_message=previous_message if previous_message_id else None,
                    is_user_message=is_user_message,
                    user_input=user_input,
                    user=self.request.user,
                    received_at=received_at,
                    is_stream=stream,
                )
            case "image":
                return generate_image_answer(
                    chat=chat,
                    previous_message=previous_message if previous_message_id else None,
                    is_user_message=is_user_message,
                    user_input=user_input,
                    user=self.request.user,
                    received_at=received_at,
                )
            case "video":
                ...
