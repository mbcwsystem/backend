from datetime import datetime, time

from fastapi import HTTPException

from app.modules.admin.models import Holiday
from app.modules.dayoff.models import DayOffRequest, Status
from app.modules.schedule.models import Schedule
from app.utils.date_utils import get_month_range
from app.utils.permission_utils import is_admin


def apply_day_off(db, user, data) -> DayOffRequest:
    """
    휴무 신청
    """

    req_start_date = data.start_date.date()
    req_end_date = data.end_date.date()

    # 휴무 하루 단위인지 체크
    if req_start_date != req_end_date:
        raise HTTPException(400, detail="휴무는 하루 단위로 신청할 수 있습니다.")

    # 신청 전에 내가 신청하는 날이 휴무인지 확인
    holiday = db.query(Holiday).filter(Holiday.date == req_start_date).first()

    # 기본값: 프론트에서 보낸 값
    is_holiday = data.is_holiday

    # 서버 기준으로 공휴일 / 주말이면 강제로 holiday 처리
    if holiday or req_start_date.weekday() in (5, 6):
        is_holiday = True

        # 휴무가 공휴일 및 주말에 2회 있는지 확인
        month_start, month_end = get_month_range(req_start_date)

        count = (
            db.query(DayOffRequest)
            .filter(
                DayOffRequest.user_id == user.id,
                DayOffRequest.start_date >= month_start,
                DayOffRequest.start_date <= month_end,
                DayOffRequest.status.in_([Status.pending, Status.approved]),
                DayOffRequest.is_holiday.is_(True),
            )
            .count()
        )

        if count >= 2:
            raise HTTPException(
                409,
                detail="해당 달에 공휴일/주말 휴무는 최대 2회까지 신청할 수 있습니다.",
            )

    # 스케줄 겹침 체크도 하루 범위로 잡는 게 안전
    day_start = datetime.combine(req_start_date, time.min)
    day_end = datetime.combine(req_start_date, time.max)

    # 스케줄 유무 확인
    schedule = (
        db.query(Schedule)
        .filter(
            Schedule.user_id == user.id,
            Schedule.start_date <= day_end,
            Schedule.end_date >= day_start,
        )
        .first()
    )

    if schedule:
        raise HTTPException(
            409, detail="해당 기간에 이미 스케줄이 있어 휴무를 신청할 수 없습니다."
        )

    day_off = DayOffRequest(
        user_id=user.id,
        start_date=data.start_date,
        end_date=data.end_date,
        reason=data.reason,
        status=Status.pending,
        is_holiday=is_holiday,
    )

    db.add(day_off)
    db.commit()
    db.refresh(day_off)

    return day_off


def approve_day_off(db, day_off_id, user):
    """
    휴무 승인
    """

    # 권한 체크
    if not is_admin(user):
        raise HTTPException(403, "휴무 승인 권한이 없습니다.")


    day_off = db.query(DayOffRequest).filter(DayOffRequest.id == day_off_id).first()

    if day_off is None:
        raise HTTPException(404,
                            detail="존재하지 않는 휴무 신청입니다.")

    # 이미 처리된 휴무
    if day_off.status in (Status.approved, Status.rejected):
        raise HTTPException(
            status_code=409,
            detail="이미 처리된 휴무입니다."
        )

    day_off.status = Status.approved

    db.commit()
    db.refresh(day_off)


    return day_off