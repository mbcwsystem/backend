from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI 의존성으로 쓸 DB 세션 팩토리
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()