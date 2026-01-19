from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_serializer

from app.modules.auth.models import GenderEnum, PositionEnum


# ---------- User(=직원) ----------
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(
        min_length=4, max_length=255
    )  # 해시 대상(서비스에서 해시하도록)
    name: str = Field(min_length=2, max_length=10)
    position: PositionEnum
    gender: GenderEnum
    birth_date: Optional[date] = None
    ssn: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    hire_date: Optional[date] = None
    retire_date: Optional[date] = None
    unavailable_days: Optional[list[int]] = None
    health_cert_expire: Optional[date] = None
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


class UserDetailOut(UserOut):
    ssn: Optional[str]
    bank_name: Optional[str]
    account_number: Optional[str]
    hire_date: Optional[date]
    retire_date: Optional[date]
    unavailable_days: Optional[list[int]]
    health_cert_expire: Optional[date]


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
    year: int

    national_pension_rate: Decimal  # 국민연금
    health_insurance_rate: Decimal  # 건강보험
    long_term_care_rate: Decimal  # 요양보험
    employment_insurance_rate: Decimal  # 고용보험

    class Config:
        json_schema_extra = {
            "example": {
                "year": "2025",
                "national_pension_rate": "4.75",
                "health_insurance_rate": "3.595",
                "long_term_care_rate": "12.95",
                "employment_insurance_rate": "0.9",
            }
        }


class InsuranceRateUpdate(BaseModel):
    national_pension_rate: Decimal
    health_insurance_rate: Decimal
    long_term_care_rate: Decimal
    employment_insurance_rate: Decimal


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

        return str(value.quantize(Decimal("0.0000"), rounding=ROUND_HALF_UP))

    model_config = {"from_attributes": True}
