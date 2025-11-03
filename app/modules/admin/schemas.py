# app/modules/admin/schemas.py
from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from app.modules.admin.models import InsuranceCategoryEnum
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
    name: str
    date: date
    description: Optional[str] = None


class HolidayUpdate(BaseModel):
    name: Optional[str] = None
    date: Optional[date] = None
    description: Optional[str] = None


class HolidayOut(BaseModel):
    id: int
    name: str
    date: date
    description: Optional[str]

    class Config:
        from_attributes = True


# ---------- 보험 요율(카테고리별) ----------
class InsuranceRateSet(BaseModel):
    category: InsuranceCategoryEnum
    rate: float  # DECIMAL(6,4) 매핑
    effective_date: date


class InsuranceRateOut(BaseModel):
    id: int
    category: InsuranceCategoryEnum
    rate: float
    effective_date: date

    class Config:
        from_attributes = True
