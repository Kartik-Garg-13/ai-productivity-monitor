from datetime import date

from pydantic import BaseModel


class LeaveApply(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: str
    mitigation_plan: str | None = None


class LeaveReview(BaseModel):
    status: str
    admin_remarks: str | None = None
