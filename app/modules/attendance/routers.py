from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.attendance import models, schemas
from app.modules.auth.models import User
from app.modules.payroll.services import update_realtime_payroll

router = APIRouter(tags=["Attendance"])


@router.post("/check-in", response_model=schemas.AttendanceResponse)
def check_in(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    today = datetime.now().date()
    existing = (
        db.query(models.Attendance)
        .filter_by(user_id=current_user.id, work_date=today)
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="이미 오늘 출근 기록이 있습니다.")

    record = models.Attendance(
        user_id=current_user.id,
        work_date=today,
        check_in=datetime.now().time(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/break-start", response_model=schemas.AttendanceResponse)
def break_start(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    today = datetime.now().date()
    record = _get_today_record(db, current_user.id, today)

    if not record.check_in:
        raise HTTPException(status_code=400, detail="출근 먼저 해주세요.")
    if record.check_out:
        raise HTTPException(status_code=400, detail="이미 퇴근한 기록이 있습니다.")
    if record.break_start and not record.break_end:
        raise HTTPException(status_code=400, detail="이미 휴식 중입니다.")

    record.break_start = datetime.now().time()
    db.commit()
    db.refresh(record)
    update_realtime_payroll(current_user.id, db)
    return record


@router.post("/break-end", response_model=schemas.AttendanceResponse)
def break_end(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    today = datetime.now().date()
    record = _get_today_record(db, current_user.id, today)

    if not record.break_start:
        record.break_start = (datetime.now() - timedelta(minutes=30)).time()
    record.break_end = datetime.now().time()

    db.commit()
    db.refresh(record)
    update_realtime_payroll(current_user.id, db)
    return record


@router.post("/check-out", response_model=schemas.AttendanceResponse)
def check_out(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    today = datetime.now().date()
    record = _get_today_record(db, current_user.id, today)

    if not record.check_in:
        raise HTTPException(status_code=400, detail="출근 기록이 없습니다.")
    if record.break_start and not record.break_end:
        raise HTTPException(
            status_code=400,
            detail="휴식 중에는 퇴근할 수 없습니다. 복귀 후 퇴근해주세요.",
        )
    if record.check_out:
        raise HTTPException(status_code=400, detail="이미 퇴근 기록이 있습니다.")

    record.check_out = datetime.now().time()
    work_minutes, break_minutes = _calc_work_minutes(record)
    record.total_work_minutes = work_minutes
    record.total_break_minutes = break_minutes

    db.commit()
    db.refresh(record)
    update_realtime_payroll(current_user.id, db)
    return record

@router.get("/me", response_model=list[schemas.AttendanceResponse])
def get_my_attendance_records(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    records = (
        db.query(models.Attendance)
        .filter(models.Attendance.user_id == current_user.id)
        .order_by(models.Attendance.work_date.desc())
        .all()
    )
    return records


def _get_today_record(db: Session, user_id: int, today):
    record = (
        db.query(models.Attendance).filter_by(user_id=user_id, work_date=today).first()
    )
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
