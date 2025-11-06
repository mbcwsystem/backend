from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class WeeklyPayrollBase(BaseModel):
    user_id: int
    year: int
    month: int
    total_work_hours: Decimal


class WeeklyPayrollResponse(WeeklyPayrollBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class PayrollBase(BaseModel):
    user_id: int
    year: int
    month: int
    hourly_wage: int
    total_hours: Decimal
    weekly_hours: Decimal
    night_hours: Decimal
    holiday_hours: Decimal
    break_hours: Decimal
    total_salary: int
    net_salary: int


class PayrollResponse(PayrollBase):
    id: int
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)