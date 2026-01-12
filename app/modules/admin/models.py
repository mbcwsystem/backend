from __future__ import annotations

import enum
from datetime import date

from sqlalchemy import (
    Column,
    Integer,
    Date,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import TimeStampedMixin
from app.core.database import Base


# 공휴일
class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)

    date = Column(Date, nullable=False, comment="공휴일 날짜")
    label = Column(String(100), nullable=False, comment="공휴일 설명")

    __table_args__ = (UniqueConstraint("date", name="uq_holiday_date"),)

class InsuranceRate(TimeStampedMixin, Base):
    """
    근로자 공제 보험 요율 (연 단위)
    - 국민연금
    - 건강보험
    - 장기요양보험
    - 고용보험
    """

    __tablename__ = "insurance_rates"
    __table_args__ = (
        UniqueConstraint("year", name="uq_insurance_rates_year"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    year = Column(
        Integer,
        nullable=False,
        comment="보험 요율 기준 연도 (예: 2025)",
    )

    # 요율은 % 그대로 저장 (예: 9.0000 = 9%)
    national_pension_rate = Column(
        Numeric(8, 4),
        nullable=False,
        comment="국민연금 요율 (근로자 부담)",
    )

    health_insurance_rate = Column(
        Numeric(8, 4),
        nullable=False,
        comment="건강보험 요율 (근로자 부담)",
    )

    long_term_care_rate = Column(
        Numeric(8, 4),
        nullable=False,
        comment="장기요양보험 요율 (건강보험 대비)",
    )

    employment_insurance_rate = Column(
        Numeric(8, 4),
        nullable=False,
        comment="고용보험 요율 (근로자 부담)",
    )