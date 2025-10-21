from fastapi import FastAPI
from app.core.routers import api_router
app = FastAPI()

app.include_router(api_router)