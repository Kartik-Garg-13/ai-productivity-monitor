from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CompanyDocumentResponse(BaseModel):
    id: int
    title: str
    category: str
    file_path: str
    original_filename: str | None
    created_at: datetime
    last_accessed: datetime | None = None
    download_count: int = 0

    class Config:
        from_attributes = True


class CompanyDocumentListResponse(BaseModel):
    items: list[CompanyDocumentResponse]
    total: int
    page: int
    page_size: int


class DocumentUploadMeta(BaseModel):
    title: str = Field(min_length=1)
    category: str = Field(min_length=1)

