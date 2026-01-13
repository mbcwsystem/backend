from .users import router as users_router
from .admin import router as admin_router
from fastapi import APIRouter

router = APIRouter()
__all__ = ["users_router", "admin_router"]
