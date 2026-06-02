from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class SalarySlipCreate(BaseModel):
    employee_id: int
    month: date
    basic_salary: Decimal = Field(ge=0)
    hra: Decimal = Field(ge=0, default=0)
    bonus: Decimal = Field(ge=0, default=0)
    deductions: Decimal = Field(ge=0, default=0)


class SalarySlipUpdate(BaseModel):
    basic_salary: Decimal | None = None
    hra: Decimal | None = None
    bonus: Decimal | None = None
    deductions: Decimal | None = None


class SalaryMarkPaid(BaseModel):
    payment_date: date | None = None
    transaction_id: str | None = None


class SalarySlipResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: str | None = None
    employee_code: str | None = None
    month: date
    basic_salary: Decimal
    hra: Decimal
    bonus: Decimal
    deductions: Decimal
    net_salary: Decimal
    status: str
    pdf_path: str | None
    paid_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class SalaryListResponse(BaseModel):
    items: list[SalarySlipResponse]
    total: int
    page: int
    page_size: int

