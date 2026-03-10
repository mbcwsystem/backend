import os
import time
from datetime import datetime, timedelta, timezone
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings
from sqlalchemy import Column, DateTime

os.environ["TZ"] = "Asia/Seoul"

try:
    time.tzset()
except AttributeError:
    pass

KST = timezone(timedelta(hours=9))


def now_kst() -> datetime:
    return datetime.now(KST)


class TimeStampedMixin:
    created_at = Column(
        DateTime, nullable=False, default=now_kst, comment="생성 시각(KST)"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=now_kst,
        onupdate=now_kst,
        comment="수정 시각(KST)",
    )


class CreatedAtMixin:
    created_at = Column(
        DateTime, nullable=False, default=now_kst, comment="생성 시각(KST)"
    )


class Settings(BaseSettings):
    MODE: str = os.getenv("MODE", "dev")
    APP_NAME: str = "Megabox"
    TIMEZONE: str = "Asia/Seoul"

    # Database configs
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # JWT configs
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_EXPIRE_MINUTES: int
    JWT_EXPIRE_DAYS: int

    # Admin configs
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    ADMIN_NAME: str
    ADMIN_EMAIL: str

    # Holiday config
    HOLIDAY_API_KEY: str

    # Ssn
    SSN_SECRET_KEY: str

    # Cors
    CORS_ORIGINS: List[str] = []

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = f"envs/.env.{os.getenv('MODE', 'dev')}"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v


settings = Settings()
