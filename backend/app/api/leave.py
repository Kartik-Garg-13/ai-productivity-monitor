from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, require_admin
from app.core.leave_constants import normalize_leave_type
from app.core.request_utils import get_client_ip
from app.db.session import get_db
from app.models.employee import Employee
from app.models.leave import LeaveApplication, LeaveBalance
from app.models.user import User
from app.schemas.leave import (
    LeaveApplicationResponse,
    LeaveApply,
    LeaveBalanceItem,
    LeaveHistoryResponse,
    LeaveReview,
)
from app.services.audit_service import log_action
from app.services.leave_service import (
    apply_leave,
    balance_responses,
    ensure_leave_balances,
    review_leave,
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/leave", tags=["leave"])


def _app_response(app: LeaveApplication) -> LeaveApplicationResponse:
    emp = app.employee
    return LeaveApplicationResponse(
        id=app.id,
        employee_id=app.employee_id,
        employee_name=emp.full_name if emp else None,
        employee_code=emp.employee_code if emp else None,
        department=emp.department if emp else None,
        leave_type=app.leave_type,
        start_date=app.start_date,
        end_date=app.end_date,
        duration_days=app.duration_days,
        reason=app.reason,
        mitigation_plan=app.mitigation_plan,
        emergency_contact_number=app.emergency_contact_number,
        status=app.status,
        admin_remarks=app.admin_remarks,
        created_at=app.created_at,
    )


@router.post("/apply")
def apply_leave_route(payload: LeaveApply, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    app = apply_leave(
        db,
        employee,
        payload.leave_type,
        payload.start_date,
        payload.end_date,
        payload.reason,
        payload.mitigation_plan,
        payload.emergency_contact_number,
    )
    db.commit()
    return {"message": "Leave applied", "duration_days": app.duration_days, "id": app.id}


@router.get("/balances", response_model=list[LeaveBalanceItem])
def leave_balances(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    balances = ensure_leave_balances(db, employee.id)
    db.commit()
    return [LeaveBalanceItem(**b) for b in balance_responses(balances)]


@router.get("/history", response_model=LeaveHistoryResponse)
def leave_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    balances = ensure_leave_balances(db, employee.id)
    history = (
        db.query(LeaveApplication)
        .filter(LeaveApplication.employee_id == employee.id)
        .order_by(LeaveApplication.created_at.desc())
        .all()
    )
    balance_items = [LeaveBalanceItem(**b) for b in balance_responses(balances)]
    paid = next((b for b in balance_items if b.leave_type == "paid"), balance_items[0] if balance_items else None)
    db.commit()
    return LeaveHistoryResponse(
        balances=balance_items,
        balance=paid,
        history=[_app_response(h) for h in history],
    )


@router.get("/admin/pending", response_model=list[LeaveApplicationResponse])
def pending_leave_requests(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    rows = (
        db.query(LeaveApplication)
        .options(joinedload(LeaveApplication.employee))
        .filter(LeaveApplication.status.in_(["pending", "clarification_requested"]))
        .order_by(LeaveApplication.created_at.asc())
        .all()
    )
    return [_app_response(r) for r in rows]


@router.get("/admin/all", response_model=list[LeaveApplicationResponse])
def all_leave_requests(
    status: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = db.query(LeaveApplication).options(joinedload(LeaveApplication.employee))
    if status:
        query = query.filter(LeaveApplication.status == status)
    rows = query.order_by(LeaveApplication.created_at.desc()).limit(200).all()
    return [_app_response(r) for r in rows]


@router.patch("/admin/{leave_id}")
def review_leave_route(
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
    review_leave(db, app, payload.status, payload.admin_remarks, current_user.id)
    db.commit()
    action = f"Leave {payload.status.replace('_', ' ').title()}"
    log_action(db, user=current_user, action=action, entity_type="leave", entity_id=app.id, ip_address=get_client_ip(request))
    db.commit()
    if app.employee and app.employee.user:
        email = app.employee.user.email
        if payload.status == "approved":
            NotificationService.leave_approved(email, str(app.start_date), str(app.end_date))
        elif payload.status == "rejected":
            NotificationService.leave_rejected(email, payload.admin_remarks)
    return {"message": "Leave request updated"}


@router.post("/{leave_id}/cancel")
def cancel_leave(leave_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    app = db.query(LeaveApplication).filter(LeaveApplication.id == leave_id).first()
    if not app or not employee or app.employee_id != employee.id:
        raise HTTPException(status_code=404, detail="Leave request not found")
    if app.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending leave can be cancelled")
    app.status = "cancelled"
    db.commit()
    return {"message": "Leave cancelled"}


@router.get("/reports/monthly")
def monthly_leave_report(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    import calendar

    start = date(year, month, 1)
    end = date(year, month, calendar.monthrange(year, month)[1])

    apps = (
        db.query(LeaveApplication)
        .options(joinedload(LeaveApplication.employee))
        .filter(LeaveApplication.start_date <= end, LeaveApplication.end_date >= start)
        .all()
    )
    return {
        "year": year,
        "month": month,
        "total_applications": len(apps),
        "approved": sum(1 for a in apps if a.status == "approved"),
        "pending": sum(1 for a in apps if a.status == "pending"),
        "rejected": sum(1 for a in apps if a.status == "rejected"),
        "items": [_app_response(a) for a in apps],
    }


@router.get("/reports/department")
def department_leave_report(
    department: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = db.query(LeaveApplication).options(joinedload(LeaveApplication.employee)).join(Employee)
    if department:
        query = query.filter(Employee.department.ilike(f"%{department}%"))
    apps = query.order_by(LeaveApplication.created_at.desc()).limit(500).all()
    by_dept: dict[str, dict] = {}
    for app in apps:
        dept = app.employee.department if app.employee else "Unknown"
        if dept not in by_dept:
            by_dept[dept] = {"department": dept, "total": 0, "approved": 0, "pending": 0, "rejected": 0}
        by_dept[dept]["total"] += 1
        if app.status in ("approved", "pending", "rejected"):
            by_dept[dept][app.status] = by_dept[dept].get(app.status, 0) + 1
    return {"departments": list(by_dept.values())}


@router.get("/reports/employee/{employee_id}")
def employee_leave_history_report(
    employee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    balances = ensure_leave_balances(db, employee_id)
    history = (
        db.query(LeaveApplication)
        .filter(LeaveApplication.employee_id == employee_id)
        .order_by(LeaveApplication.created_at.desc())
        .all()
    )
    db.commit()
    return {
        "employee": {"id": employee.id, "name": employee.full_name, "code": employee.employee_code, "department": employee.department},
        "balances": balance_responses(balances),
        "history": [_app_response(h) for h in history],
    }
