from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.employee import Employee
from app.models.leave import LeaveApplication, LeaveBalance
from app.models.user import User
from app.schemas.leave import LeaveApply, LeaveReview
router = APIRouter(prefix="/leave", tags=["leave"])


@router.post("/apply")
def apply_leave(payload: LeaveApply, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    balance = db.query(LeaveBalance).filter(LeaveBalance.employee_id == employee.id).first()
    duration = (payload.end_date - payload.start_date).days + 1
    if duration <= 0:
        raise HTTPException(status_code=400, detail="Invalid leave duration")
    if duration > balance.remaining_leave:
        raise HTTPException(status_code=400, detail="Insufficient leave balance")
    app = LeaveApplication(
        employee_id=employee.id,
        leave_type=payload.leave_type,
        start_date=payload.start_date,
        end_date=payload.end_date,
        duration_days=duration,
        reason=payload.reason,
        mitigation_plan=payload.mitigation_plan,
    )
    db.add(app)
    db.commit()
    return {"message": "Leave applied", "duration_days": duration}


@router.get("/history")
def leave_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    balance = db.query(LeaveBalance).filter(LeaveBalance.employee_id == employee.id).first()
    history = db.query(LeaveApplication).filter(LeaveApplication.employee_id == employee.id).all()
    return {"balance": balance, "history": history}


@router.get("/admin/pending")
def pending_leave_requests(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(LeaveApplication).filter(LeaveApplication.status == "pending").all()


@router.patch("/admin/{leave_id}")
def review_leave(leave_id: int, payload: LeaveReview, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    app = db.query(LeaveApplication).filter(LeaveApplication.id == leave_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Leave request not found")
    app.status = payload.status
    app.admin_remarks = payload.admin_remarks
    if payload.status == "approved":
        balance = db.query(LeaveBalance).filter(LeaveBalance.employee_id == app.employee_id).first()
        balance.leave_taken += app.duration_days
        balance.remaining_leave = max(0, balance.total_leave - balance.leave_taken)
    db.commit()
    return {"message": "Leave request updated"}
