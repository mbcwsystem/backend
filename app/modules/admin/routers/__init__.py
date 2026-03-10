from fastapi import APIRouter

from .admin import router as admin_router
from .users import router as users_router

router = APIRouter()
__all__ = ["users_router", "admin_router"]
