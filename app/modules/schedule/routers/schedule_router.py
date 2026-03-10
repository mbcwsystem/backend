from typing import List

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.auth.models import User
from app.modules.schedule.routers.dayoff_router import router as dayoff_router
from app.modules.schedule.routers.shift_router import router as shift_router
from app.modules.schedule.schemas.schedule_schemas import (
    ScheduleCreateRequest,
    ScheduleCreateResponse,
    ScheduleResponse,
    ScheduleUpdateRequest,
)
from app.modules.schedule.services import schedule_services
from app.utils.permission_utils import is_system


def block_system_user(user: User = Depends(get_current_user)) -> User:
    if is_system(user):
        raise HTTPException(403, "시스템 계정은 접근할 수 없습니다.")
    return user


router = APIRouter(dependencies=[Depends(block_system_user)])
router.include_router(
    shift_router,
    prefix="/shift",
    tags=["스케줄관리"],
)

router.include_router(
    dayoff_router,
    prefix="/dayoff",
    tags=["스케줄관리"],
)


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
    user: User = Depends(get_current_user),
):
    return schedule_services.create_schedule(db, user, data)


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
):
    return schedule_services.list_schedule(db, year, week_number)


# 스케줄 상세 조회 API
@router.get(
    "/{schedule_id}",
    response_model=ScheduleResponse,
    summary="스케줄 상세 조회",
)
def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
):
    return schedule_services.get_schedule(db, schedule_id)


# 스케줄 수정 API
@router.patch("/{schedule_id}", response_model=ScheduleResponse, summary="스케줄 수정")
def update_schedule(
    data: ScheduleUpdateRequest,
    schedule_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return schedule_services.update_schedule(db, schedule_id, data, user)


# 스케줄 삭제 API
@router.delete("/{schedule_id}", summary="스케줄 삭제")
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return schedule_services.delete_schedule(db, schedule_id, user)
