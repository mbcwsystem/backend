from datetime import datetime

from pydantic import BaseModel


class DayOffApplyRequest(BaseModel):
    """
    휴무 신청
    """

    start_date: datetime
    end_date: datetime
    reason: str
    is_holiday: bool = False

    class Config:
        orm_mode = True


class DayOffApplyResponse(BaseModel):
    """
    휴무 신청 응답
    """

    id: int
    user_id: int

    start_date: datetime
    end_date: datetime
    reason: str

    class Config:
        orm_mode = True
