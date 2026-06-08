from datetime import datetime

from pydantic import BaseModel


class CompanySettingsResponse(BaseModel):
    id: int
    company_name: str
    company_logo_path: str | None = None
    company_address: str | None = None
    gst_number: str | None = None
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanySettingsUpdate(BaseModel):
    company_name: str | None = None
    company_address: str | None = None
    gst_number: str | None = None
