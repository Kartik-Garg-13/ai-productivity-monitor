from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.leave import LeaveApplication
from app.models.sod_eod import EODEntry, SODEntry
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/admin")
def admin_dashboard(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    today = date.today()
    total_employees = db.query(func.count(Employee.id)).scalar() or 0
    present_today = db.query(func.count(Attendance.id)).filter(Attendance.date == today).scalar() or 0
    absent_today = max(0, total_employees - present_today)
    pending_leaves = db.query(func.count(LeaveApplication.id)).filter(LeaveApplication.status == "pending").scalar() or 0
    pending_sod = db.query(func.count(SODEntry.id)).filter(SODEntry.review_status == "pending").scalar() or 0
    pending_eod = db.query(func.count(EODEntry.id)).filter(EODEntry.review_status == "pending").scalar() or 0
    return {
        "total_employees": total_employees,
        "present_today": present_today,
        "absent_today": absent_today,
        "pending_leaves": pending_leaves,
        "pending_sod_eod": pending_sod + pending_eod,
        "recent_activities": [],
        "productivity_overview": {"placeholder": True},
    }
