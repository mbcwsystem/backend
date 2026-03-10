from datetime import datetime

from pydantic import BaseModel

from app.utils.day_off import DayOffStatus


class DayOffApplyRequest(BaseModel):
    """
    휴무 신청
    """

    start_date: datetime
    end_date: datetime
    reason: str
    is_holiday: bool = False

    class Config:
        from_attributes = True


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
        from_attributes = True


class DayOffDecisionRequest(BaseModel):
    """
    휴무 승인 및 거절
    """

    decision: DayOffStatus


class DayOffResponse(BaseModel):
    """
    휴무 조회 응답
    """

    id: int
    user_id: int
    start_date: datetime
    end_date: datetime
    reason: str

    class Config:
        from_attributes = True
