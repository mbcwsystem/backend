from typing import List, Optional

from sqlalchemy.orm import Session

from app.modules.payroll.models import Payroll


def get_payrolls(
    *,
    db: Session,
    year: int,
    month: Optional[int] = None,
) -> List[Payroll]:
    """
    급여 내역 조회
    - year는 필수
    - month가 있으면 특정 월, 없으면 해당 연도의 전체 월 조회
    """

    query = db.query(Payroll).filter(Payroll.year == year)

    if month is not None:
        query = query.filter(Payroll.month == month)

    return query.all()
