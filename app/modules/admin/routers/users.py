from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin
from app.modules.admin import schemas, services

router = APIRouter(tags=["유저관리"])


@router.post(
    "/users/create",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="유저 생성",
)
def create_user(
    payload: schemas.UserCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    try:
        user = services.create_user(db, payload)
        db.commit()
        db.refresh(user)
        return user
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="DB error")


@router.get(
    "/users",
    response_model=schemas.PaginatedUsers,
    summary="유저 조회",
)
def list_users(
    q: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    total, items = services.list_users(db, q, limit, offset)
    return {"total": total, "items": items}


@router.get(
    "/users/{memberId}",
    response_model=schemas.UserDetailOut,
    summary="유저 단일조회",
)
def get_user_detail(
    memberId: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    try:
        return services.get_user_detail(db, memberId)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch(
    "/users/{memberId}",
    response_model=schemas.UserOut,
    summary="유저 수정",
)
def update_user(
    memberId: int = Path(..., ge=1),
    payload: schemas.UserUpdate = ...,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    try:
        user = services.update_user(db, memberId, payload)
        db.commit()
        return user
    except LookupError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/users/{memberId}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="유저 삭제",
)
def delete_user(
    memberId: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    try:
        services.delete_user(db, memberId)
        db.commit()
    except LookupError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
