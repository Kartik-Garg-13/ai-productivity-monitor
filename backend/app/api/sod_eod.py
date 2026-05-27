from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.employee import Employee
from app.models.sod_eod import EODEntry, SODEntry
from app.models.user import User
from app.schemas.sod_eod import EODCreate, ReviewRequest, SODCreate

router = APIRouter(prefix="/workflow", tags=["sod-eod"])


def _duration(start: time, end: time) -> str:
    start_dt = datetime.combine(date.today(), start)
    end_dt = datetime.combine(date.today(), end)
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
    delta = end_dt - start_dt
    hrs = delta.seconds // 3600
    mins = (delta.seconds % 3600) // 60
    return f"{hrs:02d}:{mins:02d}"


@router.post("/sod")
def submit_sod(payload: SODCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    cutoff = time(8, 45)
    day_flag = "half-day" if datetime.now().time() > cutoff else "full-day"
    row = SODEntry(
        employee_id=employee.id,
        submitted_for_date=payload.submitted_for_date,
        type=payload.type,
        category=payload.category,
        subcategory=payload.subcategory,
        project=payload.project,
        work_type=payload.work_type,
        start_time=payload.start_time,
        end_time=payload.end_time,
        duration=_duration(payload.start_time, payload.end_time),
        completion_percentage=payload.completion_percentage,
        ticket_number=payload.ticket_number,
        day_flag=day_flag,
    )
    db.add(row)
    db.commit()
    return {"message": "SOD submitted", "day_flag": day_flag}


@router.post("/eod")
def submit_eod(payload: EODCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    next_day_cutoff = time(8, 30)
    now = datetime.now()
    day_flag = "half-day" if now.time() > next_day_cutoff else "full-day"
    row = EODEntry(
        employee_id=employee.id,
        submitted_for_date=payload.submitted_for_date,
        morning_activity=payload.morning_activity,
        incomplete_reason=payload.incomplete_reason,
        completion_remarks=payload.completion_remarks,
        day_flag=day_flag,
    )
    db.add(row)
    db.commit()
    return {"message": "EOD submitted", "day_flag": day_flag}


@router.get("/admin/sod")
def list_sod(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(SODEntry).order_by(SODEntry.created_at.desc()).all()


@router.get("/admin/eod")
def list_eod(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(EODEntry).order_by(EODEntry.created_at.desc()).all()


@router.patch("/admin/sod/{entry_id}")
def review_sod(entry_id: int, payload: ReviewRequest, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    item = db.query(SODEntry).filter(SODEntry.id == entry_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="SOD entry not found")
    item.review_status = payload.review_status
    item.admin_remarks = payload.admin_remarks
    db.commit()
    return {"message": "SOD reviewed"}


@router.patch("/admin/eod/{entry_id}")
def review_eod(entry_id: int, payload: ReviewRequest, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    item = db.query(EODEntry).filter(EODEntry.id == entry_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="EOD entry not found")
    item.review_status = payload.review_status
    item.admin_remarks = payload.admin_remarks
    db.commit()
    return {"message": "EOD reviewed"}
