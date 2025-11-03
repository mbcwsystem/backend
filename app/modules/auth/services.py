from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.auth.models import PositionEnum, User

pwd_context = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],  # 우선 bcrypt_sha256, 과거 bcrypt도 호환
    default="bcrypt_sha256",
    deprecated=["bcrypt"],  # bcrypt는 점진 폐기
)

# --- password helpers ---
# 신규 직원 생성 시 비밀번호 저장도 패스워드 해시처리(hash_password()) 사용


def hash_password(raw: str) -> str:
    return pwd_context.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)


# --- user helpers ---
def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()


def is_admin_position(pos: PositionEnum) -> bool:
    # 관리자 권한 기준: 점장 or 시스템
    return pos in {PositionEnum.manager, PositionEnum.system}


# --- JWT helpers ---
def create_access_token(*, sub: str, username: str, is_admin: bool) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": sub,
        "username": username,
        "is_admin": is_admin,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return token
