# app/modules/admin/routers.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin

from . import schemas, services

router = APIRouter()  # prefix는 core/routers.py에서 "/admin"으로 붙여줌


# ---- Users ----
@router.post(
    "/users/create", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED
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
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {e.__class__.__name__}")


@router.get("/users", response_model=schemas.PaginatedUsers)
def list_users(
    q: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    total, items = services.list_users(db, q, limit, offset)
    return {"total": total, "items": items}


@router.patch("/users/{memberId}", response_model=schemas.UserOut)
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


@router.delete("/users/{memberId}", status_code=status.HTTP_204_NO_CONTENT)
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


# ---- Holidays (전사 공휴일) ----
@router.post(
    "/holidays", response_model=schemas.HolidayOut, status_code=status.HTTP_201_CREATED
)
def create_holiday(
    payload: schemas.HolidayCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    try:
        obj = services.create_holiday(db, payload)
        db.commit()
        db.refresh(obj)
        return obj
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {e.__class__.__name__}")


@router.get("/holidays", response_model=List[schemas.HolidayOut])
def list_holidays(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    return services.list_holidays(db, start, end)


@router.patch("/holidays/{holidayId}", response_model=schemas.HolidayOut)
def update_holiday(
    holidayId: int = Path(..., ge=1),
    payload: schemas.HolidayUpdate = ...,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    try:
        obj = services.update_holiday(db, holidayId, payload)
        db.commit()
        return obj
    except LookupError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/holidays/{holidayId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holiday(
    holidayId: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    try:
        services.delete_holiday(db, holidayId)
        db.commit()
    except LookupError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))


# ---- Insurance Rates ----
@router.get("/insurance-rates", response_model=List[schemas.InsuranceRateOut])
def get_insurance_rates(
    db: Session = Depends(get_db), _admin=Depends(get_current_admin)
):
    return services.get_insurance_rates(db)


@router.post(
    "/insurance-rates",
    response_model=schemas.InsuranceRateOut,
    status_code=status.HTTP_201_CREATED,
)
def set_insurance_rate(
    payload: schemas.InsuranceRateSet,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    obj = services.set_insurance_rate(db, payload)
    db.commit()
    db.refresh(obj)
    return obj
