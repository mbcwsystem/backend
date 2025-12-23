from datetime import datetime, timedelta, date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.modules.workstatus import models
from app.modules.payroll.models import Payroll
from app.modules.wage.models import DefaultWage


class AttendanceService:
    """
    Attendance 비즈니스 로직
    - 근무시간 계산
    - Payroll 월 단위 누적
    """

    # 출근 기록 조회
    @staticmethod
    def get_today_record(
        db: Session,
        user_id: int,
        today: date,
    ) -> models.Attendance:
        record = (
            db.query(models.Attendance)
            .filter_by(user_id=user_id, work_date=today)
            .first()
        )
        if not record:
            raise ValueError("출근 기록이 없습니다.")
        return record

    # 근무 시간 계산 (분 단위)
    @staticmethod
    def calc_work_minutes(
        record: models.Attendance,
    ) -> tuple[int, int]:
        work_date = record.work_date

        check_in = datetime.combine(work_date, record.check_in)
        check_out = datetime.combine(work_date, record.check_out)

        if check_out < check_in:
            check_out += timedelta(days=1)

        total_work_minutes = int(
            (check_out - check_in).total_seconds() / 60
        )

        break_minutes = 0
        if record.break_start and record.break_end:
            b_start = datetime.combine(work_date, record.break_start)
            b_end = datetime.combine(work_date, record.break_end)

            if b_end < b_start:
                b_end += timedelta(days=1)

            break_minutes = int(
                (b_end - b_start).total_seconds() / 60
            )

        return total_work_minutes - break_minutes, break_minutes

    # Payroll 가져오기 or 생성
    @staticmethod
    def get_or_create_payroll(
        db: Session,
        user_id: int,
        work_date: date,
    ) -> Payroll:
        payroll = (
            db.query(Payroll)
            .filter_by(
                user_id=user_id,
                year=work_date.year,
                month=work_date.month,
            )
            .first()
        )

        if payroll:
            return payroll

        wage = get_default_wage_by_year(db=db, year=work_date.year)

        payroll = Payroll(
            user_id=user_id,
            year=work_date.year,
            month=work_date.month,
            wage=wage
        )

        db.add(payroll)
        db.flush()  # id 확보
        return payroll

    # 분 → 시간 변환
    @staticmethod
    def minutes_to_hours(minutes: int) -> Decimal:
        return (Decimal(minutes) / Decimal(60)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    # 퇴근 처리 + Payroll 누적
    @staticmethod
    def handle_check_out(
        db: Session,
        record: models.Attendance,
    ) -> models.Attendance:
        work_minutes, break_minutes = AttendanceService.calc_work_minutes(record)

        record.total_work_minutes = work_minutes
        record.total_break_minutes = break_minutes

        payroll = AttendanceService.get_or_create_payroll(
            db,
            user_id=record.user_id,
            work_date=record.work_date,
        )

        payroll.day_hours += AttendanceService.minutes_to_hours(work_minutes)

        return record

def get_default_wage_by_year(db: Session, year: int) -> int:
    default_wage = (
        db.query(DefaultWage)
        .filter_by(year=year)
        .first()
    )

    if default_wage:
        return default_wage.wage

    return 0