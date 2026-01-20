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

    # 스케줄 대상 사용자 ID
    # - 일반 직원: 본인 ID
    # - 관리자/바이저: 스케줄을 생성/수정할 대상 직원 ID
    target_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="스케줄 대상 사용자 ID (본인 또는 관리자가 지정한 직원)",
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="스케줄을 생성/수정한 사용자 ID",
    )
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
