from sqlalchemy import Column, Date, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserWage(Base):  # 유저별 시급
    __tablename__ = "user_wage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    wage = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

    user = relationship("User", backref="user_wage")


class DefaultWage(Base):  # 연도별 최저시급
    __tablename__ = "default_wage"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, unique=True)
    wage = Column(Integer, nullable=False)
