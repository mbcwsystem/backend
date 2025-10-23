from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Boolean, Enum,
    ForeignKey, JSON, DECIMAL, Time, Text
)
from app.core.database import Base
import enum


# ===============================
# ENUM 정의
# ===============================
class PositionEnum(str, enum.Enum):
    manager = "점장"
    assistant = "매니저"
    advisor = "바이저"
    leader = "리더"
    crew = "크루"
    cleaner = "미화"
    system = "시스템"


class GenderEnum(str, enum.Enum):
    male = "남"
    female = "여"


class ShiftTypeEnum(str, enum.Enum):
    exchange = "교대"
    substitute = "대타"


class RequestStatusEnum(str, enum.Enum):
    pending = "대기"
    approved = "승인"
    rejected = "반려"


class PostCategoryEnum(str, enum.Enum):
    notice = "notice"
    shift = "shift"
    dayoff = "dayoff"
    free_board = "free_board"


class InsuranceCategoryEnum(str, enum.Enum):
    health = "건강보험"
    care = "요양보험"
    employment = "고용보험"
    pension = "국민연금"


# ===============================
# 🧑 USERS (직원 정보)
# ===============================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)  # 로그인 ID
    password = Column(String(255), nullable=False)  # 해시된 비밀번호
    name = Column(String(50), nullable=False)
    position = Column(Enum(PositionEnum), nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    ssn = Column(String(20))
    phone = Column(String(20))
    email = Column(String(100))
    bank_name = Column(String(50))
    account_number = Column(String(50))
    hire_date = Column(Date)
    retire_date = Column(Date)
    unavailable_days = Column(JSON)
    health_cert_expire = Column(Date)
    is_active = Column(Boolean, default=True)


# ===============================
# ⏰ ATTENDANCE (근무 기록)
# ===============================
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    work_date = Column(Date)
    check_in = Column(Time)
    break_start = Column(Time)
    break_end = Column(Time)
    check_out = Column(Time)
    total_work_minutes = Column(Integer)
    total_break_minutes = Column(Integer)


# ===============================
# 💰 PAYROLL (급여 정보)
# ===============================
class Payroll(Base):
    __tablename__ = "payroll"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    year = Column(Integer)
    month = Column(Integer)
    hourly_wage = Column(Integer)
    total_hours = Column(DECIMAL(5, 2))
    weekly_hours = Column(DECIMAL(5, 2))
    night_hours = Column(DECIMAL(5, 2))
    holiday_hours = Column(DECIMAL(5, 2))
    break_hours = Column(DECIMAL(5, 2))
    total_salary = Column(Integer)
    insurance_health = Column(Integer)
    insurance_employment = Column(Integer)
    insurance_pension = Column(Integer)
    insurance_care = Column(Integer)
    total_deduction = Column(Integer)
    net_salary = Column(Integer)


# ===============================
# 📅 SCHEDULE (근무 스케줄)
# ===============================
class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    week_number = Column(Integer)
    year = Column(Integer)
    month = Column(Integer)
    is_holiday = Column(Boolean, default=False)


# ===============================
# 🔁 SHIFT REQUEST (교대/대타)
# ===============================
class ShiftRequest(Base):
    __tablename__ = "shift_request"

    id = Column(Integer, primary_key=True)
    requester_id = Column(Integer, ForeignKey("users.id"))
    target_id = Column(Integer, ForeignKey("users.id"))
    schedule_id = Column(Integer, ForeignKey("schedule.id"))
    type = Column(Enum(ShiftTypeEnum))
    status = Column(Enum(RequestStatusEnum))
    created_at = Column(DateTime)
    approved_by = Column(Integer, ForeignKey("users.id"))


# ===============================
# 🌴 DAYOFF REQUEST (휴무신청)
# ===============================
class DayOffRequest(Base):
    __tablename__ = "dayoff_request"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    reason = Column(String(255))
    status = Column(Enum(RequestStatusEnum))
    approved_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime)


# ===============================
# 💬 COMMUNITY POST (게시글)
# ===============================
class CommunityPost(Base):
    __tablename__ = "community_post"

    id = Column(Integer, primary_key=True)
    category = Column(Enum(PostCategoryEnum))
    title = Column(String(255))
    content = Column(Text)  # ✅ Text로 변경 완료
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    system_generated = Column(Boolean, default=False)


# ===============================
# 💭 COMMUNITY COMMENT (댓글)
# ===============================
class CommunityComment(Base):
    __tablename__ = "community_comment"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("community_post.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)  # ✅ String → Text로 변경 완료
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


# ===============================
# 📆 HOLIDAY (공휴일)
# ===============================
class Holiday(Base):
    __tablename__ = "holiday"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    date = Column(Date)
    description = Column(String(200))


# ===============================
# 🧾 INSURANCE RATE (보험 요율)
# ===============================
class InsuranceRate(Base):
    __tablename__ = "insurance_rate"

    id = Column(Integer, primary_key=True)
    category = Column(Enum(InsuranceCategoryEnum))
    rate = Column(DECIMAL(6, 4))
    effective_date = Column(Date)