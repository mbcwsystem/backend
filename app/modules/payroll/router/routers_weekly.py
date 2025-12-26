from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.payroll.schemas import WeeklyAllowanceResponse
from app.modules.payroll.services.weekly_service import (
    get_weekly_allowance_by_month,
)

router = APIRouter(
    prefix="/weekly-allowance",
)


@router.get("/", response_model=list[WeeklyAllowanceResponse], summary="주휴수당조회")
def get_weekly_allowance(
    user_id: int = Query(...),
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
):
    return get_weekly_allowance_by_month(
        db=db,
        user_id=user_id,
        year=year,
        month=month,
    )
