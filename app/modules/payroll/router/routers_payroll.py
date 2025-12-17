from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.utils.permission_utils import is_admin, is_system
from app.modules.payroll.schemas import PayrollResponse
from app.core.security import get_current_user

router = APIRouter(
    tags=["Payroll"],
)


@router.get("/", response_model=List[PayrollResponse])
def get_payrolls(
    year: int = Query(..., description="연도 (필수)"),
    month: Optional[int] = Query(None, ge=1, le=12, description="월 (선택)"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    급여 조회
    - system 계정: 차단
    - admin: 전체 조회
    - 일반 사용자: 개인 조회
    """

    # 시스템잘가
    if is_system(user):
        raise HTTPException(
            status_code=403,
            detail="조회할 수 없는 계정입니다.",
        )

    # 관리자여부
    if is_admin(user):
        return []  # 서비스 작성아직안함 (전체 조회예정)

    return []  # 서비스 작성아직안함 (개인 알죠?)
