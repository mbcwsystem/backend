import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.utils.permission_utils import is_system

from . import schemas, services
from .models import RefreshToken

router = APIRouter()


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = services.get_user_by_username(db, payload.username)
    if not user or not services.verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token = services.create_access_token(
        sub=str(user.id),
        username=user.username,
        is_admin=services.is_admin_position(user.position),
    )
    refresh_token, expires_at = services.create_refresh_token(sub=str(user.id))
    db.add(
        RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
        )
    )
    db.commit()

    return {
        "is_system": is_system(user),
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=schemas.UserResponse)
def me(cuurent_user=Depends(get_current_user)):
    return cuurent_user


@router.post("/refresh", response_model=schemas.RefreshResponse)
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(
            refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    db_token = db.query(RefreshToken).filter_by(token=refresh_token).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db_token.user

    new_access_token = services.create_access_token(
        sub=str(user.id),
        username=user.username,
        is_admin=services.is_admin_position(user.position),
    )

    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(
    refresh_token: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    deleted = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == refresh_token,
            RefreshToken.user_id == current_user.id,
        )
        .delete()
    )
    db.commit()

    if not deleted:
        raise HTTPException(status_code=400, detail="Already logged out")

    return {"message": "로그아웃 완료"}
