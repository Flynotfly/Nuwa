from fastapi import APIRouter

from src.views.user import user_router

router = APIRouter()
router.include_router(user_router)
