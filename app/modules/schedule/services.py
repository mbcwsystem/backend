from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.schedule.models import Schedule
from app.modules.schedule.schemas import ScheduleCreateRequest, ScheduleResponse
from app.utils.permission_utils import is_admin


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
        start_date=data.start_date,
        end_date=data.end_date,
        week_number=data.week_number,
        year=data.year,
        month=data.month,
        is_holiday=False,  # 기본값 처리
    )

    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    return schedule


def list_schedule(db, year: int, weekNumber: int) -> List[ScheduleResponse]:
    """
    스케줄 주차별 목록 조회
    """
    schedules = (
        db.query(Schedule, User.name.label("user_name"))
        .join(User, User.id == Schedule.user_id)
        .filter(
            Schedule.year == year,
            Schedule.week_number == weekNumber,
        )
        .all()
    )

    return [
        ScheduleResponse(
            id=schedule.id,
            user_id=schedule.user_id,
            user_name=user_name,
            start_date=schedule.start_date,
            end_date=schedule.end_date,
            week_number=schedule.week_number,
            year=schedule.year,
            month=schedule.month,
            is_holiday=schedule.is_holiday,
        )
        for schedule, user_name in schedules
    ]
