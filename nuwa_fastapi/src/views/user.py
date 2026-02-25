from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.auth import create_token_pair, get_current_user, refresh_access_token
from src.database import User
from src.db_connection import get_db
from src.models.users import (RefreshTokenRequest, SignInModel, SignUpModel,
                              UserResponseModel)
from src.services.users import authenticate_with_password, register_user

user_router = APIRouter(prefix="/user")


@user_router.post("/sign-up", response_model=UserResponseModel, status_code=201)
def sing_up(user: SignUpModel, db: Session = Depends(get_db)):
    try:
        user = register_user(user=user, db=db)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return user


@user_router.post("/sign-in")
def sign_in(user: SignInModel, db: Session = Depends(get_db)):
    try:
        user_obj = authenticate_with_password(user=user, db=db)
    except ValueError as e:
        raise HTTPException(
            status_code=401, detail="Username or password are not valid"
        )
    return create_token_pair(username=user_obj.username)


@user_router.post("/refresh")
def refresh(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    return refresh_access_token(body.refresh_token, db)


@user_router.get("/session", response_model=UserResponseModel)
def get_session(current_user: User = Depends(get_current_user)):
    return current_user
