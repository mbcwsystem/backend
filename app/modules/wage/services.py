from datetime import date

from sqlalchemy.orm import Session

from app.modules.wage.models import DefaultWage, UserWage


def get_applicable_wage(user_id: int, work_date: date, db: Session):
    user_wage = (
        db.query(UserWage)
        .filter(
            UserWage.user_id == user_id,
            UserWage.start_date <= work_date,
            (UserWage.end_date.is_(None)) | (UserWage.end_date >= work_date),
        )
        .order_by(UserWage.start_date.desc())
        .first()
    )
    if user_wage:
        return user_wage.wage

    year = work_date.year
    default_wage = db.query(DefaultWage).filter_by(year=year).first()
    if default_wage:
        return default_wage.wage

    return -1
