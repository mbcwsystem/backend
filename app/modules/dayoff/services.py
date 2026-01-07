from fastapi import HTTPException
from app.modules.schedule.models import Schedule


def apply_day_off(db, user, data,):
    """
    휴무 신청
    """

    # 휴무 하루 단위인지 체크
    if data['start_date'] != data['end_date']:
        raise HTTPException(400, detail="휴무는 하루 단위로 신청할 수 있습니다.")

    # 신청 전에 내가 신청하는 날이 휴무인지 확인

    # 휴무가 공휴일 및 주말에 2회 있는지 확인

    # 스케줄 유무 확인
    schedule = db.query(Schedule).filter(
        Schedule.user_id == user.id,
        Schedule.start_date >= data['start_date'],
        Schedule.end_date <= data['end_date'],
    ).first()

    if schedule:
        raise HTTPException(409, detail="해당 기간에 이미 스케줄이 있어 휴무를 신청할 수 없습니다.")

    return None