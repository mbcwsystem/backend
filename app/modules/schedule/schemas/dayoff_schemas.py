from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class DayOffStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    canceled = "canceled"


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
