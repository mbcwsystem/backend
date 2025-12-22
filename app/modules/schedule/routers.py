from typing import List

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.auth.models import User
from app.modules.schedule import services
from app.modules.schedule.schemas import (
    ScheduleCreateRequest,
    ScheduleCreateResponse,
    ScheduleResponse,
)
from app.utils.permission_utils import is_admin

router = APIRouter()


def get_schedule_user(user: User = Depends(get_current_user)) -> User:
    if not is_admin(user):
        raise HTTPException(403, "바이저 이상만 스케줄 관리 가능합니다.")
    return user


# 스케줄 생성 API
@router.post(
    "/schedule/create",
    response_model=ScheduleCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="스케줄 생성",
)
def create_schedule(
    data: ScheduleCreateRequest,
    db: Session = Depends(get_db),
    user=Depends(get_schedule_user),
):
    return services.create_schedule(db, user, data)


# 특정 주차 스케줄 조회
@router.get(
    "/schedule/week/{year}/{weekNumber}",
    response_model=List[ScheduleResponse],
    summary="특정 주차 스케줄 조회",
)
def get_schedule_week(
    year: int,
    weekNumber: int,
    db: Session = Depends(get_db),
):
    return services.list_schedule(db, year, weekNumber)

# 스케줄 상세 조회
@router.get(
    "/schedule/{scheduleId}",
    response_model=ScheduleResponse,
    summary="스케줄 상세 조회"
)
def get_schedule(
        scheduleId: int,
        db: Session = Depends(get_db),
):
    return services.get_schedule(db, scheduleId)