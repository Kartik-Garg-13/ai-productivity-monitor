from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnnouncementBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(min_length=1)
    announcement_type: str = Field(default="general", validation_alias="type", serialization_alias="type")
    content: str = Field(min_length=1)
    publish_date: datetime
    expiry_date: datetime | None = None
    is_pinned: bool = False


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str | None = None
    announcement_type: str | None = Field(default=None, validation_alias="type", serialization_alias="type")
    content: str | None = None
    publish_date: datetime | None = None
    expiry_date: datetime | None = None
    is_pinned: bool | None = None


class AnnouncementResponse(AnnouncementBase):
    id: int
    created_at: datetime

    @classmethod
    def from_orm_row(cls, row) -> AnnouncementResponse:
        return cls(
            id=row.id,
            title=row.title,
            announcement_type=row.type,
            content=row.content,
            publish_date=row.publish_date,
            expiry_date=row.expiry_date,
            is_pinned=row.is_pinned,
            created_at=row.created_at,
        )


class AnnouncementListResponse(BaseModel):
    items: list[AnnouncementResponse]
    total: int
    page: int
    page_size: int
