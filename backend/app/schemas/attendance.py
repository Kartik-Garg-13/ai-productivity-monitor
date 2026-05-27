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

    class Config:
        from_attributes = True
