import calendar
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.attendance import Attendance
from app.models.leave import LeaveApplication


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def get_attendance_summary(db: Session, employee_id: int, payroll_month: date) -> dict:
    start, end = _month_bounds(payroll_month.year, payroll_month.month)
    records = (
        db.query(Attendance)
        .filter(
            Attendance.employee_id == employee_id,
            Attendance.date >= start,
            Attendance.date <= end,
        )
        .all()
    )
    working_days = sum(1 for d in range((end - start).days + 1) if date.fromordinal(start.toordinal() + d).weekday() < 5)
    present_days = sum(1 for r in records if r.status in ("present", "half_day"))
    on_leave_days = sum(1 for r in records if r.status == "on_leave")
    absent_days = max(0, working_days - present_days - on_leave_days)

    overtime_hours = Decimal("0")
    late_days = 0
    for r in records:
        if r.work_duration:
            parts = r.work_duration.split(":")
            if len(parts) >= 2:
                try:
                    hours = int(parts[0]) + int(parts[1]) / 60
                    if hours > 9:
                        overtime_hours += Decimal(str(round(hours - 9, 2)))
                except ValueError:
                    pass
        if r.check_in and r.check_in.hour >= 10 and r.check_in.minute > 15:
            late_days += 1

    approved_leaves = (
        db.query(LeaveApplication)
        .filter(
            LeaveApplication.employee_id == employee_id,
            LeaveApplication.status == "approved",
            LeaveApplication.start_date <= end,
            LeaveApplication.end_date >= start,
        )
        .all()
    )
    casual_leave_days = sick_leave_days = paid_leave_days = unpaid_leave_days = 0
    for app in approved_leaves:
        overlap_start = max(app.start_date, start)
        overlap_end = min(app.end_date, end)
        days = (overlap_end - overlap_start).days + 1 if overlap_end >= overlap_start else 0
        lt = (app.leave_type or "").lower()
        if lt in ("casual", "cl"):
            casual_leave_days += days
        elif lt in ("sick", "sl"):
            sick_leave_days += days
        elif lt in ("paid", "annual", "pl"):
            paid_leave_days += days
        else:
            unpaid_leave_days += days

    return {
        "working_days": working_days,
        "present_days": present_days,
        "absent_days": absent_days,
        "on_leave_days": on_leave_days,
        "casual_leave_days": casual_leave_days,
        "sick_leave_days": sick_leave_days,
        "paid_leave_days": paid_leave_days,
        "unpaid_leave_days": unpaid_leave_days,
        "overtime_hours": float(overtime_hours),
        "late_days": late_days,
        "period_start": start.isoformat(),
        "period_end": end.isoformat(),
    }
