from datetime import date
from typing import Optional

from pydantic import BaseModel, field_serializer


class PayrollResponse(BaseModel):
    """
    급여 리포트 / 명세서 통합
    - 전체 조회 (년, 월 필터)
    - 단일/다건 조회 공용
    """

    # 기본 / 인적 정보
    name: Optional[str] = None  # 이름
    position: Optional[str] = None  # 직급
    wage: Optional[int] = None  # 시급
    rrn: Optional[str] = None  # 주민등록번호
    join_date: Optional[date] = None  # 입사일
    resign_date: Optional[date] = None  # 퇴사예정일
    last_work_day: Optional[date] = None  # 마지막 근로일

    bank_name: Optional[str] = None  # 은행
    bank_account: Optional[str] = None  # 계좌번호
    email: Optional[str] = None  # 이메일

    # 근무 요약
    total_work_days: Optional[int] = None  # 근무일수
    total_work_hours: Optional[float] = None  # 총 근무시간
    avg_daily_hours: Optional[float] = None  # 일 평균시간

    # 근무 시간
    day_hours: Optional[float] = None  # 주간 근무시간
    night_hours: Optional[float] = None  # 야간 근무시간
    weekly_allowance_hours: Optional[float] = None  # 주휴시간
    annual_leave_hours: Optional[float] = None  # 연차시간
    holiday_hours: Optional[float] = None  # 공휴일 근무시간

    # 급여
    day_wage: Optional[int] = None  # 주간급여
    night_wage: Optional[int] = None  # 야간급여
    weekly_allowance_pay: Optional[int] = None  # 주휴수당
    annual_leave_pay: Optional[int] = None  # 연차수당
    holiday_pay: Optional[int] = None  # 공휴일 근무수당

    gross_pay: Optional[int] = None  # 급여총액

    # 공제
    insurance_health: Optional[int] = None  # 건강보험
    insurance_care: Optional[int] = None  # 요양보험
    insurance_employment: Optional[int] = None  # 고용보험
    insurance_pension: Optional[int] = None  # 국민연금

    total_deduction: Optional[int] = None  # 공제계
    net_pay: Optional[int] = None  # 지급액

    @field_serializer(
        "total_work_hours",
        "avg_daily_hours",
        "day_hours",
        "night_hours",
        "weekly_allowance_hours",
        "annual_leave_hours",
        "holiday_hours",
        when_used="json",
    )
    def round_two_decimal(self, value):
        if value is None:
            return None
        return round(value, 2)


class WeeklyAllowanceResponse(BaseModel):
    user_id: int
    iso_year: int
    iso_week: int

    week_start_date: date
    week_end_date: date

    allowance_hours: float

    model_config = {"from_attributes": True}


class PayrollPayResponse(BaseModel):
    """
    단일 사용자 급여 금액 요약 Response
    - 본인급여 조회
    - 근무시간 상세 없음
    """

    # 기본 식별 정보
    name: Optional[str] = None  # 이름
    position: Optional[str] = None  # 직급
    birth_date: Optional[date] = None  # 생년월일
    pay_date: Optional[date] = None  # 지급일

    # 급여 항목
    day_wage: Optional[int] = None  # 주간급여
    night_wage: Optional[int] = None  # 야간근무수당
    weekly_allowance_pay: Optional[int] = None  # 주휴수당
    annual_leave_pay: Optional[int] = None  # 연차수당
    holiday_pay: Optional[int] = None  # 법정공휴일수당
    # extra_pay: Optional[int] = None  # 기타수당

    gross_pay: Optional[int] = None  # 급여총액

    # 공제
    insurance_health: Optional[int] = None  # 건강보험
    insurance_care: Optional[int] = None  # 장기요양보험
    insurance_employment: Optional[int] = None  # 고용보험
    insurance_pension: Optional[int] = None  # 국민연금

    total_deduction: Optional[int] = None  # 공제총액

    # 실지급액
    net_pay: Optional[int] = None  # 실지급액


class PayrollPayDateCreate(BaseModel):
    year: int
    month: int
    pay_date: date


class PayrollPayDateUpdate(BaseModel):
    pay_date: date


class PayrollPayDateResponse(BaseModel):
    id: int
    year: int
    month: int
    pay_date: date

    model_config = {"from_attributes": True}
