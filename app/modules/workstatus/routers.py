from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.auth.models import User
from app.modules.auth.services import verify_password
from app.modules.workstatus import models, schemas
from app.modules.workstatus.services import AttendanceService
from app.utils.permission_utils import is_system

router = APIRouter()


# Request Schema
# -----------------------------------
class AttendanceAuthInput(BaseModel):
    username: str
    password: str


# System Token 인증
# -----------------------------------
# 출퇴근 API 자체 접근 권한 체크
# - JWT 토큰 필수
# - system 계정만 접근 가능
def require_system_user(
    user: User = Depends(get_current_user),
) -> User:
    if not is_system(user):
        raise HTTPException(
            status_code=403,
            detail="시스템 계정만 접근 가능합니다.",
        )
    return user


# 출퇴근 대상자 인증 (ID / PW)
# -----------------------------------
# 실제 출퇴근을 찍는 직원 인증
# - 토큰 사용 안함
# - username / password 기반
def authenticate_attendance_user(
    db: Session,
    username: str,
    password: str,
) -> User:
    user = db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()

    # 아이디 / 비밀번호 검증
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=401,
            detail="아이디 또는 비밀번호가 올바르지 않습니다.",
        )

    # 비활성화 계정 차단
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="휴면/비활성화된 계정입니다.",
        )

    return user


# 오늘 출근 기록 조회
# -----------------------------------
# - user_id + work_date 기준
# - 없으면 출근 안 한 상태
def _get_today_record(
    db: Session,
    user_id: int,
    today,
):
    record = (
        db.query(models.Attendance).filter_by(user_id=user_id, work_date=today).first()
    )

    if not record:
        raise HTTPException(
            status_code=400,
            detail="출근 기록이 없습니다.",
        )

    return record


# 근무 시간 계산 (분 단위)
# -----------------------------------
# - 출근 ~ 퇴근 전체 시간
# - 휴게 시간 차감
# - 분 단위 int 반환
def _calc_work_minutes(record: models.Attendance):
    work_date = record.work_date

    # 출근 / 퇴근 datetime 생성
    check_in = datetime.combine(work_date, record.check_in)
    check_out = datetime.combine(work_date, record.check_out)

    # 자정 넘어간 경우 보정
    if check_out < check_in:
        check_out += timedelta(days=1)

    # 전체 체류 시간 (분)
    total_work_minutes = int((check_out - check_in).total_seconds() / 60)

    # 휴게 시간 계산
    break_minutes = 0
    if record.break_start and record.break_end:
        b_start = datetime.combine(work_date, record.break_start)
        b_end = datetime.combine(work_date, record.break_end)

        # 자정 넘어간 휴게시간 보정
        if b_end < b_start:
            b_end += timedelta(days=1)

        break_minutes = int((b_end - b_start).total_seconds() / 60)

    # 실 근무 시간, 휴게 시간 반환
    return total_work_minutes - break_minutes, break_minutes


# 출근
# -----------------------------------
@router.post("/check-in", response_model=schemas.AttendanceResponse, summary="출근등록")
def check_in(
    payload: AttendanceAuthInput,
    db: Session = Depends(get_db),
    system_user: User = Depends(require_system_user),  # 시스템 토큰 검증
):
    # 출퇴근 대상자 인증
    user = authenticate_attendance_user(
        db,
        payload.username,
        payload.password,
    )

    today = datetime.now().date()

    # 이미 출근 기록이 있는지 확인
    existing = (
        db.query(models.Attendance).filter_by(user_id=user.id, work_date=today).first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="이미 오늘 출근 기록이 있습니다.",
        )

    # 출근 기록 생성
    record = models.Attendance(
        user_id=user.id,
        work_date=today,
        check_in=datetime.now().time(),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    # 응답용 필드 (DB 컬럼 아님)
    record.user_name = user.name
    return record


# 휴식 시작
# -----------------------------------
@router.post(
    "/break-start", response_model=schemas.AttendanceResponse, summary="휴식등록"
)
def break_start(
    payload: AttendanceAuthInput,
    db: Session = Depends(get_db),
    system_user: User = Depends(require_system_user),
):
    user = authenticate_attendance_user(
        db,
        payload.username,
        payload.password,
    )

    today = datetime.now().date()
    record = _get_today_record(db, user.id, today)

    # 상태 검증
    if not record.check_in:
        raise HTTPException(status_code=400, detail="출근 먼저 해주세요.")
    if record.check_out:
        raise HTTPException(status_code=400, detail="이미 퇴근한 기록이 있습니다.")
    if record.break_start and not record.break_end:
        raise HTTPException(status_code=400, detail="이미 휴식 중입니다.")

    record.break_start = datetime.now().time()
    db.commit()
    db.refresh(record)

    record.user_name = user.name
    return record


# 휴식 종료
# -----------------------------------
@router.post(
    "/break-end", response_model=schemas.AttendanceResponse, summary="복귀등록"
)
def break_end(
    payload: AttendanceAuthInput,
    db: Session = Depends(get_db),
    system_user: User = Depends(require_system_user),
):
    user = authenticate_attendance_user(
        db,
        payload.username,
        payload.password,
    )

    today = datetime.now().date()
    record = _get_today_record(db, user.id, today)

    if not record.break_start:
        raise HTTPException(
            status_code=400,
            detail="휴식 시작 기록이 없습니다.",
        )

    if record.break_end:
        raise HTTPException(
            status_code=400,
            detail="이미 복귀한 기록이 있습니다.",
        )

    record.break_end = datetime.now().time()
    db.commit()
    db.refresh(record)

    record.user_name = user.name
    return record


# 퇴근
# -----------------------------------
@router.post(
    "/check-out", response_model=schemas.AttendanceResponse, summary="퇴근등록"
)
def check_out(
    payload: AttendanceAuthInput,
    db: Session = Depends(get_db),
    system_user: User = Depends(require_system_user),
):
    # 출퇴근 대상자 인증
    user = authenticate_attendance_user(
        db,
        payload.username,
        payload.password,
    )

    today = datetime.now().date()
    record = _get_today_record(db, user.id, today)

    # 상태 검증
    if not record.check_in:
        raise HTTPException(status_code=400, detail="출근 기록이 없습니다.")
    if record.break_start and not record.break_end:
        raise HTTPException(
            status_code=400,
            detail="휴식 중에는 퇴근할 수 없습니다.",
        )
    if record.check_out:
        raise HTTPException(
            status_code=400,
            detail="이미 퇴근 기록이 있습니다.",
        )

    # 퇴근 시간 기록
    record.check_out = datetime.now().time()

    # Attendance + Payroll 처리 (서비스 연결)
    AttendanceService.handle_check_out(
        db=db,
        record=record,
    )

    db.commit()
    db.refresh(record)

    record.user_name = user.name
    return record


class AttendanceAllInOneInput(BaseModel):
    username: str
    password: str
    work_date: date

    check_in: time
    break_start: time | None = None
    break_end: time | None = None
    check_out: time

    class Config:
        json_schema_extra = {
            "example": {
                "username": "user",
                "password": "user",
                "work_date": "2026-01-01",
                "check_in": "14:00:00",
                "break_start": "15:00:00",
                "break_end": "16:00:00",
                "check_out": "23:00:00",
            }
        }


@router.post(
    "/submit",
    response_model=schemas.AttendanceResponse,
    summary="출근~퇴근 통합 등록",
)
def submit_attendance_all_in_one(
    payload: AttendanceAllInOneInput,
    db: Session = Depends(get_db),
    system_user: User = Depends(require_system_user),  # 시스템 토큰 검증 유지
):
    # 출퇴근 대상자 인증
    user = authenticate_attendance_user(db, payload.username, payload.password)

    work_date = payload.work_date or datetime.now().date()

    # 기존 기록 조회
    record = (
        db.query(models.Attendance)
        .filter_by(user_id=user.id, work_date=work_date)
        .first()
    )

    if not record:
        record = models.Attendance(user_id=user.id, work_date=work_date)
        db.add(record)

    # 필드 세팅
    record.check_in = payload.check_in
    record.break_start = payload.break_start
    record.break_end = payload.break_end
    record.check_out = payload.check_out

    # 상태/순서 검증
    if record.check_out and not record.check_in:
        raise HTTPException(
            status_code=400, detail="check_in 없이 check_out은 불가합니다."
        )

    if record.break_end and not record.break_start:
        raise HTTPException(
            status_code=400, detail="break_start 없이 break_end는 불가합니다."
        )

    # 휴게가 시작됐으면 종료도 있어야 퇴근 가능
    if record.break_start and not record.break_end:
        raise HTTPException(
            status_code=400, detail="휴식 종료(break_end) 없이 퇴근 처리할 수 없습니다."
        )

    # 실제 근무시간 계산
    work_minutes, break_minutes = _calc_work_minutes(record)
    if work_minutes < 0:
        raise HTTPException(
            status_code=400,
            detail="근무 시간이 0보다 작을 수 없습니다. 시간 입력을 확인하세요.",
        )
    db.commit()
    db.refresh(record)

    # 여기서 퇴근 처리 + Payroll 반영
    AttendanceService.handle_check_out(
        db=db,
        record=record,
    )

    db.commit()
    db.refresh(record)

    # 응답용 필드
    record.user_name = user.name
    return record
