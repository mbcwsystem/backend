from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.orm import Session

from app.modules.admin.models import Holiday
from app.modules.payroll.models import Payroll
from app.modules.wage.models import DefaultWage
from app.modules.workstatus import models


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
    ) -> tuple[int, int, int]:
        work_date = record.work_date

        check_in = datetime.combine(work_date, record.check_in)
        check_out = datetime.combine(work_date, record.check_out)

        if check_out < check_in:
            check_out += timedelta(days=1)

        # 휴게 시간 계산
        break_minutes = 0
        if record.break_start and record.break_end:
            b_start = datetime.combine(work_date, record.break_start)
            b_end = datetime.combine(work_date, record.break_end)
            if b_end < b_start:
                b_end += timedelta(days=1)
            break_minutes = int((b_end - b_start).total_seconds() / 60)

        # 야간 기준
        night_start = datetime.combine(
            work_date, datetime.strptime("22:00", "%H:%M").time()
        )
        night_end = datetime.combine(
            work_date + timedelta(days=1), datetime.strptime("06:00", "%H:%M").time()
        )

        day_minutes = 0
        night_minutes = 0

        current = check_in
        while current < check_out:
            next_minute = current + timedelta(minutes=1)

            if night_start <= current < night_end:
                night_minutes += 1
            else:
                day_minutes += 1

            current = next_minute

        # 휴게시간은 주간에서 차감 (정책상 제일 단순)
        day_minutes = max(day_minutes - break_minutes, 0)

        return day_minutes, night_minutes, break_minutes

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
            user_id=user_id, year=work_date.year, month=work_date.month, wage=wage
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
        day_minutes, night_minutes, break_minutes = AttendanceService.calc_work_minutes(
            record
        )
        record.total_work_minutes = day_minutes + night_minutes
        record.total_break_minutes = break_minutes

        payroll = AttendanceService.get_or_create_payroll(
            db,
            user_id=record.user_id,
            work_date=record.work_date,
        )

        if payroll.day_hours is None:
            payroll.day_hours = Decimal("0.00")
        if payroll.night_hours is None:
            payroll.night_hours = Decimal("0.00")
        if payroll.break_hours is None:
            payroll.break_hours = Decimal("0.00")
        if payroll.holiday_hours is None:
            payroll.holiday_hours = Decimal("0.00")

        # 누적
        payroll.day_hours += AttendanceService.minutes_to_hours(day_minutes)
        payroll.night_hours += AttendanceService.minutes_to_hours(night_minutes)
        payroll.break_hours += AttendanceService.minutes_to_hours(break_minutes)

        if is_holiday(db, record.work_date):
            payroll.holiday_hours += AttendanceService.minutes_to_hours(
                record.total_work_minutes
            )

        payroll.last_work_day = record.work_date

        # =========================
        # ISO 주 기준 정보
        # =========================
        work_date = record.work_date
        iso_year, iso_week, iso_weekday = work_date.isocalendar()

        # =========================
        # 해당 ISO 주 누적 근무시간 계산
        # =========================
        weekly_total_minutes = 0

        week_start = work_date - timedelta(days=iso_weekday - 1)

        # ISO 주 끝 (일요일)
        week_end = week_start + timedelta(days=6)

        weekly_records = (
            db.query(models.Attendance)
            .filter(
                models.Attendance.user_id == record.user_id,
                models.Attendance.check_out.isnot(None),
                models.Attendance.work_date >= week_start,
                models.Attendance.work_date <= week_end,
            )
            .all()
        )

        weekly_work_days = set()

        for r in weekly_records:
            weekly_work_days.add(r.work_date)
            weekly_total_minutes += r.total_work_minutes

        weekly_total_hours = (Decimal(weekly_total_minutes) / Decimal("60")).quantize(
            Decimal("0.01")
        )

        # =========================
        # 주휴 발생 조건: 주 15시간 이상
        # =========================
        if weekly_total_hours < Decimal("15.00"):
            db.flush()
            record.is_payroll_applied = True
            return record

        # =========================
        # Recalculate MONTHLY weekly allowance (overwrite)
        # =========================

        # Get current payroll (month based)
        current_payroll = AttendanceService.get_or_create_payroll(
            db=db,
            user_id=record.user_id,
            work_date=record.work_date,
        )

        monthly_weekly_allowance_hours = Decimal("0.00")

        # Fetch all attendance records in the same month
        monthly_records = (
            db.query(models.Attendance)
            .filter(
                models.Attendance.user_id == record.user_id,
                models.Attendance.check_out.isnot(None),
                models.Attendance.work_date
                >= date(current_payroll.year, current_payroll.month, 1),
                models.Attendance.work_date
                < (
                    date(current_payroll.year, current_payroll.month, 1)
                    + timedelta(days=32)
                ).replace(day=1),
            )
            .all()
        )

        # Group by ISO week
        weeks = {}

        for r in monthly_records:
            y, w, _ = r.work_date.isocalendar()
            weeks.setdefault((y, w), []).append(r)

        for (y, w), records in weeks.items():
            week_start = min(r.work_date for r in records)
            week_end = week_start + timedelta(days=6)

            # 주 종료일이 현재 Payroll 월이 아니면 제외
            if week_end.month != current_payroll.month:
                continue

            total_minutes = 0
            work_days = set()

            for r in records:
                total_minutes += r.total_work_minutes
                work_days.add(r.work_date)
            if not work_days:
                continue

            total_hours = (Decimal(total_minutes) / Decimal("60")).quantize(
                Decimal("0.01")
            )

            if total_hours < Decimal("15.00"):
                continue

            weekly_allowance = (total_hours / Decimal(len(work_days))).quantize(
                Decimal("0.01")
            )

            monthly_weekly_allowance_hours += weekly_allowance

        # 🔥 OVERWRITE (not +=)
        current_payroll.weekly_allowance_hours = monthly_weekly_allowance_hours

        db.flush()
        record.is_payroll_applied = True

        return record


def get_default_wage_by_year(db: Session, year: int) -> int:
    default_wage = db.query(DefaultWage).filter_by(year=year).first()

    if default_wage:
        return default_wage.wage

    return 0


def is_holiday(db: Session, target_date: date) -> bool:
    return db.query(Holiday.id).filter(Holiday.date == target_date).first() is not None
