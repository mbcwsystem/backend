from fastapi import APIRouter

from app.modules.payroll.router.routers_payroll import router as payroll_router
from app.modules.payroll.router.routers_weekly import router as weekly_router

router = APIRouter()
router.include_router(payroll_router)
router.include_router(weekly_router)
