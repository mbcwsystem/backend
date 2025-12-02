from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy import select

from app.core.database import get_db
from app.modules.workstatus import models, schemas
from app.modules.auth.models import User
from app.modules.auth.services import verify_password
from app.modules.payroll.services import update_realtime_payroll

router = APIRouter(tags=["Attendance"])


class AttendanceAuthInput(BaseModel):
    username: str
    password: str

def authenticate_attendance_user(db: Session, username: str, password: str) -> User:
    user = db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="휴면/비활성화된 계정입니다.")

    return user


@router.post("/check-in", response_model=schemas.AttendanceResponse)
def check_in(payload: AttendanceAuthInput, db: Session = Depends(get_db)):
    user = authenticate_attendance_user(db, payload.username, payload.password)

    today = datetime.now().date()
    existing = db.query(models.Attendance).filter_by(user_id=user.id, work_date=today).first()

    if existing:
        raise HTTPException(status_code=400, detail="이미 오늘 출근 기록이 있습니다.")

    record = models.Attendance(
        user_id=user.id,
        work_date=today,
        check_in=datetime.now().time(),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    record.user_name = user.name
    return record

@router.post("/break-start", response_model=schemas.AttendanceResponse)
def break_start(payload: AttendanceAuthInput, db: Session = Depends(get_db)):
    user = authenticate_attendance_user(db, payload.username, payload.password)

    today = datetime.now().date()
    record = _get_today_record(db, user.id, today)

    if not record.check_in:
        raise HTTPException(status_code=400, detail="출근 먼저 해주세요.")
    if record.check_out:
        raise HTTPException(status_code=400, detail="이미 퇴근한 기록이 있습니다.")
    if record.break_start and not record.break_end:
        raise HTTPException(status_code=400, detail="이미 휴식 중입니다.")

    record.break_start = datetime.now().time()
    db.commit()
    db.refresh(record)

    update_realtime_payroll(user.id, db)
    record.user_name = user.name
    return record

@router.post("/break-end", response_model=schemas.AttendanceResponse)
def break_end(
    payload: AttendanceAuthInput,
    db: Session = Depends(get_db),
):
    user = authenticate_attendance_user(db, payload.username, payload.password)
    today = datetime.now().date()
    record = _get_today_record(db, user.id, today)

    if not record.break_start:
        raise HTTPException(status_code=400, detail="휴식 시작 기록이 없습니다.")

    if record.break_end:
        raise HTTPException(status_code=400, detail="이미 복귀한 기록이 있습니다.")

    record.break_end = datetime.now().time()
    db.commit()
    db.refresh(record)

    update_realtime_payroll(user.id, db)

    record.user_name = user.name
    return record

@router.post("/check-out", response_model=schemas.AttendanceResponse)
def check_out(payload: AttendanceAuthInput, db: Session = Depends(get_db)):
    user = authenticate_attendance_user(db, payload.username, payload.password)

    today = datetime.now().date()
    record = _get_today_record(db, user.id, today)

    if not record.check_in:
        raise HTTPException(status_code=400, detail="출근 기록이 없습니다.")
    if record.break_start and not record.break_end:
        raise HTTPException(status_code=400, detail="휴식 중에는 퇴근할 수 없습니다.")
    if record.check_out:
        raise HTTPException(status_code=400, detail="이미 퇴근 기록이 있습니다.")

    record.check_out = datetime.now().time()

    work_minutes, break_minutes = _calc_work_minutes(record)
    record.total_work_minutes = work_minutes
    record.total_break_minutes = break_minutes

    db.commit()
    db.refresh(record)

    update_realtime_payroll(user.id, db)
    record.user_name = user.name
    return record

def _get_today_record(db: Session, user_id: int, today):
    record = db.query(models.Attendance).filter_by(user_id=user_id, work_date=today).first()
    if not record:
        raise HTTPException(status_code=400, detail="출근 기록이 없습니다.")
    return record


def _calc_work_minutes(record: models.Attendance):
    work_date = record.work_date

    check_in = datetime.combine(work_date, record.check_in)
    check_out = datetime.combine(work_date, record.check_out)

    if check_out < check_in:
        check_out += timedelta(days=1)

    total_work = (check_out - check_in).total_seconds() / 60

    break_minutes = 0
    if record.break_start and record.break_end:
        b_start = datetime.combine(work_date, record.break_start)
        b_end = datetime.combine(work_date, record.break_end)

        if b_end < b_start:
            b_end += timedelta(days=1)

        break_minutes = (b_end - b_start).total_seconds() / 60

    return int(total_work - break_minutes), int(break_minutes)