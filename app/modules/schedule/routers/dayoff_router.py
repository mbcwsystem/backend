from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.auth.models import User
from app.modules.schedule.schemas.dayoff_schemas import (
    DayOffApplyRequest,
    DayOffApplyResponse,
    DayOffDecisionRequest,
)
from app.modules.schedule.services import dayoff_services
from app.utils.permission_utils import is_system


def block_system_user(user: User = Depends(get_current_user)) -> User:
    if is_system(user):
        from fastapi import HTTPException

        raise HTTPException(403, "시스템 계정은 접근할 수 없습니다.")
    return user


router = APIRouter(dependencies=[Depends(block_system_user)])


# 휴무 신청 API
@router.post(
    "/apply",
    response_model=DayOffApplyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="휴무 신청",
)
def apply_day_off(
    data: DayOffApplyRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return dayoff_services.apply_day_off(db, user, data)


# 휴무 승인 및 거절 API
@router.patch(
    "/{day_off_id}", status_code=status.HTTP_200_OK, summary="휴무 승인 및 거절"
)
def decision_day_off(
    day_off_id: int,
    data: DayOffDecisionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return dayoff_services.decision_day_off(data, db, day_off_id, user)
