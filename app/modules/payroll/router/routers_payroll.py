from typing import List, Union
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.utils.permission_utils import is_system
from app.modules.payroll.schemas import (
    PayrollResponse,
    PayrollPayResponse,
)
from app.modules.payroll.services.payroll_service import PayrollService

router = APIRouter(tags=["Payroll"])


@router.get(
    "/",
    response_model=Union[
        List[PayrollResponse],  # 관리자
        PayrollPayResponse,  # 일반 사용자
    ],
    summary="관리자: 전체조회 / 사용자: 개인조회",
)
def get_payrolls(
    year: int = Query(...),
    month: int | None = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if is_system(user):
        raise HTTPException(status_code=403, detail="조회할 수 없는 계정입니다.")

    return PayrollService.get_payrolls(
        db=db,
        user=user,
        year=year,
        month=month,
    )
