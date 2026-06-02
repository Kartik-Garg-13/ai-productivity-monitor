from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, require_admin
from app.core.request_utils import get_client_ip
from app.db.session import get_db
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.user import User
from app.schemas.attendance import AttendanceAdminResponse, AttendanceResponse

router = APIRouter(prefix="/attendance", tags=["attendance"])


def _duration_text(start: datetime, end: datetime) -> str:
    total_seconds = int((end - start).total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"


@router.post("/check-in")
def check_in(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile missing")
    today = date.today()
    existing = db.query(Attendance).filter(Attendance.employee_id == employee.id, Attendance.date == today).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already checked in for today")
    item = Attendance(
        employee_id=employee.id,
        date=today,
        check_in=datetime.utcnow(),
        status="present",
        ip_address=get_client_ip(request),
    )
    db.add(item)
    db.commit()
    return {"message": "Check-in successful", "ip_address": item.ip_address}


@router.post("/check-out")
def check_out(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    today = date.today()
    item = db.query(Attendance).filter(Attendance.employee_id == employee.id, Attendance.date == today).first()
    if not item:
        raise HTTPException(status_code=400, detail="No check-in record found")
    if item.check_out:
        raise HTTPException(status_code=400, detail="Already checked out")
    item.check_out = datetime.utcnow()
    item.work_duration = _duration_text(item.check_in, item.check_out)
    if not item.ip_address:
        item.ip_address = get_client_ip(request)
    db.commit()
    return {"message": "Check-out successful", "duration": item.work_duration, "ip_address": item.ip_address}


@router.get("/today", response_model=AttendanceResponse | None)
def today_attendance(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        return None
    return (
        db.query(Attendance)
        .filter(Attendance.employee_id == employee.id, Attendance.date == date.today())
        .first()
    )


@router.get("/history", response_model=list[AttendanceResponse])
def my_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        return []
    return db.query(Attendance).filter(Attendance.employee_id == employee.id).order_by(Attendance.date.desc()).all()


@router.get("/admin", response_model=list[AttendanceAdminResponse])
def admin_attendance(
    employee_id: int | None = None,
    attendance_date: date | None = None,
    department: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = (
        db.query(Attendance)
        .join(Employee, Attendance.employee_id == Employee.id)
        .join(User, Employee.user_id == User.id)
        .options(joinedload(Attendance.employee).joinedload(Employee.user))
    )
    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)
    if attendance_date:
        query = query.filter(Attendance.date == attendance_date)
    if department:
        query = query.filter(Employee.department.ilike(f"%{department}%"))
    rows = query.order_by(Attendance.date.desc(), Attendance.check_in.desc()).all()
    return [
        AttendanceAdminResponse(
            id=row.id,
            employee_id=row.employee_id,
            employee_name=row.employee.user.name,
            employee_code=row.employee.employee_code,
            department=row.employee.department,
            date=row.date,
            check_in=row.check_in,
            check_out=row.check_out,
            status=row.status,
            work_duration=row.work_duration,
            ip_address=row.ip_address,
        )
        for row in rows
    ]
