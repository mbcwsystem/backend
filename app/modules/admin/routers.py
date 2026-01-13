import os
import requests  # type: ignore
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session


from app.core.database import get_db
from app.core.security import get_current_admin
from app.modules.admin.schemas import InsuranceRateResponse, InsuranceRateCreate
from app.modules.admin.models import InsuranceRate

from . import schemas, services, models
from dotenv import load_dotenv


router = APIRouter()  # prefix는 core/routers.py에서 "/admin"으로 붙여줌
load_dotenv()

HOLIDAY_API_KEY = os.getenv("HOLIDAY_API_KEY")

if not HOLIDAY_API_KEY:
    raise RuntimeError("HOLIDAY_API_KEY is not set")


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


@router.post("/holidays", status_code=status.HTTP_201_CREATED)
def sync_holidays(
    year: int,
    db: Session = Depends(get_db),
):
    url = (
        "https://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo"
    )

    params = {
        "serviceKey": HOLIDAY_API_KEY,
        "solYear": year,
        "_type": "json",
        "numOfRows": 100,
    }

    try:
        res = requests.get(url, params=params, timeout=20)
        res.raise_for_status()
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="공휴일 API 호출 실패")

    body = res.json()["response"]["body"]
    items = body.get("items")

    if not items:
        return {"year": year, "saved": 0}

    items = items["item"]
    saved = 0

    for item in items:
        ymd = str(item["locdate"])  # e.g. 20250505
        holiday_date = date(
            int(ymd[:4]),
            int(ymd[4:6]),
            int(ymd[6:]),
        )
        label = item["dateName"]

        holiday = models.Holiday(
            date=holiday_date,
            label=label,
        )

        try:
            with db.begin_nested():
                db.add(holiday)
            saved += 1
        except IntegrityError:
            continue

    db.commit()

    return {
        "year": year,
        "saved": saved,
    }


@router.get(
    "/holidays",
    response_model=list[schemas.HolidayOut],
)
def list_holidays(
    year: int,
    db: Session = Depends(get_db),
):
    start = date(year, 1, 1)
    end = date(year, 12, 31)

    return (
        db.query(models.Holiday)
        .filter(models.Holiday.date.between(start, end))
        .order_by(models.Holiday.date)
        .all()
    )


@router.put(
    "/holidays/{holiday_id}",
    response_model=schemas.HolidayOut,
)
def update_holiday(
    holiday_id: int,
    payload: schemas.HolidayUpdate,
    db: Session = Depends(get_db),
):
    holiday = db.query(models.Holiday).get(holiday_id)
    if not holiday:
        raise HTTPException(status_code=404, detail="공휴일 없음")

    if payload.date is not None:
        holiday.date = payload.date
    if payload.label is not None:
        holiday.label = payload.label

    db.commit()
    db.refresh(holiday)
    return holiday


@router.delete(
    "/holidays/{holiday_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_holiday(
    holiday_id: int,
    db: Session = Depends(get_db),
):
    holiday = db.query(models.Holiday).get(holiday_id)
    if not holiday:
        raise HTTPException(status_code=404, detail="공휴일 없음")

    db.delete(holiday)
    db.commit()

@router.post(
    "/insurance-rates",
    response_model=InsuranceRateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_insurance_rate(
    payload: InsuranceRateCreate,
    db: Session = Depends(get_db),
):
    exists = (
        db.query(InsuranceRate)
        .filter(InsuranceRate.year == payload.year)
        .first()
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Insurance rate for this year already exists",
        )

    rate = InsuranceRate(**payload.dict())
    db.add(rate)
    db.commit()
    db.refresh(rate)

    return rate

@router.get(
    "/insurance-rates/{year}",
    response_model=InsuranceRateResponse,
)
def get_insurance_rate(
    year: int,
    db: Session = Depends(get_db),
):
    rate = (
        db.query(InsuranceRate)
        .filter(InsuranceRate.year == year)
        .first()
    )
    if not rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance rate not found",
        )

    return rate

@router.get(
    "/insurance-rates",
    response_model=list[InsuranceRateResponse],
)
def list_insurance_rates(db: Session = Depends(get_db)):
    return (
        db.query(InsuranceRate)
        .order_by(InsuranceRate.year.desc())
        .all()
    )

@router.put(
    "/insurance-rates/{year}",
    response_model=InsuranceRateResponse,
)
def update_insurance_rate_full(
    year: int,
    payload: InsuranceRateCreate,
    db: Session = Depends(get_db),
):
    rate = (
        db.query(InsuranceRate)
        .filter(InsuranceRate.year == year)
        .first()
    )
    if not rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance rate not found",
        )

    for field, value in payload.dict().items():
        setattr(rate, field, value)

    db.commit()
    db.refresh(rate)

    return rate

@router.delete(
    "/insurance-rates/{year}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_insurance_rate(
    year: int,
    db: Session = Depends(get_db),
):
    rate = (
        db.query(InsuranceRate)
        .filter(InsuranceRate.year == year)
        .first()
    )
    if not rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance rate not found",
        )

    db.delete(rate)
    db.commit()