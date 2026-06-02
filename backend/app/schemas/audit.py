from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    user_id: int | None
    user_name: str | None = None
    action: str
    entity_type: str | None
    entity_id: int | None
    details: str | None
    ip_address: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int

