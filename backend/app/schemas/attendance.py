from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class AttendanceResponse(BaseModel):
    id: int
    employee_id: int
    date: date
    check_in: datetime
    check_out: datetime | None
    status: str
    work_duration: str | None
    ip_address: str | None = None

    class Config:
        from_attributes = True


class AttendanceAdminResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    employee_code: str
    department: str
    date: date
    check_in: datetime
    check_out: datetime | None
    status: str
    work_duration: str | None
    ip_address: str | None
