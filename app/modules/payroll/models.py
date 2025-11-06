from sqlalchemy import DECIMAL, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base


class Payroll(Base):
    __tablename__ = "payroll"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    hourly_wage = Column(Integer, nullable=False)
    total_hours = Column(DECIMAL(5, 2), default=0)
    weekly_hours = Column(DECIMAL(5, 2), default=0)
    night_hours = Column(DECIMAL(5, 2), default=0)
    holiday_hours = Column(DECIMAL(5, 2), default=0)
    break_hours = Column(DECIMAL(5, 2), default=0)
    total_salary = Column(Integer, default=0)
    insurance_health = Column(Integer, default=0)
    insurance_employment = Column(Integer, default=0)
    insurance_pension = Column(Integer, default=0)
    insurance_care = Column(Integer, default=0)
    total_deduction = Column(Integer, default=0)
    net_salary = Column(Integer, default=0)

    user = relationship("User", back_populates="payrolls")

class WeeklyPayroll(Base):
    __tablename__ = "weekly_payroll"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    total_work_hours = Column(DECIMAL(5, 2), default=0.0)

    user = relationship("User", back_populates="weekly_payroll")