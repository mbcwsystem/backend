from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 기본 설정
    MODE: str = "dev"
    APP_NAME: str = "Megabox"

    # DB 설정
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # JWT 설정
    JWT_SECRET_KEY: str = "JWT_SECRET_KEY"
    JWT_ALGORITHM: str = "JWT_ALGORITHM"
    JWT_EXPIRE_MINUTES: int = "JWT_EXPIRE_MINUTES"

    # 슈퍼 관리자 계정
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

    class Config:
        env_file = "envs/.env.dev"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
ADMIN_ROLES = ["점장", "매니저", "바이저"]
