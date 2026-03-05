# app/modules/admin/services.py
from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.admin import schemas
from app.modules.admin.models import Holiday, InsuranceRate
from app.modules.admin.schemas import InsuranceRateCreate, InsuranceRateUpdate
from app.modules.auth.models import User
from app.modules.auth.services import decrypt_ssn, encrypt_ssn, hash_password


# --------- Users ----------
def create_user(db: Session, data: schemas.UserCreate) -> User:
    user = User(
        username=data.username,
        password=hash_password(data.password),
        name=data.name,
        position=data.position,
        gender=data.gender,
        birth_date=data.birth_date,
        ssn=encrypt_ssn(data.ssn) if data.ssn else None,
        phone=data.phone,
        email=str(data.email) if data.email else None,
        bank_name=data.bank_name,
        account_number=data.account_number,
        hire_date=data.hire_date,
        retire_date=data.retire_date,
        unavailable_days=data.unavailable_days,
        health_cert_expire=data.health_cert_expire,
        is_active=data.is_active,
    )

    db.add(user)

    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise ValueError("이미 사용 중인 username 입니다.")

    return user


def get_user_detail(db: Session, memberId: int) -> User:
    user = db.get(User, memberId)
    if not user:
        raise LookupError("사용자를 찾을 수 없습니다.")

    # 관리자만 복호화
    if user.ssn:
        user.ssn = decrypt_ssn(user.ssn)

    return user


def list_users(
    db: Session, q: Optional[str], limit: int, offset: int
) -> Tuple[int, List[User]]:
    stmt = select(User)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            (User.name.ilike(like))
            | (User.username.ilike(like))
            | (User.email.ilike(like))
        )

    # total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    # items
    items = (
        db.execute(stmt.order_by(User.id.desc()).limit(limit).offset(offset))
        .scalars()
        .all()
    )
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


def list_holidays(
    db: Session, start: Optional[date], end: Optional[date]
) -> List[Holiday]:
    stmt = select(Holiday)
    if start:
        stmt = stmt.where(Holiday.date >= start)
    if end:
        stmt = stmt.where(Holiday.date <= end)
    return db.execute(stmt.order_by(Holiday.date.desc())).scalars().all()


def update_holiday(
    db: Session, holiday_id: int, data: schemas.HolidayUpdate
) -> Holiday:
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


def get_insurance_rates(db: Session) -> list[InsuranceRate]:
    stmt = select(InsuranceRate).order_by(InsuranceRate.year.desc())
    return db.execute(stmt).scalars().all()


def get_insurance_rate_by_year(
    db: Session,
    year: int,
) -> InsuranceRate | None:
    stmt = select(InsuranceRate).where(InsuranceRate.year == year)
    return db.execute(stmt).scalars().first()


def create_insurance_rate(
    db: Session,
    payload: InsuranceRateCreate,
) -> InsuranceRate:
    rate = InsuranceRate(
        year=payload.year,
        national_pension_rate=payload.national_pension_rate,
        health_insurance_rate=payload.health_insurance_rate,
        long_term_care_rate=payload.long_term_care_rate,
        employment_insurance_rate=payload.employment_insurance_rate,
    )
    db.add(rate)
    db.commit()
    db.refresh(rate)
    return rate


def update_insurance_rate_full(
    db: Session,
    rate: InsuranceRate,
    payload: InsuranceRateCreate,
) -> InsuranceRate:
    rate.national_pension_rate = payload.national_pension_rate
    rate.health_insurance_rate = payload.health_insurance_rate
    rate.long_term_care_rate = payload.long_term_care_rate
    rate.employment_insurance_rate = payload.employment_insurance_rate

    db.commit()
    db.refresh(rate)
    return rate


def update_insurance_rate_partial(
    db: Session,
    rate: InsuranceRate,
    payload: InsuranceRateUpdate,
) -> InsuranceRate:
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(rate, field, value)

    db.commit()
    db.refresh(rate)
    return


def delete_insurance_rate(
    db: Session,
    rate: InsuranceRate,
) -> None:
    db.delete(rate)
    db.commit()
