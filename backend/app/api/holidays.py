from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.request_utils import get_client_ip
from app.db.session import get_db
from app.models.holiday import Holiday
from app.models.user import User
from app.schemas.holiday import HolidayCreate, HolidayListResponse, HolidayResponse, HolidayUpdate
from app.services.audit_service import log_action

router = APIRouter(prefix="/holidays", tags=["holidays"])


@router.get("", response_model=HolidayListResponse)
def list_holidays(
    search: str | None = None,
    year: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Holiday)
    if search:
        query = query.filter(Holiday.name.ilike(f"%{search.lower()}%"))
    if year:
        query = query.filter(Holiday.date.between(f"{year}-01-01", f"{year}-12-31"))
    query = query.order_by(Holiday.date.asc())
    total = query.count()
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    return HolidayListResponse(
        items=[HolidayResponse.from_orm_row(r) for r in rows], total=total, page=page, page_size=page_size
    )


def _apply_holiday_payload(holiday: Holiday, data: dict) -> None:
    if "name" in data:
        holiday.name = data["name"]
    if "holiday_date" in data:
        holiday.date = data["holiday_date"]
    if "holiday_type" in data:
        holiday.type = data["holiday_type"]
    if "description" in data:
        holiday.description = data["description"]


@router.post("", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
def create_holiday(
    payload: HolidayCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    data = payload.model_dump()
    holiday = Holiday(
        name=data["name"],
        date=data["holiday_date"],
        type=data["holiday_type"],
        description=data.get("description"),
    )
    db.add(holiday)
    db.commit()
    db.refresh(holiday)
    log_action(db, user=current_user, action="Holiday Created", entity_type="holiday", entity_id=holiday.id, ip_address=get_client_ip(request))
    db.commit()
    return HolidayResponse.from_orm_row(holiday)


@router.put("/{holiday_id}", response_model=HolidayResponse)
def update_holiday(
    holiday_id: int,
    payload: HolidayUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    _apply_holiday_payload(holiday, payload.model_dump(exclude_unset=True))
    db.commit()
    log_action(db, user=current_user, action="Holiday Updated", entity_type="holiday", entity_id=holiday.id, ip_address=get_client_ip(request))
    db.commit()
    return HolidayResponse.from_orm_row(holiday)


@router.delete("/{holiday_id}")
def delete_holiday(
    holiday_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    db.delete(holiday)
    log_action(db, user=current_user, action="Holiday Deleted", entity_type="holiday", entity_id=holiday_id, ip_address=get_client_ip(request))
    db.commit()
    return {"message": "Holiday deleted"}
