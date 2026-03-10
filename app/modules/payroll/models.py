from decimal import Decimal

from sqlalchemy import DECIMAL, Column, Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class Payroll(Base):
    __tablename__ = "payroll"
    __table_args__ = (
        UniqueConstraint("user_id", "year", "month", name="uq_user_year_month"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 기본설정
    year = Column(Integer, nullable=False)  # 연도
    month = Column(Integer, nullable=False)  # 월
    wage = Column(Integer, nullable=False)  # 시급

    # 마지막 근무일
    last_work_day = Column(Date)  # 마지막 근무일

    # 근무시간
    day_hours = Column(DECIMAL(5, 2), default=Decimal("0.00"))  # 월간 주간 근무시간
    night_hours = Column(DECIMAL(5, 2), default=Decimal("0.00"))  # 월간 야간 근무시간
    weekly_allowance_hours = Column(
        DECIMAL(5, 2), default=Decimal("0.00")
    )  # 월간 주휴시간
    holiday_hours = Column(
        DECIMAL(5, 2), default=Decimal("0.00")
    )  # 월간 공휴일 근무시간
    break_hours = Column(DECIMAL(5, 2), default=Decimal("0.00"))  # 월간 휴식 시간

    # 공제
    insurance_health = Column(Integer, default=0)  # 건강보험
    insurance_care = Column(Integer, default=0)  # 요양보험
    insurance_employment = Column(Integer, default=0)  # 고용보험
    insurance_pension = Column(Integer, default=0)  # 국민연금

    user = relationship("User", back_populates="payrolls")


class PayrollPayDate(Base):
    """
    연/월 기준 급여 지급일 관리 테이블
    - 해당 연월 Payroll과 매칭하여 지급일 표시
    """

    __tablename__ = "payroll_pay_date"
    __table_args__ = (
        UniqueConstraint(
            "year",
            "month",
            name="uq_payroll_pay_date_year_month",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    year = Column(Integer, nullable=False)  # 지급 연도
    month = Column(Integer, nullable=False)  # 지급 월

    pay_date = Column(Date, nullable=False)  # 해당 월 급여 지급일
