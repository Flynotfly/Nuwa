from sqlalchemy.orm import Session

from src.auth import hash_password, verify_password
from src.database import User
from src.models.user import SignInModel, SignUpModel


def register_user(
    user: SignUpModel,
    db: Session,
) -> User:
    existing = db.query(User).filter(User.username == user.username).first()
    if existing is not None:
        raise ValueError("Username already taken")
    new_user = User(
        username=user.username, hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_with_password(
    user: SignInModel,
    db: Session,
) -> User:
    user_obj: User | None = (
        db.query(User).filter(User.username == user.username).first()
    )
    if user_obj is None:
        raise ValueError(f"No user with username {user.username}")
    if not verify_password(user.password, user_obj.hashed_password):
        raise ValueError(f"Invalid password")
    return user_obj
