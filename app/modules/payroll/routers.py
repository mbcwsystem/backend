from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.auth.models import User
from app.modules.payroll import models, schemas
from app.utils.permission_utils import RoleChecker

router = APIRouter(prefix="/api/payroll", tags=["Payroll"])


@router.get("/", response_model=list[schemas.PayrollResponse])
def get_payroll_list(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if RoleChecker.is_admin(current_user.position):
        payrolls = db.query(models.Payroll).all()
    else:
        payrolls = (
            db.query(models.Payroll)
            .filter(models.Payroll.user_id == current_user.id)
            .all()
        )

    if not payrolls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="급여 데이터가 없습니다."
        )
    return payrolls