# app/modules/auth/schemas.py
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    is_system : bool
    access_token: str
    token_type: str = "bearer"
