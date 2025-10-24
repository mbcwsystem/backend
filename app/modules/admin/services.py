# app/modules/admin/services.py
from typing import Optional, List, Tuple
from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.admin.models import Holiday, InsuranceRate
from app.modules.admin import schemas
from app.modules.auth.services import hash_password  # ← 해시 적용

# --------- Users ----------
def create_user(db: Session, data: schemas.UserCreate) -> User:
    user = User(
        username=data.username,
        password=hash_password(data.password),  # ← 해시 저장
        name=data.name,
        position=data.position,
        gender=data.gender,
        phone=data.phone,
        email=data.email,
        is_active=data.is_active,
    )
    db.add(user)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise ValueError("이미 사용 중인 username 입니다.")
    return user

def list_users(db: Session, q: Optional[str], limit: int, offset: int) -> Tuple[int, List[User]]:
    stmt = select(User)
    if q:
        like = f"%{q}%"
        stmt = stmt.where((User.name.ilike(like)) | (User.username.ilike(like)) | (User.email.ilike(like)))

    # total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    # items
    items = db.execute(stmt.order_by(User.id.desc()).limit(limit).offset(offset)).scalars().all()
    return total, items

def update_user(db: Session, user_id: int, data: schemas.UserUpdate) -> User:
    user = db.get(User, user_id)
    if not user:
        raise LookupError("해당 사용자가 존재하지 않습니다.")

    payload = data.model_dump(exclude_unset=True)
    # 비밀번호 변경을 허용한다면 해시 처리
    if "password" in payload and payload["password"]:
        payload["password"] = hash_password(payload["password"])

    for k, v in payload.items():
        setattr(user, k, v)

    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise ValueError("중복 또는 제약조건 위반입니다.")
    return user

def delete_user(db: Session, user_id: int) -> None:
    user = db.get(User, user_id)
    if not user:
        raise LookupError("해당 사용자가 존재하지 않습니다.")
    db.delete(user)
    # flush/commit은 라우터에서

# --------- Holidays (전사 공휴일) ----------
def create_holiday(db: Session, data: schemas.HolidayCreate) -> Holiday:
    h = Holiday(name=data.name, date=data.date, description=data.description)
    db.add(h)
    db.flush()
    return h

def list_holidays(db: Session, start: Optional[date], end: Optional[date]) -> List[Holiday]:
    stmt = select(Holiday)
    if start:
        stmt = stmt.where(Holiday.date >= start)
    if end:
        stmt = stmt.where(Holiday.date <= end)
    return db.execute(stmt.order_by(Holiday.date.desc())).scalars().all()

def update_holiday(db: Session, holiday_id: int, data: schemas.HolidayUpdate) -> Holiday:
    h = db.get(Holiday, holiday_id)
    if not h:
        raise LookupError("해당 공휴일이 존재하지 않습니다.")
    payload = data.model_dump(exclude_unset=True)
    if not payload:
        raise ValueError("변경할 값이 없습니다.")
    for k, v in payload.items():
        setattr(h, k, v)
    db.flush()
    return h

def delete_holiday(db: Session, holiday_id: int) -> None:
    h = db.get(Holiday, holiday_id)
    if not h:
        raise LookupError("해당 공휴일이 존재하지 않습니다.")
    db.delete(h)

# --------- Insurance Rates (카테고리별 레코드) ----------
def get_insurance_rates(db: Session) -> List[InsuranceRate]:
    stmt = select(InsuranceRate).order_by(InsuranceRate.effective_date.desc(), InsuranceRate.category.asc())
    return db.execute(stmt).scalars().all()

def set_insurance_rate(db: Session, data: schemas.InsuranceRateSet) -> InsuranceRate:
    existing = db.execute(
        select(InsuranceRate).where(
            and_(
                InsuranceRate.category == data.category,
                InsuranceRate.effective_date == data.effective_date,
            )
        )
    ).scalar_one_or_none()

    if existing:
        existing.rate = data.rate
        db.flush()
        return existing

    obj = InsuranceRate(
        category=data.category,
        rate=data.rate,
        effective_date=data.effective_date,
    )
    db.add(obj)
    db.flush()
    return obj