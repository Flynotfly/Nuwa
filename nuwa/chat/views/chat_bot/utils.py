from dataclasses import dataclass

from django.utils import timezone

from chat.models import MEDIA_TYPE_CHOICES_WITH_TEXT, Chat, Message
from chat.serializers.message import MessageSerializer
from chat.utils import update_chat_structure


def get_last_n_messages(
    previous_message: Message,
    chat: Chat,
    user,
    n: int = 30,
):
    message_history_ids = previous_message.history
    all_message_ids = list(message_history_ids) + [previous_message.pk]
    history = Message.objects.filter(
        owner=user, pk__in=all_message_ids, chat=chat
    ).order_by("-conducted")[:n]
    history = reversed(list(history))
    return history


def append_text_messages_from_history(
    messages: list[dict],
    previous_message: Message,
    chat: Chat,
    user,
    qnt_of_appended_messages: int = 30,
):
    history = get_last_n_messages(
        previous_message=previous_message,
        chat=chat,
        user=user,
        n=qnt_of_appended_messages,
    )
    for message in history:
        if message.media_type != "text":
            continue
        messages.append({"role": message.role, "content": message.message})


@dataclass
class MessageData:
    role: str
    media_type: str
    message: str | None = None
    conducted: timezone.timezone | None = None
    info: dict | None = None
    filename: str | None = None
    media_content: any = None


def save_messages(
    chat: Chat,
    user,
    previous_message: Message | None,
    messages: list,
):
    if previous_message:
        prev_message_history = previous_message.history
        history = list(prev_message_history) + [previous_message.pk]
    else:
        history = []
    result = []
    structure = chat.structure
    last_message_with_text = None
    for message_data in messages:
        role = message_data.role
        media_type = message_data.media_type
        message_content = message_data.message
        conducted = message_data.conducted
        info = message_data.info

        message = Message.objects.create(
            owner=user,
            chat=chat,
            role=role,
            media_type=media_type,
            message=message_content,
            conducted=conducted if conducted is not None else timezone.now(),
            history=history,
            info=info,
        )

        filename = message_data.filename
        media_content = message_data.media_content
        if filename is not None and media_content is not None:
            message.media.save(filename, media_content, save=True)
        serializer = MessageSerializer(message)
        result.append(serializer.data)
        structure = update_chat_structure(
            structure,
            previous_message.pk if previous_message else None,
            message.pk,
            previous_message.history if previous_message else [],
        )
        if message.media_type in MEDIA_TYPE_CHOICES_WITH_TEXT.keys():
            last_message_with_text = message
        previous_message = message
        history = list(history) + [message.pk]
    chat.structure = structure
    chat.last_message = previous_message
    chat.last_message_datetime = previous_message.conducted
    if last_message_with_text:
        chat.last_message_text = last_message_with_text.message
    chat.save()
    return result
