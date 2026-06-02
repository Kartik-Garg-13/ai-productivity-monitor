from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.request_utils import get_client_ip
from app.db.session import get_db
from app.models.announcement import Announcement
from app.models.user import User
from app.schemas.announcement import (
    AnnouncementCreate,
    AnnouncementListResponse,
    AnnouncementResponse,
    AnnouncementUpdate,
)
from app.services.audit_service import log_action
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/announcements", tags=["announcements"])


@router.get("", response_model=AnnouncementListResponse)
def list_announcements(
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    query = db.query(Announcement)
    if current_user.role != "admin":
        query = query.filter(
            Announcement.publish_date <= now,
            or_(Announcement.expiry_date.is_(None), Announcement.expiry_date >= now),
        )
    if search:
        query = query.filter(Announcement.title.ilike(f"%{search.lower()}%"))
    query = query.order_by(Announcement.is_pinned.desc(), Announcement.publish_date.desc())
    total = query.count()
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    return AnnouncementListResponse(
        items=[AnnouncementResponse.from_orm_row(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


def _apply_announcement_payload(ann: Announcement, data: dict) -> None:
    field_map = {"announcement_type": "type"}
    for key, value in data.items():
        setattr(ann, field_map.get(key, key), value)


@router.post("", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
def create_announcement(
    payload: AnnouncementCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    data = payload.model_dump()
    ann = Announcement(
        title=data["title"],
        type=data["announcement_type"],
        content=data["content"],
        publish_date=data["publish_date"],
        expiry_date=data.get("expiry_date"),
        is_pinned=data.get("is_pinned", False),
        created_by=current_user.id,
    )
    db.add(ann)
    db.commit()
    db.refresh(ann)
    log_action(db, user=current_user, action="Announcement Created", entity_type="announcement", entity_id=ann.id, ip_address=get_client_ip(request))
    db.commit()
    employees = db.query(User).filter(User.role == "employee").all()
    for u in employees:
        NotificationService.new_announcement(u.email, ann.title)
    return AnnouncementResponse.from_orm_row(ann)


@router.put("/{announcement_id}", response_model=AnnouncementResponse)
def update_announcement(
    announcement_id: int,
    payload: AnnouncementUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    ann = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    _apply_announcement_payload(ann, payload.model_dump(exclude_unset=True))
    db.commit()
    log_action(db, user=current_user, action="Announcement Updated", entity_type="announcement", entity_id=ann.id, ip_address=get_client_ip(request))
    db.commit()
    return AnnouncementResponse.from_orm_row(ann)


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    ann = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    db.delete(ann)
    log_action(db, user=current_user, action="Announcement Deleted", entity_type="announcement", entity_id=announcement_id, ip_address=get_client_ip(request))
    db.commit()
    return {"message": "Announcement deleted"}
