from datetime import datetime

from pydantic import BaseModel


class ScheduleCreateRequest(BaseModel):
    """
    스케줄 생성
    """

    start_date: datetime
    end_date: datetime

    week_number: int
    year: int
    month: int


class ScheduleCreateResponse(BaseModel):
    """
    스케줄 생성 응답
    """

    id: int
    user_id: int
    start_date: datetime
    end_date: datetime
    week_number: int
    year: int
    month: int

    class Config:
        orm_mode = True
