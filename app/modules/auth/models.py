from __future__ import annotations

import enum

from sqlalchemy import JSON, Boolean, Column, Date, Enum, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class PositionEnum(str, enum.Enum):
    manager = "점장"
    assistant_manager = "매니저"
    advisor = "바이저"
    leader = "리더"
    crew = "크루"
    cleaner = "미화"
    system = "시스템"


class GenderEnum(str, enum.Enum):
    male = "남"
    female = "여"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, comment="로그인 ID")
    password = Column(String(255), nullable=False, comment="비밀번호(해시 저장)")
    name = Column(String(50), nullable=False, comment="이름")
    position = Column(Enum(PositionEnum), nullable=False, comment="직급")
    gender = Column(Enum(GenderEnum), nullable=True, comment="성별")
    ssn = Column(String(20), nullable=True, comment="주민등록번호(암호화/마스킹)")
    phone = Column(String(20), nullable=True, comment="휴대폰번호")
    email = Column(String(100), nullable=True, comment="이메일")
    bank_name = Column(String(50), nullable=True, comment="은행명")
    account_number = Column(String(50), nullable=True, comment="계좌번호")
    hire_date = Column(Date, nullable=True, comment="입사일")
    retire_date = Column(Date, nullable=True, comment="퇴사일")
    unavailable_days = Column(JSON, nullable=True, comment="고정 불가 요일 리스트")
    health_cert_expire = Column(Date, nullable=True, comment="보건증 만료일")
    is_active = Column(Boolean, default=True, comment="재직 상태")

    # 문자열로 충분. 이 라인이 매퍼 구성 시점에 Payroll을 필요로 함
    attendances = relationship(
        "Attendance", back_populates="user", cascade="all, delete"
    )  # 출퇴근
    payrolls = relationship(
        "Payroll", back_populates="user", cascade="all, delete"
    )  # 급여
    user_wages = relationship(
        "UserWage", back_populates="user", cascade="all, delete"
    )  # 개별 시급

    def __repr__(self):
        return f"<User(username={self.username}, position={self.position})>"
