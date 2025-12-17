from datetime import date


def get_iso_week_range(iso_year: int, iso_week: int) -> tuple[date, date]:
    """
    ISO year + week → (week_start_date, week_end_date)
    월요일 시작 / 일요일 종료
    """
    week_start = date.fromisocalendar(iso_year, iso_week, 1)
    week_end = date.fromisocalendar(iso_year, iso_week, 7)
    return week_start, week_end