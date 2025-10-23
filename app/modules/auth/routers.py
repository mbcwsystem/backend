from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user  # /auth/me 용
from . import schemas, services

router = APIRouter()

@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = services.get_user_by_username(db, payload.username)
    if not user or not services.verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = services.create_access_token(
        sub=str(user.id),
        username=user.username,
        is_admin=services.is_admin_position(user.position),
    )
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def me(current = Depends(get_current_user)):
    # 가볍게 현재 로그인 사용자 확인용
    return {
        "id": current.id,
        "username": current.username,
        "name": current.name,
        "position": str(current.position.value),
        "is_active": current.is_active,
    }