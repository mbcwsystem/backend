from datetime import datetime

from sqlalchemy import extract
from sqlalchemy.orm import Session

from app.modules.attendance import models as attendance_models
from app.modules.payroll import models as payroll_models
from app.modules.wage.services import get_applicable_wage


def update_realtime_payroll(user_id: int, db: Session):
    today = datetime.now().date()
    year, month = today.year, today.month

    records = (
        db.query(attendance_models.Attendance)
        .filter(
            attendance_models.Attendance.user_id == user_id,
            extract("year", attendance_models.Attendance.work_date) == year,
            extract("month", attendance_models.Attendance.work_date) == month,
        )
        .all()
    )

    if not records:
        return None

    total_work_minutes = sum(r.total_work_minutes for r in records)
    total_break_minutes = sum(r.total_break_minutes for r in records)
    total_hours = round(total_work_minutes / 60, 2)
    break_hours = round(total_break_minutes / 60, 2)

    wages = []
    for record in records:
        wage = get_applicable_wage(user_id, record.work_date, db)
        wages.append((wage, record.total_work_minutes))

    if total_work_minutes == 0:
        weighted_wage = 0
    else:
        weighted_wage = sum(w * m for w, m in wages) / total_work_minutes

    total_salary = int(total_hours * weighted_wage)

    payroll = (
        db.query(payroll_models.Payroll)
        .filter_by(user_id=user_id, year=year, month=month)
        .first()
    )

    if not payroll:
        payroll = payroll_models.Payroll(
            user_id=user_id,
            year=year,
            month=month,
            total_hours=total_hours,
            break_hours=break_hours,
            total_salary=total_salary,
            insurance_health=0,
            insurance_employment=0,
            insurance_pension=0,
            insurance_care=0,
            total_deduction=0,
            net_salary=total_salary,  # 공제 전 실지급액
        )
        db.add(payroll)
    else:
        payroll.total_hours = total_hours
        payroll.break_hours = break_hours
        payroll.total_salary = total_salary
        payroll.net_salary = total_salary  # 단순 갱신 (추후 공제 계산 추가 가능)

    db.commit()
    db.refresh(payroll)
    return payroll


def recalculate_all_users(db: Session):
    from app.modules.auth.models import User

    users = db.query(User).all()
    for user in users:
        update_realtime_payroll(user.id, db)

    return {"status": "success", "message": f"{len(users)} users payroll recalculated."}
