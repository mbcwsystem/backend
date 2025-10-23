# app/modules/admin/services.py
from typing import Optional, List, Tuple
from sqlalchemy import select, func, update, delete, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.all_models import User, Holiday, InsuranceRate
from . import schemas

# --------- Users ----------
def create_user(db: Session, data: schemas.UserCreate) -> User:
    # TODO: password 해시 적용 필요
    user = User(
        username=data.username,
        password=data.password,
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
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()
    items = db.execute(stmt.order_by(User.id.desc()).limit(limit).offset(offset)).scalars().all()
    return total, items

def update_user(db: Session, user_id: int, data: schemas.UserUpdate) -> User:
    values = {k: v for k, v in data.model_dump(exclude_unset=True).items()}
    if not values:
        raise ValueError("변경할 값이 없습니다.")
    res = db.execute(
        update(User).where(User.id == user_id).values(values).returning(User)
    ).fetchone()
    if not res:
        raise LookupError("해당 사용자가 존재하지 않습니다.")
    return res[0]

def delete_user(db: Session, user_id: int) -> None:
    res = db.execute(delete(User).where(User.id == user_id))
    if res.rowcount == 0:
        raise LookupError("해당 사용자가 존재하지 않습니다.")

# --------- Holidays (전사 공휴일) ----------
def create_holiday(db: Session, data: schemas.HolidayCreate) -> Holiday:
    h = Holiday(name=data.name, date=data.date, description=data.description)
    db.add(h)
    db.flush()
    return h

def list_holidays(db: Session, start: Optional[str], end: Optional[str]) -> List[Holiday]:
    stmt = select(Holiday)
    if start:
        stmt = stmt.where(Holiday.date >= start)
    if end:
        stmt = stmt.where(Holiday.date <= end)
    return db.execute(stmt.order_by(Holiday.date.desc())).scalars().all()

def update_holiday(db: Session, holiday_id: int, data: schemas.HolidayUpdate) -> Holiday:
    values = {k: v for k, v in data.model_dump(exclude_unset=True).items()}
    if not values:
        raise ValueError("변경할 값이 없습니다.")
    res = db.execute(
        update(Holiday).where(Holiday.id == holiday_id).values(values).returning(Holiday)
    ).fetchone()
    if not res:
        raise LookupError("해당 공휴일이 존재하지 않습니다.")
    return res[0]

def delete_holiday(db: Session, holiday_id: int) -> None:
    res = db.execute(delete(Holiday).where(Holiday.id == holiday_id))
    if res.rowcount == 0:
        raise LookupError("해당 공휴일이 존재하지 않습니다.")

# --------- Insurance Rates (카테고리별 레코드) ----------
def get_insurance_rates(db: Session) -> List[InsuranceRate]:
    # 최신 시행일이 위로, 카테고리+시행일 조합 다 보여줌
    stmt = select(InsuranceRate).order_by(InsuranceRate.effective_date.desc(), InsuranceRate.category.asc())
    return db.execute(stmt).scalars().all()

def set_insurance_rate(db: Session, data: schemas.InsuranceRateSet) -> InsuranceRate:
    # 동일 (category, effective_date) 가 있으면 갱신, 없으면 생성 (UPSERT 느낌)
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
    else:
        obj = InsuranceRate(
            category=data.category,
            rate=data.rate,
            effective_date=data.effective_date,
        )
        db.add(obj)
        db.flush()
        return obj