from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    name: str = Field(min_length=1)
    client_name: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str = "active"
    project_lead_id: int | None = None
    tech_owner_id: int | None = None
    member_ids: list[int] = []


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    client_name: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = None
    project_lead_id: int | None = None
    tech_owner_id: int | None = None
    member_ids: list[int] | None = None


class MemberBrief(BaseModel):
    id: int
    employee_code: str
    name: str

    class Config:
        from_attributes = True


class ProjectResponse(BaseModel):
    id: int
    name: str
    client_name: str | None
    description: str | None
    start_date: date | None
    end_date: date | None
    status: str
    project_lead_id: int | None
    tech_owner_id: int | None
    project_lead_name: str | None = None
    tech_owner_name: str | None = None
    members: list[MemberBrief] = []
    task_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
    page: int
    page_size: int

