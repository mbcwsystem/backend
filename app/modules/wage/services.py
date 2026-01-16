import re
from datetime import date

import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.wage.models import DefaultWage, UserWage


def _fetch_minimum_wage_table() -> dict[int, int]:
    """
    최저임금위원회 사이트에서
    {연도: 시간급} 딕셔너리로 반환
    """
    try:
        res = requests.get(
            "https://www.minimumwage.go.kr/minWage/policy/decisionMain.do", timeout=10
        )
        res.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(502, "최저임금 사이트 호출 실패") from e

    soup = BeautifulSoup(res.text, "html.parser")

    table = soup.select_one("table.table-board tbody")
    if not table:
        raise HTTPException(500, "최저임금 테이블 구조 변경됨")

    result: dict[int, int] = {}

    for row in table.select("tr"):
        cols = row.select("td")
        if len(cols) < 2:
            continue

        raw_year = cols[0].get_text(strip=True)

        match = re.search(r"'(\d{2})\.01\.01", raw_year)
        if not match:
            continue

        year = 2000 + int(match.group(1))
        if year > date.today().year + 10:
            continue

        hourly_text = cols[1].get_text(strip=True)
        if not re.match(r"^[\d,]+$", hourly_text):
            continue

        hourly = int(hourly_text.replace(",", ""))

        result[year] = hourly

    if not result:
        raise HTTPException(404, "최저임금 데이터 파싱 실패")

    return result


def fetch_all_minimum_wages() -> dict[int, int]:
    """
    전체 연도 최저임금 반환
    예: {2026: 10320, 2025: 10030, ...}
    """
    return _fetch_minimum_wage_table()


def fetch_minimum_wage_by_year(year: int) -> int:
    """
    특정 연도 최저임금 조회
    """
    data = _fetch_minimum_wage_table()

    if year not in data:
        raise HTTPException(
            status_code=404,
            detail=f"{year}년 최저임금 데이터가 없습니다.",
        )

    return data[year]


def get_applicable_wage(user_id: int, work_date: date, db: Session):
    user_wage = (
        db.query(UserWage)
        .filter(
            UserWage.user_id == user_id,
            UserWage.start_date <= work_date,
            (UserWage.end_date.is_(None)) | (UserWage.end_date >= work_date),
        )
        .order_by(UserWage.start_date.desc())
        .first()
    )
    if user_wage:
        return user_wage.wage

    year = work_date.year
    default_wage = db.query(DefaultWage).filter_by(year=year).first()
    if default_wage:
        return default_wage.wage

    return -1
