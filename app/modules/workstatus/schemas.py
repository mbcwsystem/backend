from datetime import date, time
from typing import Optional

from pydantic import BaseModel


class AttendanceBase(BaseModel):
    work_date: Optional[date] = None
    check_in: Optional[time] = None
    break_start: Optional[time] = None
    break_end: Optional[time] = None
    check_out: Optional[time] = None
    total_work_minutes: Optional[int] = None
    total_break_minutes: Optional[int] = None


class AttendanceCreate(BaseModel):
    pass


class AttendanceResponse(AttendanceBase):
    id: int
    user_id: int
    user_name: Optional[str] = None

    class Config:
        from_attributes = True
