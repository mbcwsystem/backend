from sqlalchemy.orm import Session
from decimal import Decimal

from app.modules.payroll.models import PayrollWeeklyAllowanceHours
from app.utils.date_utils import get_iso_week_range


def get_weekly_allowance_by_month(
    db: Session,
    user_id: int,
    year: int,
    month: int,
):
    """
    월 기준으로 해당되는 ISO 주휴시간 조회
    """
    records = db.query(PayrollWeeklyAllowanceHours).filter(
        PayrollWeeklyAllowanceHours.user_id == user_id
    ).all()

    result = []

    for record in records:
        week_start, week_end = get_iso_week_range(
            record.iso_year,
            record.iso_week,
        )

        # 해당 월과 겹치는 주만 포함
        if (
            week_start.month == month
            or week_end.month == month
        ):
            result.append({
                "user_id": record.user_id,
                "iso_year": record.iso_year,
                "iso_week": record.iso_week,
                "week_start_date": week_start,
                "week_end_date": week_end,
                "allowance_hours": float(record.allowance_hours),
            })

    return result


def upsert_weekly_allowance(
    db: Session,
    user_id: int,
    iso_year: int,
    iso_week: int,
    allowance_hours: Decimal,
):
    """
    주휴시간 UPSERT
    """
    record = db.query(PayrollWeeklyAllowanceHours).filter(
        PayrollWeeklyAllowanceHours.user_id == user_id,
        PayrollWeeklyAllowanceHours.iso_year == iso_year,
        PayrollWeeklyAllowanceHours.iso_week == iso_week,
    ).first()

    if record:
        record.allowance_hours = allowance_hours
    else:
        record = PayrollWeeklyAllowanceHours(
            user_id=user_id,
            iso_year=iso_year,
            iso_week=iso_week,
            allowance_hours=allowance_hours,
        )
        db.add(record)

    db.commit()
    return record