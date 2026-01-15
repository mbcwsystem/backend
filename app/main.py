from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import configure_mappers
from datetime import date
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.routers import api_router
from app.modules.auth.models import GenderEnum, PositionEnum, User
from app.modules.auth.services import hash_password

configure_mappers()
app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://mbansan.iptime.org",
    "http://mbansan.iptime.org:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 테스트코드
templates = Jinja2Templates(directory="app/templates")
# 테스트코드
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", tags=["홈페이지"])
def index(request: Request):
    return templates.TemplateResponse("login_signup.html", {"request": request})


@app.get("/main", response_class=HTMLResponse, tags=["홈페이지"])
def render_main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@app.get("/schedule", response_class=HTMLResponse, tags=["홈페이지"])
def render_schedule_page(request: Request):
    return templates.TemplateResponse("schedule.html", {"request": request})


@app.get("/community", response_class=HTMLResponse, tags=["홈페이지"])
def render_community_page(request: Request):
    return templates.TemplateResponse("community.html", {"request": request})


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        admin = db.query(User).filter_by(
            username=settings.ADMIN_USERNAME
        ).first()

        if not admin:

            admin = User(
                username=settings.ADMIN_USERNAME,
                password=hash_password(settings.ADMIN_PASSWORD),
                birth_date=date(1998,2,4),
                name=settings.ADMIN_NAME,
                position=PositionEnum.manager,
                gender=GenderEnum.male,
                email=settings.ADMIN_EMAIL,
                is_active=True,
            )
            db.add(admin)

        test_users = [
            {
                "username": "system",
                "password": "system",
                "name": "시스템",
                "position": PositionEnum.system,
                "gender": GenderEnum.male,
                "email": "system@test.com",
            },
            {
                "username": "user",
                "password": "user",
                "name": "일반유저",
                "position": PositionEnum.crew,
                "gender": GenderEnum.male,
                "email": "user@test.com",
            },
            {
                "username": "crew",
                "password": "crew",
                "name": "크루",
                "position": PositionEnum.crew,
                "gender": GenderEnum.female,
                "email": "crew@test.com",
            },
        ]

        for u in test_users:
            exists = db.query(User).filter_by(username=u["username"]).first()
            if not exists:
                db.add(
                    User(
                        username=u["username"],
                        password=hash_password(u["password"]),
                        birth_date=date(1998,2,4),
                        name=u["name"],
                        position=u["position"],
                        gender=u["gender"],
                        email=u["email"],
                        is_active=True,
                    )
                )

        db.commit()
    finally:
        db.close()


app.include_router(api_router, prefix="/api")
