import enum

from sqlalchemy import (
    VARCHAR,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
)
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.orm import relationship

from app.core.database import Base


class Status(str, enum.Enum):
    pending = "대기"
    approved = "승인"
    rejected = "반려"


# 스케쥴표
class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # ISO 주차(쿼리 최적화용, 선택적)
    week_number = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    is_holiday = Column(Boolean, nullable=False)


# 주차별 근무 요약
class WeeklySchedule(Base):
    __tablename__ = "weekly_schedule"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    year = Column(Integer, nullable=False)
    week_number = Column(Integer, nullable=False)
    total_work_hours = Column(DECIMAL(5, 2), default=0)


# 휴무 신청
class DayOffRequest(Base):
    __tablename__ = "day_off_request"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(VARCHAR(255), nullable=False)
    status = Column(Enum(Status), nullable=False, comment="승인 현황")
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)
