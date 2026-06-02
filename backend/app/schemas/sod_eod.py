from __future__ import annotations

from datetime import date, time

from pydantic import BaseModel, Field


class SODCreate(BaseModel):
    submitted_for_date: date
    type: str
    category: str
    subcategory: str | None = None
    project: str
    work_type: str = Field(description="Bug, Feature, Query")
    start_time: time
    end_time: time
    completion_percentage: int = Field(ge=0, le=100)
    ticket_number: str | None = None


class EODCreate(BaseModel):
    submitted_for_date: date
    morning_activity: str
    incomplete_reason: str | None = None
    completion_remarks: str | None = None


class ReviewRequest(BaseModel):
    review_status: str
    admin_remarks: str | None = None

