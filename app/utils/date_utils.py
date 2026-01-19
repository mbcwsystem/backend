from calendar import monthrange
from datetime import date


def get_iso_week_range(iso_year: int, iso_week: int) -> tuple[date, date]:
    """
    ISO year + week → (week_start_date, week_end_date)
    월요일 시작 / 일요일 종료
    """
    week_start = date.fromisocalendar(iso_year, iso_week, 1)
    week_end = date.fromisocalendar(iso_year, iso_week, 7)
    return week_start, week_end


def get_month_range(target_date: date) -> tuple[date, date]:
    """
    주어진 날짜가 속한 달의 시작일과 마지막 날짜를 반환한다.

    - 휴무 신청 월별 제한 정책 계산용
    - 윤년 및 월별 일수 차이를 자동으로 처리한다.
    """

    year = target_date.year
    month = target_date.month

    return (
        date(year, month, 1),
        date(year, month, monthrange(year, month)[1]),
    )
