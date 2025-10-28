from pydantic import BaseModel


class PayrollBase(BaseModel):
    year: int
    month: int
    hourly_wage: int


class PayrollResponse(PayrollBase):
    id: int
    total_hours: float
    total_salary: int
    total_deduction: int
    net_salary: int

    class Config:
        orm_mode = True
