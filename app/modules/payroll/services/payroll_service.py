from datetime import date, timedelta
from decimal import ROUND_DOWN, Decimal
from typing import List, Optional, Union

from sqlalchemy.orm import Session

from app.modules.admin.models import InsuranceRate
from app.modules.auth.models import User
from app.modules.payroll.models import Payroll, PayrollPayDate
from app.modules.payroll.schemas import PayrollPayResponse, PayrollResponse
from app.modules.workstatus.models import Attendance
from app.utils.permission_utils import is_admin


class PayrollService:
    """
    급여 조회 서비스
    - 관리자는 모두 조회
    - 그 외 개인 조회
    - 시스템은 접근 못함
    """

    @staticmethod
    def get_payrolls(
        *,
        db: Session,
        user: User,
        year: int,
        month: Optional[int] = None,
    ) -> Union[List[PayrollResponse], PayrollPayResponse]:
        """
        급여 조회
        """

        # 관리자: 급여 명세서 전체 조회
        if is_admin(user):
            query = (
                db.query(Payroll)
                .join(User, Payroll.user_id == User.id)
                .filter(Payroll.year == year)
            )

            if month is not None:
                query = query.filter(Payroll.month == month)

            payrolls = query.all()
            return [PayrollService._to_admin_response(p, db) for p in payrolls]

        # 사용자: 본인 급여 조회
        payroll = (
            db.query(Payroll)
            .filter(
                Payroll.user_id == user.id,
                Payroll.year == year,
                Payroll.month == month,
            )
            .first()
        )

        if not payroll:
            return PayrollPayResponse()

        return PayrollService._to_user_pay_response(payroll, db)

    # 관리자 Response
    @staticmethod
    def _to_admin_response(payroll: Payroll, db: Session) -> PayrollResponse:
        user = payroll.user

        day_wage = int(payroll.wage * float(payroll.day_hours))
        night_wage = int(payroll.wage * float(payroll.night_hours) * 1.5)
        weekly_allowance_pay = int(payroll.wage * float(payroll.weekly_allowance_hours))
        holiday_pay = int(payroll.wage * float(payroll.holiday_hours) * 1.5)
        annual_leave_pay = payroll.wage * float(user.annual_leave_hours)

        gross_pay = (
            day_wage
            + night_wage
            + weekly_allowance_pay
            + holiday_pay
            + int(annual_leave_pay)
        )

        total_work_hours = float(payroll.day_hours) + float(payroll.night_hours)

        rate_year = get_insurance_rate_year(payroll.year, payroll.month)
        rate = get_insurance_rate(db, rate_year)

        gross_pay_decimal = Decimal(gross_pay)

        health = Decimal(payroll.insurance_health or 0)
        care = Decimal(payroll.insurance_care or 0)
        employment = Decimal(payroll.insurance_employment or 0)
        pension = Decimal(payroll.insurance_pension or 0)

        if rate:
            if health == 0:
                health = (
                    gross_pay_decimal * rate.health_insurance_rate / Decimal("100")
                ).quantize(Decimal("1E1"), rounding=ROUND_DOWN)

            if care == 0:
                care = (health * rate.long_term_care_rate / Decimal("100")).quantize(
                    Decimal("1E1"), rounding=ROUND_DOWN
                )

            if employment == 0:
                employment = (
                    gross_pay_decimal * rate.employment_insurance_rate / Decimal("100")
                ).quantize(Decimal("1E1"), rounding=ROUND_DOWN)

            if pension == 0:
                pension = (
                    gross_pay_decimal * rate.national_pension_rate / Decimal("100")
                ).quantize(Decimal("1E1"), rounding=ROUND_DOWN)

        total_deduction = health + care + employment + pension

        total_work_days = (
            db.query(Attendance.work_date)
            .filter(
                Attendance.user_id == payroll.user_id,
                Attendance.work_date >= date(payroll.year, payroll.month, 1),
                Attendance.work_date
                < (date(payroll.year, payroll.month, 1) + timedelta(days=32)).replace(
                    day=1
                ),
                Attendance.check_out.isnot(None),
            )
            .distinct()
            .count()
        )

        return PayrollResponse(
            # 인적 정보
            name=user.name,
            position=user.position,
            wage=payroll.wage,
            rrn=user.ssn,
            join_date=user.hire_date,
            resign_date=user.retire_date,
            last_work_day=payroll.last_work_day,
            bank_name=user.bank_name,
            bank_account=user.account_number,
            email=user.email,
            total_work_days=total_work_days,
            # 근무 요약
            total_work_hours=total_work_hours,
            avg_daily_hours=(
                float(total_work_hours / total_work_days)
                if total_work_days > 0
                else None
            ),
            # 근무 시간
            day_hours=float(payroll.day_hours),
            night_hours=float(payroll.night_hours),
            weekly_allowance_hours=float(payroll.weekly_allowance_hours),
            annual_leave_hours=float(user.annual_leave_hours or 0),
            holiday_hours=float(payroll.holiday_hours),
            day_wage=day_wage,
            night_wage=night_wage,
            weekly_allowance_pay=weekly_allowance_pay,
            annual_leave_pay=int(annual_leave_pay),
            holiday_pay=holiday_pay,
            # 급여
            gross_pay=gross_pay,
            # 공제
            insurance_health=int(health),
            insurance_care=int(care),
            insurance_employment=int(employment),
            insurance_pension=int(pension),
            total_deduction=int(total_deduction),
            net_pay=gross_pay - int(total_deduction),
        )

    # 일반 사용자 Response
    @staticmethod
    def _to_user_pay_response(
        payroll: Payroll,
        db: Session,
    ) -> PayrollPayResponse:
        user = payroll.user
        pay_date = get_pay_date(db, payroll.year, payroll.month)

        day_pay = int(payroll.wage * float(payroll.day_hours))
        night_pay = int(payroll.wage * (float(payroll.night_hours) * 1.5))
        weekly_allowance_pay = int(payroll.wage * float(payroll.weekly_allowance_hours))
        annual_leave_pay = int(payroll.wage * float(user.annual_leave_hours))
        holiday_pay = int(payroll.wage * (float(payroll.holiday_hours) * 1.5))
        gross_pay = (
            day_pay + night_pay + weekly_allowance_pay + annual_leave_pay + holiday_pay
        )
        rate_year = get_insurance_rate_year(payroll.year, payroll.month)
        rate = get_insurance_rate(db, rate_year)

        gross_pay_decimal = Decimal(gross_pay)

        health = Decimal(payroll.insurance_health or 0)
        care = Decimal(payroll.insurance_care or 0)
        employment = Decimal(payroll.insurance_employment or 0)
        pension = Decimal(payroll.insurance_pension or 0)

        if rate:
            if health == 0:
                health = (
                    gross_pay_decimal * rate.health_insurance_rate / Decimal("100")
                ).quantize(Decimal("1E1"), rounding=ROUND_DOWN)

            if care == 0:
                care = (health * rate.long_term_care_rate / Decimal("100")).quantize(
                    Decimal("1E1"), rounding=ROUND_DOWN
                )

            if employment == 0:
                employment = (
                    gross_pay_decimal * rate.employment_insurance_rate / Decimal("100")
                ).quantize(Decimal("1E1"), rounding=ROUND_DOWN)

            if pension == 0:
                pension = (
                    gross_pay_decimal * rate.national_pension_rate / Decimal("100")
                ).quantize(Decimal("1E1"), rounding=ROUND_DOWN)

        total_deduction = health + care + employment + pension

        return PayrollPayResponse(
            # 기본 정보
            name=user.name,
            position=user.position,
            birth_date=user.birth_date,
            pay_date=pay_date,
            # 급여 항목
            day_wage=day_pay,  # 주간
            night_wage=night_pay,  # 야간
            weekly_allowance_pay=weekly_allowance_pay,  # 주휴
            annual_leave_pay=annual_leave_pay,  # 연차
            holiday_pay=holiday_pay,  # 공휴일
            # extra_pay=0, 기타수당 제거예쩡
            gross_pay=gross_pay,  # 급여 총계
            # 공제
            insurance_health=int(health),  # 건강
            insurance_care=int(care),  # 요양
            insurance_employment=int(employment),  # 고용
            insurance_pension=int(pension),  # 국민
            total_deduction=int(total_deduction),  # 공제계
            # 실지급액
            net_pay=gross_pay - int(total_deduction),
        )


def get_insurance_rate_year(year: int, month: int) -> int:
    # 1~6월: 전년도 보험료율, 7~12월: 해당 연도 보험료율
    return year if month >= 7 else year - 1


def get_insurance_rate(db: Session, rate_year: int):
    return db.query(InsuranceRate).filter(InsuranceRate.year == rate_year).first()


def get_pay_date(db: Session, year: int, month: int):
    pay_date = (
        db.query(PayrollPayDate)
        .filter(
            PayrollPayDate.year == year,
            PayrollPayDate.month == month,
        )
        .first()
    )
    return pay_date.pay_date if pay_date else None
