from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    expense_date: date
    expense_type: str = Field(min_length=1)
    expense_category: str = Field(min_length=1)
    amount: Decimal = Field(gt=0)
    description: str | None = None


class ExpenseReview(BaseModel):
    status: str
    admin_remarks: str | None = None
    payment_date: date | None = None
    transaction_id: str | None = None


class ExpenseResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: str | None = None
    expense_date: date
    expense_type: str
    expense_category: str
    amount: Decimal
    description: str | None
    status: str
    payment_date: date | None
    transaction_id: str | None
    admin_remarks: str | None
    attachments: list[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


class ExpenseListResponse(BaseModel):
    items: list[ExpenseResponse]
    total: int
    page: int
    page_size: int

