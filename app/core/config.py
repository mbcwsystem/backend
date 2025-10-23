from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 기본 설정
    MODE: str = "dev"
    APP_NAME: str = "Megabox Dev API"

    # DB 설정
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # JWT 설정
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_EXPIRE_MINUTES: int

    @property
    def DATABASE_URL(self):
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = "envs/.env.dev"
        extra = "ignore"

settings = Settings()