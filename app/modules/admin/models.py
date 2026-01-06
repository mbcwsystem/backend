from __future__ import annotations

import enum
from datetime import date
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    Date,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import TimeStampedMixin
from app.core.database import Base


# 직원(사원) - 관리자 계정 생성/조회/수정/삭제 대상
class Employee(TimeStampedMixin, Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


# 공휴일
class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)

    date = Column(Date, nullable=False, comment="공휴일 날짜")
    label = Column(String(100), nullable=False, comment="공휴일 설명")

    __table_args__ = (UniqueConstraint("date", name="uq_holiday_date"),)


# 4대 보험 요율(버전/시점 관리)
class InsuranceRate(TimeStampedMixin, Base):
    __tablename__ = "insurance_rates"
    __table_args__ = (
        UniqueConstraint("effective_date", name="uq_insurance_rate_effective_date"),
        Index("idx_insurance_rate_effective_date", "effective_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 각각 % 단위(예: 9.15%)를 9.15로 저장. 소수 2자리까지 허용
    national_pension: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    health_insurance: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    employment_insurance: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    industrial_accident: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    effective_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )  # 시행일(동일일자 중복 불가)


class InsuranceCategoryEnum(str, enum.Enum):
    health = "건강보험"
    care = "요양보험"
    employment = "고용보험"
    pension = "국민연금"
