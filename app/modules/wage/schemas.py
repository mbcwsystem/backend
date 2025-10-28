# app/modules/wage/schemas.py
from datetime import date
from typing import Optional

from pydantic import BaseModel


class UserWageCreate(BaseModel):
    user_id: int
    wage: int
    start_date: date
    end_date: Optional[date] = None


class UserWageResponse(UserWageCreate):
    id: int

    class Config:
        orm_mode = True


class DefaultWageCreate(BaseModel):
    year: int
    wage: int


class DefaultWageResponse(DefaultWageCreate):
    id: int

    class Config:
        orm_mode = True
