from dataclasses import dataclass
from sqlalchemy.orm import Session
from fastapi import Depends, UploadFile
from datetime import datetime, timezone

from src.utils import update_chat_structure
from src.db_connection import get_db
from src.auth import get_current_user
from src.database import Message, User, Chat
from src.services.message import add_message, MessageCreate
from src.models.message import MessageResponse


def get_last_n_messages(
        previous_message: Message,
        chat: Chat,
        n: int,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    message_history_ids = previous_message.history
    all_message_ids = list(message_history_ids) + [previous_message.id]
    history = db.query(Message).filter(
        Message.owner_id == user.id,
        Message.id.in_(all_message_ids),
        Message.chat_id == chat.id,
    ).order_by(Message.conducted.desc()).limit(n).all()
    history = reversed(history)
    return history


def append_text_messages_from_history(
        messages: list[dict],
        previous_message: Message,
        chat: Chat,
        qnt_of_appended_messages: int = 60,
):
    history = get_last_n_messages(
        previous_message=previous_message,
        chat=chat,
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
    conducted: datetime | None = None
    info: dict | None = None
    file: UploadFile | None = None


MEDIA_TYPE_CHOICES_WITH_TEXT = {"text"}


async def save_messages(
        chat: Chat,
        previous_message: Message | None,
        messages: list,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    if previous_message:
        prev_message_history = previous_message.history
        history = list(prev_message_history) + [previous_message.id]
    else:
        history = []
    result = []
    structure = chat.structure
    last_message_with_text = None
    for message_data in messages:
        message_create = MessageCreate(
            chat_id=chat.id,
            role=message_data.role,
            media_type=message_data.media_type,
            message=message_data.message,
            conducted=message_data.conducted if message_data.conducted is not None else datetime.now(timezone.utc),
            history=history,
            info=message_data.info,
        )
        message = await add_message(
            message_model=message_create,
            file=message_data.file,
            commit=False,
        )
        message_model = MessageResponse.model_validate(message)
        result.append(message_model)
        structure = update_chat_structure(
            structure,
            previous_message.id if previous_message else None,
            message.id,
            previous_message.history if previous_message else [],
        )
        if message.media_type in MEDIA_TYPE_CHOICES_WITH_TEXT:
            last_message_with_text = message
        previous_message = message
        history = list(history) + [message.id]
    chat.structure = structure
    chat.last_message_id = previous_message.id
    chat.last_message_datetime = previous_message.conducted
    if last_message_with_text:
        chat.last_message_text = last_message_with_text.message
    db.commit()
    return result
