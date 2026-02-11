from dataclasses import dataclass

from django.utils import timezone

from chat.models import Chat, Message
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
    ).order_by("-conducted")[:30]
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
    return messages


def update_chat_info_with_single_message(
    chat: Chat,
    message: Message,
    message_with_text: bool,
    previous_message: Message | None,
):
    chat.structure = update_chat_structure(
        chat.structure,
        previous_message.pk if previous_message else None,
        message.pk,
        message.history[:-1] if len(message.history) > 0 else [],
    )
    chat.last_message = message
    chat.last_message_datetime = message.conducted
    if message_with_text:
        chat.last_message_text = message.message
    chat.save()


def update_chat_info_with_two_messages(
    chat: Chat,
    message_1: Message,
    message_2: Message,
    message_with_text: Message | None,
    previous_message: Message | None,
):
    structure = update_chat_structure(
        chat.structure,
        previous_message.pk if previous_message else None,
        message_1.pk,
        message_1.history[:-1] if len(message_1.history) > 0 else [],
    )
    chat.structure = update_chat_structure(
        structure,
        message_1.pk,
        message_2.pk,
        message_1.history,
    )
    chat.last_message = message_2
    chat.last_message_datetime = message_2.conducted
    if message_with_text:
        chat.last_message_text = message_with_text.message
    chat.save()


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
    history: list,
    messages: list,
):
    result = []
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
        media_content = message_content.message_content
        if filename is not None and media_content is not None:
            message.media.save(filename, media_content, save=True)
        result.append(message)

        history = list(history) + [message.pk]
    return result
