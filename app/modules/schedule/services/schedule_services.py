from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.schedule.models.schedule_models import Schedule
from app.modules.schedule.schemas.schedule_schemas import (
    ScheduleCreateRequest,
    ScheduleResponse,
    ScheduleUpdateRequest,
)
from app.utils.permission_utils import is_admin


def _build_schedule_response(schedule: Schedule) -> ScheduleResponse:
    return ScheduleResponse(
        id=schedule.id,
        user_id=schedule.user_id,
        user_name=schedule.target.name,
        start_date=schedule.start_date,
        end_date=schedule.end_date,
        week_number=schedule.week_number,
        year=schedule.year,
        month=schedule.month,
    )


# 스케줄 생성
def create_schedule(db: Session, user: User, data: ScheduleCreateRequest) -> Schedule:
    """
    스케줄 생성
    - 바이저 이상 생성 불가능
    """

    # 권한 체크
    if not is_admin(user):
        raise HTTPException(403, "바이저급 이상만 관리 가능합니다.")

    schedule = Schedule(
        user_id=user.id,
        target_id=data.target_id,
        start_date=data.start_date,
        end_date=data.end_date,
        week_number=data.week_number,
        year=data.year,
        month=data.month,
    )

    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    return schedule


def list_schedule(db: Session, year: int, week_number: int) -> List[ScheduleResponse]:
    """
    스케줄 주차별 목록 조회
    """

    schedules = (
        db.query(Schedule)
        .filter(
            Schedule.year == year,
            Schedule.week_number == week_number,
        )
        .all()
    )

    return [_build_schedule_response(schedule) for schedule in schedules]


def get_schedule(db: Session, schedule_id: int) -> ScheduleResponse:
    """
    스케줄 상세 조회
    """

    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()

    if schedule is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 스케줄입니다.")

    return _build_schedule_response(schedule)


def update_schedule(
    db: Session, schedule_id: int, data: ScheduleUpdateRequest, user: User
) -> ScheduleResponse:
    """
    스케줄 수정
    """
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()

    # 스케줄 존재 여부
    if schedule is None:
        raise HTTPException(404, "존재하지 않는 스케줄입니다.")

    # 권한 체크
    if not is_admin(user):
        raise HTTPException(403, "바이저급 이상만 관리 가능합니다.")

    updated_schedule = data.model_dump(exclude_unset=True)

    allowed_fields = {
        "start_date",
        "end_date",
        "week_number",
        "year",
        "month",
    }

    for field, value in updated_schedule.items():
        if field in allowed_fields:
            setattr(schedule, field, value)

    db.commit()
    db.refresh(schedule)

    return _build_schedule_response(schedule)


def delete_schedule(db: Session, schedule_id: int, user: User):
    """
    스케줄 삭제
    """

    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()

    # 스케줄 존재 여부
    if schedule is None:
        raise HTTPException(404, "존재하지 않는 스케줄입니다.")

    # 권한 체크
    if not is_admin(user):
        raise HTTPException(403, "스케줄 삭제 권한이 없습니다.")

    db.delete(schedule)
    db.commit()

    return {"message": "스케줄이 삭제되었습니다."}
