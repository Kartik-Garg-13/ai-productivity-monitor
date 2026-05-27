from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.user import User

router = APIRouter(prefix="/attendance", tags=["attendance"])


def _duration_text(start: datetime, end: datetime) -> str:
    total_seconds = int((end - start).total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"


@router.post("/check-in")
def check_in(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile missing")
    today = date.today()
    existing = db.query(Attendance).filter(Attendance.employee_id == employee.id, Attendance.date == today).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already checked in for today")
    item = Attendance(employee_id=employee.id, date=today, check_in=datetime.utcnow(), status="present")
    db.add(item)
    db.commit()
    return {"message": "Check-in successful"}


@router.post("/check-out")
def check_out(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    today = date.today()
    item = db.query(Attendance).filter(Attendance.employee_id == employee.id, Attendance.date == today).first()
    if not item:
        raise HTTPException(status_code=400, detail="No check-in record found")
    if item.check_out:
        raise HTTPException(status_code=400, detail="Already checked out")
    item.check_out = datetime.utcnow()
    item.work_duration = _duration_text(item.check_in, item.check_out)
    db.commit()
    return {"message": "Check-out successful", "duration": item.work_duration}


@router.get("/history")
def my_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    return db.query(Attendance).filter(Attendance.employee_id == employee.id).order_by(Attendance.date.desc()).all()


@router.get("/admin")
def admin_attendance(
    employee_id: int | None = None,
    attendance_date: date | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = db.query(Attendance)
    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)
    if attendance_date:
        query = query.filter(Attendance.date == attendance_date)
    return query.order_by(Attendance.date.desc()).all()
