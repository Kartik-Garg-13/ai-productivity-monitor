from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.leave_constants import DEFAULT_LEAVE_TOTALS, LEAVE_TYPES, VALID_LEAVE_STATUSES, normalize_leave_type
from app.models.employee import Employee
from app.models.leave import LeaveApplication, LeaveBalance


def ensure_leave_balances(db: Session, employee_id: int) -> list[LeaveBalance]:
    existing = db.query(LeaveBalance).filter(LeaveBalance.employee_id == employee_id).all()
    by_type: dict[str, LeaveBalance] = {}
    for b in existing:
        lt = normalize_leave_type(b.leave_type)
        if lt in LEAVE_TYPES:
            if b.leave_type != lt:
                b.leave_type = lt
            by_type[lt] = b

    for leave_type in LEAVE_TYPES:
        if leave_type not in by_type:
            total = DEFAULT_LEAVE_TOTALS[leave_type]
            db.add(
                LeaveBalance(
                    employee_id=employee_id,
                    leave_type=leave_type,
                    total_leave=total,
                    leave_taken=0,
                    remaining_leave=total,
                )
            )
    db.flush()
    return (
        db.query(LeaveBalance)
        .filter(LeaveBalance.employee_id == employee_id, LeaveBalance.leave_type.in_(LEAVE_TYPES))
        .order_by(LeaveBalance.leave_type)
        .all()
    )


def get_balance_for_type(db: Session, employee_id: int, leave_type: str) -> LeaveBalance:
    lt = normalize_leave_type(leave_type)
    ensure_leave_balances(db, employee_id)
    bal = (
        db.query(LeaveBalance)
        .filter(LeaveBalance.employee_id == employee_id, LeaveBalance.leave_type == lt)
        .first()
    )
    if not bal:
        total = DEFAULT_LEAVE_TOTALS.get(lt, 12)
        bal = LeaveBalance(employee_id=employee_id, leave_type=lt, total_leave=total, remaining_leave=total)
        db.add(bal)
        db.flush()
    return bal


def pending_days_for_type(db: Session, employee_id: int, leave_type: str) -> int:
    lt = normalize_leave_type(leave_type)
    pending = (
        db.query(LeaveApplication)
        .filter(
            LeaveApplication.employee_id == employee_id,
            LeaveApplication.status == "pending",
        )
        .all()
    )
    return sum(a.duration_days for a in pending if normalize_leave_type(a.leave_type) == lt)


def available_balance(db: Session, employee_id: int, leave_type: str) -> int:
    bal = get_balance_for_type(db, employee_id, leave_type)
    pending = pending_days_for_type(db, employee_id, leave_type)
    return max(0, bal.remaining_leave - pending)


def calculate_duration(start_date: date, end_date: date) -> int:
    return (end_date - start_date).days + 1


def compute_excess_unpaid_leave(db: Session, employee_id: int, payroll_month: date) -> int:
    """Days of unpaid leave beyond balance in the payroll month."""
    import calendar

    start = date(payroll_month.year, payroll_month.month, 1)
    end = date(payroll_month.year, payroll_month.month, calendar.monthrange(payroll_month.year, payroll_month.month)[1])
    apps = (
        db.query(LeaveApplication)
        .filter(
            LeaveApplication.employee_id == employee_id,
            LeaveApplication.status == "approved",
            LeaveApplication.start_date <= end,
            LeaveApplication.end_date >= start,
        )
        .all()
    )
    excess = 0
    for app in apps:
        lt = normalize_leave_type(app.leave_type)
        overlap_start = max(app.start_date, start)
        overlap_end = min(app.end_date, end)
        days = (overlap_end - overlap_start).days + 1 if overlap_end >= overlap_start else 0
        bal = get_balance_for_type(db, employee_id, lt)
        if days > bal.total_leave:
            excess += days - bal.total_leave
    return max(0, excess)


def apply_leave(
    db: Session,
    employee: Employee,
    leave_type: str,
    start_date: date,
    end_date: date,
    reason: str,
    mitigation_plan: str | None,
    emergency_contact_number: str | None,
) -> LeaveApplication:
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    lt = normalize_leave_type(leave_type)
    duration = calculate_duration(start_date, end_date)
    if duration <= 0:
        raise HTTPException(status_code=400, detail="Invalid leave duration")
    avail = available_balance(db, employee.id, lt)
    if duration > avail:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient {lt} leave balance. Available: {avail}, requested: {duration}",
        )
    app = LeaveApplication(
        employee_id=employee.id,
        leave_type=lt,
        start_date=start_date,
        end_date=end_date,
        duration_days=duration,
        reason=reason,
        mitigation_plan=mitigation_plan,
        emergency_contact_number=emergency_contact_number,
        status="pending",
    )
    db.add(app)
    return app


def review_leave(db: Session, app: LeaveApplication, status: str, admin_remarks: str | None, reviewer_id: int) -> None:
    if status not in VALID_LEAVE_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")
    if app.status != "pending" and app.status != "clarification_requested":
        raise HTTPException(status_code=400, detail=f"Leave already {app.status}")
    prev_status = app.status
    app.status = status
    app.admin_remarks = admin_remarks
    app.reviewed_at = datetime.utcnow()
    app.reviewed_by = reviewer_id

    if status == "approved" and prev_status in ("pending", "clarification_requested"):
        bal = get_balance_for_type(db, app.employee_id, app.leave_type)
        bal.leave_taken += app.duration_days
        bal.remaining_leave = max(0, bal.total_leave - bal.leave_taken)


def balance_responses(balances: list[LeaveBalance]) -> list[dict]:
    from app.core.leave_constants import LEAVE_TYPE_LABELS

    return [
        {
            "leave_type": b.leave_type,
            "label": LEAVE_TYPE_LABELS.get(b.leave_type, b.leave_type.title()),
            "total_leave": b.total_leave,
            "leave_taken": b.leave_taken,
            "remaining_leave": b.remaining_leave,
        }
        for b in sorted(balances, key=lambda x: x.leave_type)
    ]
