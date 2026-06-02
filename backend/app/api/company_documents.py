import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.company_document import CompanyDocument, DocumentDownload
from app.models.user import User
from app.schemas.company_document import CompanyDocumentListResponse, CompanyDocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])
UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "company"


@router.get("", response_model=CompanyDocumentListResponse)
def list_documents(
    search: str | None = None,
    category: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(CompanyDocument)
    if search:
        query = query.filter(CompanyDocument.title.ilike(f"%{search.lower()}%"))
    if category:
        query = query.filter(CompanyDocument.category == category)
    query = query.order_by(CompanyDocument.created_at.desc())
    total = query.count()
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    items = []
    for doc in rows:
        last_dl = (
            db.query(DocumentDownload)
            .filter(DocumentDownload.document_id == doc.id)
            .order_by(DocumentDownload.downloaded_at.desc())
            .first()
        )
        count = db.query(func.count(DocumentDownload.id)).filter(DocumentDownload.document_id == doc.id).scalar() or 0
        items.append(
            CompanyDocumentResponse(
                id=doc.id,
                title=doc.title,
                category=doc.category,
                file_path=doc.file_path,
                original_filename=doc.original_filename,
                created_at=doc.created_at,
                last_accessed=last_dl.downloaded_at if last_dl else None,
                download_count=count,
            )
        )
    return CompanyDocumentListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=CompanyDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    title: str = Form(...),
    category: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1]
    stored = f"{uuid.uuid4().hex}{ext}"
    path = UPLOAD_ROOT / stored
    content = await file.read()
    path.write_bytes(content)
    rel = f"uploads/company/{stored}"
    doc = CompanyDocument(
        title=title,
        category=category,
        file_path=rel,
        original_filename=file.filename,
        uploaded_by=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return CompanyDocumentResponse(
        id=doc.id,
        title=doc.title,
        category=doc.category,
        file_path=doc.file_path,
        original_filename=doc.original_filename,
        created_at=doc.created_at,
        download_count=0,
    )


@router.post("/{document_id}/download")
def track_download(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(CompanyDocument).filter(CompanyDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.add(DocumentDownload(document_id=document_id, user_id=current_user.id))
    db.commit()
    return {"file_path": doc.file_path, "title": doc.title}


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    doc = db.query(CompanyDocument).filter(CompanyDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted"}
