from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
)
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.orm import relationship

from app.core.database import Base


# 스케쥴표
class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="schedules")
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    # ISO 주차(쿼리 최적화용, 선택적)
    week_number = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)


# 주차별 근무 요약
class WeeklySchedule(Base):
    __tablename__ = "weekly_schedule"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    year = Column(Integer, nullable=False)
    week_number = Column(Integer, nullable=False)
    total_work_hours = Column(DECIMAL(5, 2), default=0)
