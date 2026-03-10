from pydantic import BaseModel

from app.modules.auth.models import PositionEnum


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    is_system: bool
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    name: str
    position: str
    is_active: bool

    class Config:
        from_attributes = True


class StaffResponse(BaseModel):
    id: int
    name: str
    position: PositionEnum

    class Config:
        from_attributes = True
