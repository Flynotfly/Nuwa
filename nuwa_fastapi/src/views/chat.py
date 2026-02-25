from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy import or_
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from src.auth import get_current_user
from src.database import User, Chat, Character
from src.db_connection import get_db
from src.models.chat import ChatCreate, ChatResponse, ChatRetrieveAll, ChatUpdate
from src.views.utils import raise_non_found_error


chat_router = APIRouter(prefix="/chats", tags=["chats"])


CurrentUser = Annotated[User, Depends(get_current_user)]
DB = Annotated[Session, Depends(get_db)]


@chat_router.get("", response_model=list[ChatRetrieveAll])
def retrieve_all_chats(
        user: CurrentUser,
        db: DB,
):
    return db.query(Chat).filter(
        Chat.owner_id == user.id,
        Chat.is_active.is_(True),
    ).all()


@chat_router.post("", status_code=201, response_model=ChatResponse)
def create_chat(
        payload: ChatCreate,
        user: CurrentUser,
        db: DB,
):
    data = payload.model_dump()
    character_id = data["character_id"]
    character_instance: Character | None = db.query(Character).filter(
        Character.id == character_id,
        Character.is_active.is_(True),
        or_(
            Character.owner_id == user.id,
            Character.is_private.is_(False),
        ),
    ).first()
    if character_instance is None:
        raise_non_found_error("Character", character_id)
    instance = Chat(
        owner_id=user.id,
        character_id=character_instance.id,
        character_name=character_instance.name,
        system_prompt=character_instance.system_prompt,
        description=character_instance.description,
        is_hidden_prompt=character_instance.is_hidden_prompt,
        is_active=True,
        last_message_datetime=datetime.now(tz=timezone.utc),
    )
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


@chat_router.get("/{instance_id}", response_model=ChatResponse)
def retrieve_chat(
        instance_id: int,
        user: CurrentUser,
        db: DB,
):
    instance: Chat | None = db.query(Chat).filter(
        Chat.id == instance_id,
        Chat.is_active.is_(True),
        Chat.owner_id == user.id,
    ).first()
    if instance is None:
        raise_non_found_error("Chat", instance_id)
    return instance


@chat_router.put("/{instance_id}", response_model=ChatResponse)
def update_chat(
        instance_id: int,
        payload: ChatUpdate,
        user: CurrentUser,
        db: DB,
):
    data = payload.model_dump()
    instance: Chat | None = db.query(Chat).filter(
        Chat.id == instance_id,
        Chat.is_active.is_(True),
        Chat.owner_id == user.id,
    ).first()
    if instance is None:
        raise_non_found_error("Chat", instance_id)
    instance.system_prompt = data["system_prompt"]
    db.commit()
    db.refresh(instance)
    return instance


@chat_router.patch("/{instance_id}", response_model=ChatResponse)
def partially_update_chat(
        instance_id: int,
        payload: ChatUpdate,
        user: CurrentUser,
        db: DB,
):
    return update_chat(
        instance_id=instance_id,
        payload=payload,
        user=user,
        db=db,
    )


@chat_router.delete("/{instance_id}", status_code=204)
def destroy_chat(
        instance_id: int,
        user: CurrentUser,
        db: DB,
):
    instance: Chat | None = db.query(Chat).filter(
        Chat.id == instance_id,
        Chat.is_active.is_(True),
        Chat.owner_id == user.id,
    ).first()
    if instance is None:
        raise_non_found_error("Chat", instance_id)
    instance.is_active = False
    db.commit()
    return None
