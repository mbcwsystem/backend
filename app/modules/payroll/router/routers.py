from fastapi import APIRouter

from app.modules.payroll.router.routers_payroll import router as payroll_router

router = APIRouter()
router.include_router(payroll_router)
