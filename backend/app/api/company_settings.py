from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.company_settings import CompanySettings
from app.models.user import User
from app.schemas.company_settings import CompanySettingsResponse, CompanySettingsUpdate
from app.services.salary_service import get_company_settings
from app.utils.file_validation import validate_upload_file

router = APIRouter(prefix="/company-settings", tags=["company-settings"])

UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "company"


@router.get("", response_model=CompanySettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    row = get_company_settings(db)
    db.commit()
    return row


@router.put("", response_model=CompanySettingsResponse)
def update_settings(payload: CompanySettingsUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    row = get_company_settings(db)
    if payload.company_name is not None:
        row.company_name = payload.company_name
    if payload.company_address is not None:
        row.company_address = payload.company_address
    if payload.gst_number is not None:
        row.gst_number = payload.gst_number
    db.commit()
    db.refresh(row)
    return row


@router.post("/logo", response_model=CompanySettingsResponse)
async def upload_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename or "logo.png").suffix or ".png"
    filename = f"logo_{uuid4().hex}{ext}"
    dest = UPLOAD_ROOT / filename
    content = await file.read()
    validate_upload_file(file.filename, content, image_only=True)
    dest.write_bytes(content)
    row = get_company_settings(db)
    row.company_logo_path = f"uploads/company/{filename}"
    db.commit()
    db.refresh(row)
    return row
