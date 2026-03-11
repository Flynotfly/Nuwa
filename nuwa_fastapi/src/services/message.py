import asyncio
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime

import aiofiles
from fastapi import Depends, UploadFile
from sqlalchemy.orm import Session

from src.auth import get_current_user
from src.config import settings
from src.database import Message, User
from src.db_connection import get_db
from src.models.message import MessageCreate


@dataclass
class MessageCreate:
    chat_id: int
    role: str
    media_type: str
    conducted: datetime
    history: list[int]
    message: str | None = None
    info: dict | None = None


async def add_message(
    message_model: MessageCreate,
    file: UploadFile | None = None,
    commit: bool = True,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Message:
    message_data = asdict(message_model)
    message_data["owner_id"] = user.id
    if file and file.filename:
        message_data["media"] = await save_media(
            file=file, user_id=user.id, chat_id=message_model.chat_id
        )
    instance = Message(**message_data)
    db.add(instance)
    if commit:
        db.commit()
        db.refresh(instance)
    else:
        db.flush()
    return instance


async def save_media(
    file: UploadFile,
    user_id: int,
    chat_id: int,
):
    full_filename = (
        f"{settings.media_path}/{user_id}/{chat_id}/{uuid.uuid4()}-{file.filename}"
    )
    make_dir_filepath = settings.base_dir / f"{settings.media_path}/{user_id}/{chat_id}"
    make_dir_filepath.mkdir(parents=True, exist_ok=True)
    save_filename = settings.base_dir / full_filename
    async with aiofiles.open(save_filename, "wb") as out:
        while chunk := await file.read(1024 * 64):  # 64KB chunks
            await out.write(chunk)
    return full_filename
