from fastapi import APIRouter

from src.views.user import user_router
from src.views.character import character_router
from src.views.chat import chat_router

router = APIRouter()
router.include_router(user_router)
router.include_router(character_router)
router.include_router(chat_router)
