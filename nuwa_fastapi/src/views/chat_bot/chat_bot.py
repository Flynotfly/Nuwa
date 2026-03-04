from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.auth import get_current_user
from src.database import Chat, Message, User
from src.db_connection import get_db
from src.models.chat_bot import ChatPayload
from src.views.chat_bot.detect import ALLOWED_ANSWER_TYPES, detect_answer_type

chat_bot_router = APIRouter(prefix="/chat", tags=["chat_bot"])


CurrentUser = Annotated[User, Depends(get_current_user)]
DB = Annotated[Session, Depends(get_db)]


@chat_bot_router.post("")
def chat_bot(
    payload: ChatPayload,
    user: CurrentUser,
    db: DB,
):
    user_input = payload.user_input
    chat_id = payload.chat_id
    previous_message_id = payload.previous_message_id
    is_user_message = payload.is_user_message
    stream = payload.stream
    answer_type = payload.answer_type

    if user_input is not None:
        user_input = user_input.strip()
    if answer_type not in ALLOWED_ANSWER_TYPES and answer_type != "detect":
        raise HTTPException(
            status_code=400,
            detail=f"Wrong 'answer_type'. Allowed answer types: {ALLOWED_ANSWER_TYPES} and 'detect'.",
        )
    if is_user_message and not user_input:
        raise HTTPException(
            status_code=400,
            detail="As 'is_user_message' is true, 'message' should be provided.",
        )

    chat: Chat | None = (
        db.query(Chat)
        .filter(
            Chat.id == chat_id,
            Chat.owner_id == user.id,
        )
        .first()
    )
    if chat is None:
        raise HTTPException(
            status_code=400,
            detail="Chat id is invalid",
        )

    previous_message = None
    if previous_message_id:
        previous_message: Message | None = (
            db.query(Message)
            .filter(
                Message.id == previous_message_id,
                Message.owner_id == user.id,
                Message.chat_id == chat.id,
            )
            .first()
        )
        if previous_message is None:
            raise HTTPException(
                status_code=400,
                detail="Previous_message_id is invalid",
            )

    if answer_type == "detect":
        if user_input:
            answer_type = detect_answer_type(user_input)
        else:
            answer_type = "text"

    match answer_type:
        case "text":
            ...
        case "image":
            ...
        case "video":
            raise HTTPException(
                status_code=501,
                detail="Video generation not implemented yet",
            )
