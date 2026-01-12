from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_serializer

from app.modules.auth.models import GenderEnum, PositionEnum


# ---------- User(=직원) ----------
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(
        min_length=4, max_length=255
    )  # 해시 대상(서비스에서 해시하도록)
    name: str
    position: PositionEnum
    gender: GenderEnum
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: bool = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[PositionEnum] = None
    gender: Optional[GenderEnum] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    username: str
    name: str
    position: PositionEnum
    gender: GenderEnum
    phone: Optional[str]
    email: Optional[EmailStr]
    is_active: bool

    class Config:
        from_attributes = True


class PaginatedUsers(BaseModel):
    total: int
    items: List[UserOut]


# ---------- 공휴일(전사 공휴일) ----------
class HolidayCreate(BaseModel):
    date: date
    label: str


class HolidayUpdate(BaseModel):
    date: Optional[date] = None
    label: Optional[str] = None


class HolidayOut(BaseModel):
    id: int
    date: date
    label: str

    class Config:
        from_attributes = True

class InsuranceRateCreate(BaseModel):
    year: int = Field(..., example=2025)

    national_pension_rate: Decimal = Field(
        ..., example="4.5", description="국민연금 요율 (%)"
    )
    health_insurance_rate: Decimal = Field(
        ..., example="3.595", description="건강보험 요율 (%)"
    )
    long_term_care_rate: Decimal = Field(
        ..., example="12.95", description="장기요양보험 요율 (건강보험 대비 %)"
    )
    employment_insurance_rate: Decimal = Field(
        ..., example="0.9", description="고용보험 요율 (%)"
    )

class InsuranceRateUpdate(BaseModel):
    national_pension_rate: Decimal | None = Field(
        None, example="9.0000"
    )
    health_insurance_rate: Decimal | None = Field(
        None, example="7.1200"
    )
    long_term_care_rate: Decimal | None = Field(
        None, example="12.9500"
    )
    employment_insurance_rate: Decimal | None = Field(
        None, example="0.9000"
    )

class InsuranceRateResponse(BaseModel):
    id: int
    year: int

    national_pension_rate: Optional[float] = None
    health_insurance_rate: Optional[float] = None
    long_term_care_rate: Optional[float] = None
    employment_insurance_rate: Optional[float] = None

    @field_serializer(
        "national_pension_rate",
        "health_insurance_rate",
        "long_term_care_rate",
        "employment_insurance_rate",
        when_used="json",
    )
    def serialize_rate(self, value: Decimal):
        if value is None:
            return None
        if isinstance(value, float):
            value = Decimal(str(value))

        return str(
            value.quantize(Decimal("0.0000"), rounding=ROUND_HALF_UP)
        )

    model_config = {"from_attributes": True}