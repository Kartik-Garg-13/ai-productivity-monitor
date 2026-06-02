from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class HolidayBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1)
    holiday_date: date = Field(validation_alias="date", serialization_alias="date")
    holiday_type: str = Field(default="public", validation_alias="type", serialization_alias="type")
    description: str | None = None


class HolidayCreate(HolidayBase):
    pass


class HolidayUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str | None = None
    holiday_date: date | None = Field(default=None, validation_alias="date", serialization_alias="date")
    holiday_type: str | None = Field(default=None, validation_alias="type", serialization_alias="type")
    description: str | None = None


class HolidayResponse(HolidayBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    created_at: datetime

    @classmethod
    def from_orm_row(cls, row) -> HolidayResponse:
        return cls(
            id=row.id,
            name=row.name,
            holiday_date=row.date,
            holiday_type=row.type,
            description=row.description,
            created_at=row.created_at,
        )


class HolidayListResponse(BaseModel):
    items: list[HolidayResponse]
    total: int
    page: int
    page_size: int
