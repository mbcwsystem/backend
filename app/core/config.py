import os
import time
from datetime import timezone, timedelta, datetime
from pydantic_settings import BaseSettings

os.environ["TZ"] = "Asia/Seoul"

try:
    time.tzset()
except AttributeError:
    pass

KST = timezone(timedelta(hours=9))

class Settings(BaseSettings):
    MODE: str = os.getenv("MODE", "dev")
    APP_NAME: str = "Megabox"
    TIMEZONE: str = "Asia/Seoul"

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_EXPIRE_MINUTES: int

    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    ADMIN_NAME: str
    ADMIN_EMAIL: str

    @property
    def DATABASE_URL(self):
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def now_kst(self) -> datetime:
        return datetime.now(KST)

    class Config:
        env_file = f"envs/.env.{os.getenv('MODE', 'dev')}"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
ADMIN_ROLES = ["점장", "매니저", "바이저"]