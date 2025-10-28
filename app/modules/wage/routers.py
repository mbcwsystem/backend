from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.wage import models, schemas

router = APIRouter(tags=["Wage"])
admin_router = APIRouter(tags=["Admin"])


@router.post("/user", response_model=schemas.UserWageResponse)  # 유저 전용 시급 설정
def create_user_wage(data: schemas.UserWageCreate, db: Session = Depends(get_db)):
    record = models.UserWage(**data.dict())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get(
    "/user/{user_id}", response_model=list[schemas.UserWageResponse]
)  # 유저 전용 시급 조회
def get_user_wage_list(user_id: int, db: Session = Depends(get_db)):
    records = db.query(models.UserWage).filter(models.UserWage.user_id == user_id).all()
    return records


@admin_router.post(
    "/", response_model=schemas.DefaultWageResponse
)  # 연도 최저임금 설정
def create_default_wage(data: schemas.DefaultWageCreate, db: Session = Depends(get_db)):
    record = models.DefaultWage(**data.dict())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@admin_router.get(
    "/", response_model=list[schemas.DefaultWageResponse]
)  # 연도별 최저임금 조회
def list_default_wages(db: Session = Depends(get_db)):
    return db.query(models.DefaultWage).order_by(models.DefaultWage.year.desc()).all()
