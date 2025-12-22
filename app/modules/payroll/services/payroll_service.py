from typing import List, Union, Optional

from sqlalchemy.orm import Session

from app.modules.payroll.models import Payroll
from app.modules.payroll.schemas import (
    PayrollResponse,
    PayrollPayResponse,
)
from app.modules.auth.models import User
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
            return [PayrollService._to_admin_response(p) for p in payrolls]

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

        return PayrollService._to_user_pay_response(payroll)

    # 관리자 Response
    @staticmethod
    def _to_admin_response(payroll: Payroll) -> PayrollResponse:
        user = payroll.user

        total_work_hours = (
            float(payroll.day_hours)
            + float(payroll.night_hours)
            + float(payroll.weekly_allowance_hours)
            + float(payroll.holiday_hours)
        )

        gross_pay = int(total_work_hours * payroll.wage)

        total_deduction = (
            payroll.insurance_health
            + payroll.insurance_care
            + payroll.insurance_employment
            + payroll.insurance_pension
        )

        return PayrollResponse(
            # 인적 정보
            name=user.name,
            position=user.position,
            wage=payroll.wage,
            rrn=user.ssn,
            join_date=user.hire_date,
            resign_date=user.retire_date,
            email=user.email,
            bank_name=user.bank_name,
            bank_account=user.account_number,
            # 근무 요약
            total_work_hours=total_work_hours,
            avg_daily_hours=(total_work_hours / 20 if total_work_hours else None),
            # 근무 시간
            day_hours=float(payroll.day_hours),
            night_hours=float(payroll.night_hours),
            weekly_allowance_hours=float(payroll.weekly_allowance_hours),
            holiday_hours=float(payroll.holiday_hours),
            # 급여
            gross_pay=gross_pay,
            # 공제
            insurance_health=payroll.insurance_health,
            insurance_care=payroll.insurance_care,
            insurance_employment=payroll.insurance_employment,
            insurance_pension=payroll.insurance_pension,
            total_deduction=total_deduction,
            net_pay=gross_pay - total_deduction,
        )

    # 일반 사용자 Response
    @staticmethod
    def _to_user_pay_response(payroll: Payroll) -> PayrollPayResponse:
        user = payroll.user

        day_pay = int(payroll.wage * float(payroll.day_hours))
        night_pay = int(payroll.wage * float(payroll.night_hours))
        weekly_allowance_pay = int(payroll.wage * float(payroll.weekly_allowance_hours))

        gross_pay = day_pay + night_pay + weekly_allowance_pay

        total_deduction = (
            payroll.insurance_health
            + payroll.insurance_care
            + payroll.insurance_employment
            + payroll.insurance_pension
        )

        return PayrollPayResponse(
            # 기본 정보
            name=user.name,
            birth_date=user.birth_date,
            pay_date=None,  # TODO: 지급일 컬럼/테이블 추가 시 연결
            # 급여 항목
            day_wage=day_pay,
            night_wage=night_pay,
            weekly_allowance_pay=weekly_allowance_pay,
            annual_leave_pay=0,
            holiday_pay=0,
            extra_pay=0,
            gross_pay=gross_pay,
            # 공제
            insurance_health=payroll.insurance_health,
            insurance_care=payroll.insurance_care,
            insurance_employment=payroll.insurance_employment,
            insurance_pension=payroll.insurance_pension,
            total_deduction=total_deduction,
            # 실지급액
            net_pay=gross_pay - total_deduction,
        )
