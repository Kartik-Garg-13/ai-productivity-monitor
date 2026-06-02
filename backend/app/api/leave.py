from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, require_admin
from app.core.request_utils import get_client_ip
from app.db.session import get_db
from app.models.employee import Employee
from app.models.leave import LeaveApplication, LeaveBalance
from app.models.user import User
from app.schemas.leave import LeaveApply, LeaveReview
from app.services.audit_service import log_action
from app.services.notification_service import NotificationService

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
    return db.query(LeaveApplication).options(joinedload(LeaveApplication.employee)).filter(LeaveApplication.status == "pending").all()


@router.patch("/admin/{leave_id}")
def review_leave(
    leave_id: int,
    payload: LeaveReview,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    app = (
        db.query(LeaveApplication)
        .options(joinedload(LeaveApplication.employee).joinedload(Employee.user))
        .filter(LeaveApplication.id == leave_id)
        .first()
    )
    if not app:
        raise HTTPException(status_code=404, detail="Leave request not found")
    app.status = payload.status
    app.admin_remarks = payload.admin_remarks
    if payload.status == "approved":
        balance = db.query(LeaveBalance).filter(LeaveBalance.employee_id == app.employee_id).first()
        balance.leave_taken += app.duration_days
        balance.remaining_leave = max(0, balance.total_leave - balance.leave_taken)
    db.commit()
    action = "Leave Approved" if payload.status == "approved" else "Leave Rejected"
    log_action(db, user=current_user, action=action, entity_type="leave", entity_id=app.id, ip_address=get_client_ip(request))
    db.commit()
    if app.employee and app.employee.user:
        email = app.employee.user.email
        if payload.status == "approved":
            NotificationService.leave_approved(email, str(app.start_date), str(app.end_date))
        else:
            NotificationService.leave_rejected(email, payload.admin_remarks)
    return {"message": "Leave request updated"}
