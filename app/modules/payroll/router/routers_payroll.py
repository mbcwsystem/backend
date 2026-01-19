from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin, get_current_user
from app.modules.payroll.models import PayrollPayDate
from app.modules.payroll.schemas import (
    PayrollPayDateCreate,
    PayrollPayDateResponse,
    PayrollPayDateUpdate,
    PayrollPayResponse,
    PayrollResponse,
)
from app.modules.payroll.services.payroll_service import PayrollService
from app.utils.permission_utils import is_system

router = APIRouter()


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


@router.post(
    "/pay-dates",
    response_model=PayrollPayDateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="급여 지급일 등록",
)
def create_payroll_pay_date(
    payload: PayrollPayDateCreate = ...,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    pay_date = PayrollPayDate(
        year=payload.year,
        month=payload.month,
        pay_date=payload.pay_date,
    )

    try:
        db.add(pay_date)
        db.commit()
        db.refresh(pay_date)
        return pay_date
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="해당 연월의 급여 지급일이 이미 존재합니다",
        )


@router.patch(
    "/pay-dates/{year}/{month}",
    response_model=PayrollPayDateResponse,
    summary="급여 지급일 수정",
)
def update_payroll_pay_date(
    year: int = Path(...),
    month: int = Path(...),
    payload: PayrollPayDateUpdate = ...,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    pay_date = (
        db.query(PayrollPayDate)
        .filter(
            PayrollPayDate.year == year,
            PayrollPayDate.month == month,
        )
        .first()
    )

    if not pay_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="급여 지급일이 존재하지 않습니다",
        )

    pay_date.pay_date = payload.pay_date
    db.commit()
    db.refresh(pay_date)
    return pay_date


@router.delete(
    "/pay-dates/{year}/{month}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="급여 지급일 삭제",
)
def delete_payroll_pay_date(
    year: int = Path(...),
    month: int = Path(...),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    pay_date = (
        db.query(PayrollPayDate)
        .filter(
            PayrollPayDate.year == year,
            PayrollPayDate.month == month,
        )
        .first()
    )

    if not pay_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="급여 지급일이 존재하지 않습니다",
        )

    db.delete(pay_date)
    db.commit()
