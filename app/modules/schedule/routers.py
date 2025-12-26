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
    ScheduleUpdateRequest,
)
from app.utils.permission_utils import is_admin

router = APIRouter()


def get_schedule_user(user: User = Depends(get_current_user)) -> User:
    if not is_admin(user):
        raise HTTPException(403, "바이저 이상만 스케줄 관리 가능합니다.")
    return user


# 스케줄 생성 API
@router.post(
    "/create",
    response_model=ScheduleCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="스케줄 생성",
)
def create_schedule(
    data: ScheduleCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_schedule_user),
):
    return services.create_schedule(db, user, data)


# 특정 주차 스케줄 조회 API
@router.get(
    "/week/{year}/{week_number}",
    response_model=List[ScheduleResponse],
    summary="특정 주차 스케줄 조회",
)
def get_schedule_week(
    year: int,
    week_number: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_schedule_user),
):
    return services.list_schedule(db, user, year, week_number)


# 스케줄 상세 조회 API
@router.get(
    "/{schedule_id}",
    response_model=ScheduleResponse,
    summary="스케줄 상세 조회",
)
def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_schedule_user),
):
    return services.get_schedule(db, user, schedule_id)


# 스케줄 수정 API
@router.patch("/{schedule_id}", response_model=ScheduleResponse, summary="스케줄 수정")
def update_schedule(
    data: ScheduleUpdateRequest,
    schedule_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_schedule_user),
):
    return services.update_schedule(db, schedule_id, data, user)


# 스케줄 삭제 API
@router.delete("/{schedule_id}", response_model=ScheduleResponse, summary="스케줄 삭제")
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_schedule_user),
):
    return services.delete_schedule(db, schedule_id, user)
