from datetime import date, time
from typing import Optional

from pydantic import BaseModel, field_serializer


class AttendanceBase(BaseModel):
    work_date: Optional[date] = None
    check_in: Optional[time] = None
    break_start: Optional[time] = None
    break_end: Optional[time] = None
    check_out: Optional[time] = None
    total_work_minutes: Optional[int] = 0
    total_break_minutes: Optional[int] = 0


class AttendanceCreate(BaseModel):
    pass


class AttendanceResponse(AttendanceBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

    @field_serializer("check_in", "break_start", "break_end", "check_out")
    def serialize_time(self, value: Optional[time], _info):
        return value.strftime("%H:%M:%S") if value else None
