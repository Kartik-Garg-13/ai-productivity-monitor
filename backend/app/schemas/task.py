from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    project_id: int
    title: str = Field(min_length=1)
    description: str | None = None
    priority: str = "medium"
    assigned_employee_id: int | None = None
    due_date: date | None = None
    status: str = "pending"


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    assigned_employee_id: int | None = None
    due_date: date | None = None
    status: str | None = None
    project_id: int | None = None


class TaskStatusUpdate(BaseModel):
    status: str


class CommentCreate(BaseModel):
    comment: str = Field(min_length=1)


class CommentResponse(BaseModel):
    id: int
    user_name: str
    comment: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    id: int
    project_id: int
    project_name: str | None = None
    title: str
    description: str | None
    priority: str
    assigned_employee_id: int | None
    assignee_name: str | None = None
    assigned_by_name: str | None = None
    due_date: date | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int

