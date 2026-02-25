from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session, joinedload

from src.database import User, Character
from src.auth import get_current_user, get_current_user_optional
from src.db_connection import get_db
from src.models.character import CharacterRetrieve, CharacterCreate, CharacterRetrieveAll


character_router = APIRouter(prefix="/characters")


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserOptional = Annotated[User, Depends(get_current_user_optional)]
DB = Annotated[Session, Depends(get_db)]


@character_router.get("", response_model=CharacterRetrieveAll)
def retrieve_all_characters(
        user: CurrentUserOptional,
        db: DB,
        only_user: bool | None = None,
):
    if only_user:
        if user is None:
            raise HTTPException(status_code=400, detail="Only authenticated users allowed to retrieve owned characters")
        return db.query(Character).filter(
            Character.owner_id == user.id,
            Character.is_active == True,
        ).all()
    return db.query(Character).filter(
        Character.is_private == False,
        Character.is_active == True,
    ).all()


@character_router.get("/{instance_id}", response_model=CharacterRetrieve)
def retrieve_character(
        instance_id: int,
        user: CurrentUser,
        db: DB,
):
    db_instance = db.query(Character).options(joinedload(Character.owner)).filter(
        Character.id == instance_id,
        Character.is_active == True,
        or_(
            Character.is_private == False,
            Character.owner_id == user.id,
        ),
    ).first()
    if db_instance is None:
        raise HTTPException(
            status_code=404,
            detail=f"Character with id {instance_id} is not found",
        )
    return db_instance
