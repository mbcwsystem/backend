import enum

from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime

from app.core.database import Base

class Status(str, enum.Enum):
    pending = "대기"
    approved = "승인"
    rejected = "반려"


class ShiftChangeType(str, enum.Enum):
    shift = "교대"
    replacement = "대타"



class ShiftRequest(Base):
    __tablename__ = "shifts_request"

    id = Column(Integer, primary_key=True, autoincrement=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("schedule.id"), nullable=False)
    type = Column(Enum(ShiftChangeType), nullable=False, comment="교대, 대타 타입")
    status = Column(Enum(Status), nullable=False, comment="승인 현황")
    created_at = Column(DateTime, nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=False)
