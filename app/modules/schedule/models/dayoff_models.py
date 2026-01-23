import enum

from sqlalchemy import VARCHAR, Boolean, Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.config import CreatedAtMixin
from app.core.database import Base


class Status(str, enum.Enum):
    pending = "대기"
    approved = "승인"
    rejected = "반려"


# 휴무 신청
class DayOffRequest(CreatedAtMixin, Base):
    __tablename__ = "day_off_request"
    id = Column(Integer, primary_key=True)

    # 신청자
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship(
        "User", foreign_keys=[user_id], back_populates="day_off_requests"
    )

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    reason = Column(VARCHAR(255), nullable=False)
    status = Column(SAEnum(Status), nullable=False, comment="승인 현황")
    is_holiday = Column(Boolean, nullable=False, default=False)

    # 승인자
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    processor = relationship(
        "User", foreign_keys=[processed_by], back_populates="processed_day_off_requests"
    )
