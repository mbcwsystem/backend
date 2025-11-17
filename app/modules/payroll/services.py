from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.modules.payroll.models import Payroll, WeeklyPayroll
from app.modules.attendance import models
from app.modules.wage.services import get_applicable_wage

def get_week_range(target_date: date):
    """해당 날짜의 주차 시작일(월)과 종료일(일)을 반환"""
    start = target_date - timedelta(days=target_date.weekday())
    end = start + timedelta(days=6)
    return start, end


def update_realtime_payroll(user_id: int, db: Session):
    today = date.today()
    year, month = today.year, today.month
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    print(f"🔄 [DEBUG] update_realtime_payroll triggered for user={user_id}")

    attendances = (
        db.query(models.Attendance)
        .filter(
            models.Attendance.user_id == user_id,
            models.Attendance.work_date.between(week_start, week_end),
        )
        .all()
    )

    print(f"🧾 Attendance count this week: {len(attendances)}")

    total_week_minutes = sum(a.total_work_minutes or 0 for a in attendances)
    total_week_hours = Decimal(total_week_minutes) / Decimal(60)
    print(f"⏱ total_week_hours={total_week_hours}")

    # WeeklyPayroll
    weekly = (
        db.query(WeeklyPayroll)
        .filter_by(user_id=user_id, year=year, month=month)
        .first()
    )

    if not weekly:
        weekly = WeeklyPayroll(
            user_id=user_id, year=year, month=month, total_work_hours=total_week_hours
        )
        db.add(weekly)
        print("🆕 WeeklyPayroll created")
    else:
        weekly.total_work_hours = total_week_hours
        print("♻️ WeeklyPayroll updated")

    # Payroll
    total_month_minutes = (
        db.query(models.Attendance)
        .filter(
            models.Attendance.user_id == user_id,
            models.Attendance.work_date.between(date(year, month, 1), today),
        )
        .with_entities(models.Attendance.total_work_minutes)
        .all()
    )
    total_month_hours = Decimal(sum(m[0] or 0 for m in total_month_minutes)) / Decimal(60)

    hourly_wage = get_applicable_wage(user_id, today)

    payroll = (
        db.query(Payroll)
        .filter_by(user_id=user_id, year=year, month=month)
        .first()
    )
    if not payroll:
        payroll = Payroll(
            user_id=user_id,
            year=year,
            month=month,
            hourly_wage=hourly_wage,
            total_hours=total_month_hours,
            weekly_hours=total_week_hours,
            total_salary=int(hourly_wage * float(total_month_hours)),
        )
        db.add(payroll)
        print("🆕 Payroll created")
    else:
        payroll.total_hours = total_month_hours
        payroll.weekly_hours = total_week_hours
        payroll.total_salary = int(hourly_wage * float(total_month_hours))
        print("♻️ Payroll updated")

    db.commit()
    print("✅ Payroll & WeeklyPayroll committed.")
    db.refresh(payroll)
    return payroll