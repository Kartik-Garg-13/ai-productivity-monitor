from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class LeaveApply(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: str
    mitigation_plan: str | None = None
    emergency_contact_number: str | None = None


class LeaveReview(BaseModel):
    status: str
    admin_remarks: str | None = None


class LeaveBalanceItem(BaseModel):
    leave_type: str
    label: str
    total_leave: int
    leave_taken: int
    remaining_leave: int


class LeaveApplicationResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: str | None = None
    employee_code: str | None = None
    department: str | None = None
    leave_type: str
    start_date: date
    end_date: date
    duration_days: int
    reason: str
    mitigation_plan: str | None = None
    emergency_contact_number: str | None = None
    status: str
    admin_remarks: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class LeaveHistoryResponse(BaseModel):
    balances: list[LeaveBalanceItem]
    balance: LeaveBalanceItem | None = None  # legacy: first / paid balance
    history: list[LeaveApplicationResponse]


class LeaveReportParams(BaseModel):
    month: int | None = Field(default=None, ge=1, le=12)
    year: int | None = None
    department: str | None = None
    employee_id: int | None = None
