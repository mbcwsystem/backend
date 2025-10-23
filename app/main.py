from fastapi import FastAPI
from app.core.database import Base, engine
from app.core.routers import api_router
from app.modules import all_models

app = FastAPI()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(api_router, prefix="/api")