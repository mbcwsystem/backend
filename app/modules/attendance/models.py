from sqlalchemy import Column, Date, ForeignKey, Integer, Time, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("user_id", "work_date", name="uq_user_workdate"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    work_date = Column(Date, nullable=False)

    check_in = Column(Time, nullable=True)
    break_start = Column(Time, nullable=True)
    break_end = Column(Time, nullable=True)
    check_out = Column(Time, nullable=True)

    total_work_minutes = Column(Integer, default=0)
    total_break_minutes = Column(Integer, default=0)

    user = relationship("User", back_populates="attendances")
