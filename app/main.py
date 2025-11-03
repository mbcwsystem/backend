from fastapi import FastAPI
from sqlalchemy.orm import configure_mappers

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.routers import api_router
from app.modules.auth.models import GenderEnum, PositionEnum, User
from app.modules.auth.services import hash_password

configure_mappers()
app = FastAPI()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter_by(username=settings.ADMIN_USERNAME).first()
        if not admin:
            admin = User(
                username=settings.ADMIN_USERNAME,
                password=hash_password(settings.ADMIN_PASSWORD),
                name=settings.ADMIN_NAME,
                position=PositionEnum.manager,
                gender=GenderEnum.male,
                email=settings.ADMIN_EMAIL,
                is_active=True,
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


app.include_router(api_router, prefix="/api")
