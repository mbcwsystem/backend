from datetime import datetime

from pydantic import BaseModel


class ScheduleCreateRequest(BaseModel):
    """
    스케줄 생성
    """

    start_date: datetime
    end_date: datetime

    target_id: int
    week_number: int
    year: int
    month: int


class ScheduleCreateResponse(BaseModel):
    """
    스케줄 생성 응답
    """

    id: int
    user_id: int
    target_id: int
    start_date: datetime
    end_date: datetime
    week_number: int
    year: int
    month: int

    class Config:
        from_attributes = True


class ScheduleResponse(BaseModel):
    """
    스케줄 상세 조회 응답
    """

    id: int
    user_id: int
    user_name: str
    start_date: datetime
    end_date: datetime
    week_number: int
    year: int
    month: int | None  # 월 스냅샷 (표시용)

    class Config:
        from_attributes = True


class ScheduleUpdateRequest(BaseModel):
    """
    스케줄 수정
    """

    start_date: datetime | None = None
    end_date: datetime | None = None
    week_number: int | None = None
    year: int | None = None
    month: int | None = None

    class Config:
        from_attributes = True
