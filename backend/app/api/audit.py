from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogListResponse, AuditLogResponse

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=AuditLogListResponse)
def list_audit_logs(
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = db.query(AuditLog).options(joinedload(AuditLog.user))
    if search:
        query = query.filter(AuditLog.action.ilike(f"%{search.lower()}%"))
    query = query.order_by(AuditLog.created_at.desc())
    total = query.count()
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    items = [
        AuditLogResponse(
            id=r.id,
            user_id=r.user_id,
            user_name=r.user.name if r.user else None,
            action=r.action,
            entity_type=r.entity_type,
            entity_id=r.entity_id,
            details=r.details,
            ip_address=r.ip_address,
            created_at=r.created_at,
        )
        for r in rows
    ]
    return AuditLogListResponse(items=items, total=total, page=page, page_size=page_size)
