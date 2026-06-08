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
    da: Decimal = Field(ge=0, default=0)
    conveyance_allowance: Decimal = Field(ge=0, default=0)
    medical_allowance: Decimal = Field(ge=0, default=0)
    internet_allowance: Decimal = Field(ge=0, default=0)
    special_allowance: Decimal = Field(ge=0, default=0)
    incentive: Decimal = Field(ge=0, default=0)
    overtime_pay: Decimal = Field(ge=0, default=0)
    project_bonus: Decimal = Field(ge=0, default=0)
    other_earnings: Decimal = Field(ge=0, default=0)
    pf: Decimal = Field(ge=0, default=0)
    esi: Decimal = Field(ge=0, default=0)
    professional_tax: Decimal = Field(ge=0, default=0)
    tds: Decimal = Field(ge=0, default=0)
    loan_deduction: Decimal = Field(ge=0, default=0)
    advance_salary_recovery: Decimal = Field(ge=0, default=0)
    leave_deduction: Decimal = Field(ge=0, default=0)
    late_attendance_deduction: Decimal = Field(ge=0, default=0)
    penalty_deduction: Decimal = Field(ge=0, default=0)
    other_deductions: Decimal = Field(ge=0, default=0)
    apply_auto_leave_deduction: bool = True


class SalarySlipUpdate(BaseModel):
    basic_salary: Decimal | None = None
    hra: Decimal | None = None
    bonus: Decimal | None = None
    deductions: Decimal | None = None
    da: Decimal | None = None
    conveyance_allowance: Decimal | None = None
    medical_allowance: Decimal | None = None
    internet_allowance: Decimal | None = None
    special_allowance: Decimal | None = None
    incentive: Decimal | None = None
    overtime_pay: Decimal | None = None
    project_bonus: Decimal | None = None
    other_earnings: Decimal | None = None
    pf: Decimal | None = None
    esi: Decimal | None = None
    professional_tax: Decimal | None = None
    tds: Decimal | None = None
    loan_deduction: Decimal | None = None
    advance_salary_recovery: Decimal | None = None
    leave_deduction: Decimal | None = None
    late_attendance_deduction: Decimal | None = None
    penalty_deduction: Decimal | None = None
    other_deductions: Decimal | None = None
    apply_auto_leave_deduction: bool = True


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
    da: Decimal = Decimal("0")
    conveyance_allowance: Decimal = Decimal("0")
    medical_allowance: Decimal = Decimal("0")
    internet_allowance: Decimal = Decimal("0")
    special_allowance: Decimal = Decimal("0")
    incentive: Decimal = Decimal("0")
    overtime_pay: Decimal = Decimal("0")
    project_bonus: Decimal = Decimal("0")
    other_earnings: Decimal = Decimal("0")
    total_earnings: Decimal = Decimal("0")
    pf: Decimal = Decimal("0")
    esi: Decimal = Decimal("0")
    professional_tax: Decimal = Decimal("0")
    tds: Decimal = Decimal("0")
    loan_deduction: Decimal = Decimal("0")
    advance_salary_recovery: Decimal = Decimal("0")
    leave_deduction: Decimal = Decimal("0")
    late_attendance_deduction: Decimal = Decimal("0")
    penalty_deduction: Decimal = Decimal("0")
    other_deductions: Decimal = Decimal("0")
    total_deductions: Decimal = Decimal("0")
    gross_salary: Decimal = Decimal("0")
    in_hand_salary: Decimal = Decimal("0")
    amount_in_words: str | None = None
    payroll_year: int | None = None
    generated_at: datetime | None = None
    bank_snapshot: dict | None = None
    attendance_snapshot: dict | None = None
    leave_snapshot: dict | None = None
    employee_snapshot: dict | None = None
    company_snapshot: dict | None = None
    payment_date: date | None = None
    transaction_id: str | None = None

    class Config:
        from_attributes = True


class SalaryListResponse(BaseModel):
    items: list[SalarySlipResponse]
    total: int
    page: int
    page_size: int
