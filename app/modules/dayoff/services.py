from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import Tuple

from app.modules.admin.models import Holiday
from app.modules.dayoff.models import DayOffRequest, Status
from app.modules.schedule.models import Schedule
from app.utils.date_utils import get_month_range


def apply_day_off(db, user, data) -> DayOffRequest:
    """
    휴무 신청
    """

    # 휴무 하루 단위인지 체크
    if data["start_date"] != data["end_date"]:
        raise HTTPException(400, detail="휴무는 하루 단위로 신청할 수 있습니다.")

    # 신청 전에 내가 신청하는 날이 휴무인지 확인
    holiday = (
        db.query(Holiday)
        .filter(
            Holiday.date == data["start_date"],
        )
        .first()
    )

    if holiday:
        data["is_holiday"] = True

    # 휴무가 공휴일 및 주말에 2회 있는지 확인
    month_start, month_end = get_month_range(data["start_date"])

    count = (
        db.query(DayOffRequest)
        .filter(
            DayOffRequest.user_id == user.id,
            DayOffRequest.start_date >= month_start,
            DayOffRequest.start_date <= month_end,
            DayOffRequest.status.in_([Status.approved]),
            DayOffRequest.is_holiday == True,
        )
        .count()
    )

    if count >= 2:
        raise HTTPException(
            409, detail="해당 달에 공휴일/주말 휴무는 최대 2회까지 신청할 수 있습니다."
        )

    # 스케줄 유무 확인
    schedule = (
        db.query(Schedule)
        .filter(
            Schedule.user_id == user.id,
            Schedule.end_date >= data["start_date"],
            Schedule.start_date <= data["end_date"],
        )
        .first()
    )

    if schedule:
        raise HTTPException(
            409, detail="해당 기간에 이미 스케줄이 있어 휴무를 신청할 수 없습니다."
        )

    dayOff = DayOffRequest(
        user_id=user.id,
        start_date=data["start_date"],
        end_date=data["end_date"],
        reason=data["reason"],
        status=Status.pending,
        is_holiday=data["is_holiday"],
    )

    db.add(dayOff)
    db.commit()
    db.refresh(dayOff)

    return dayOff
