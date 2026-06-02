from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.expense import Expense
from app.models.leave import LeaveApplication
from app.models.project import Project, ProjectTask
from app.models.salary import SalarySlip
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

    week_start = today - timedelta(days=6)
    attendance_trend = []
    for i in range(7):
        d = week_start + timedelta(days=i)
        count = db.query(func.count(Attendance.id)).filter(Attendance.date == d).scalar() or 0
        attendance_trend.append({"date": d.isoformat(), "present": count})

    leave_stats = {
        "pending": pending_leaves,
        "approved": db.query(func.count(LeaveApplication.id)).filter(LeaveApplication.status == "approved").scalar() or 0,
        "rejected": db.query(func.count(LeaveApplication.id)).filter(LeaveApplication.status == "rejected").scalar() or 0,
    }

    expense_stats = {
        "pending": db.query(func.count(Expense.id)).filter(Expense.status == "pending").scalar() or 0,
        "approved": db.query(func.count(Expense.id)).filter(Expense.status == "approved").scalar() or 0,
        "paid": db.query(func.count(Expense.id)).filter(Expense.status == "paid").scalar() or 0,
        "total_amount": float(db.query(func.sum(Expense.amount)).filter(Expense.status == "paid").scalar() or 0),
    }

    salary_stats = {
        "generated": db.query(func.count(SalarySlip.id)).filter(SalarySlip.status == "generated").scalar() or 0,
        "paid": db.query(func.count(SalarySlip.id)).filter(SalarySlip.status == "paid").scalar() or 0,
        "total_paid": float(db.query(func.sum(SalarySlip.net_salary)).filter(SalarySlip.status == "paid").scalar() or 0),
    }

    project_stats = {
        "active": db.query(func.count(Project.id)).filter(Project.status == "active").scalar() or 0,
        "completed": db.query(func.count(Project.id)).filter(Project.status == "completed").scalar() or 0,
        "on_hold": db.query(func.count(Project.id)).filter(Project.status == "on_hold").scalar() or 0,
    }

    total_tasks = db.query(func.count(ProjectTask.id)).scalar() or 0
    completed_tasks = db.query(func.count(ProjectTask.id)).filter(ProjectTask.status == "completed").scalar() or 0
    task_completion_rate = round((completed_tasks / total_tasks * 100) if total_tasks else 0, 1)

    return {
        "total_employees": total_employees,
        "present_today": present_today,
        "absent_today": absent_today,
        "pending_leaves": pending_leaves,
        "pending_sod_eod": pending_sod + pending_eod,
        "attendance_trend": attendance_trend,
        "leave_stats": leave_stats,
        "expense_stats": expense_stats,
        "salary_stats": salary_stats,
        "project_stats": project_stats,
        "task_completion_rate": task_completion_rate,
        "completed_tasks": completed_tasks,
        "total_tasks": total_tasks,
    }


@router.get("/employee")
def employee_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")

    today = date.today()
    today_attendance = (
        db.query(Attendance)
        .filter(Attendance.employee_id == employee.id, Attendance.date == today)
        .first()
    )
    pending_leaves = (
        db.query(func.count(LeaveApplication.id))
        .filter(LeaveApplication.employee_id == employee.id, LeaveApplication.status == "pending")
        .scalar()
        or 0
    )
    sod_today = (
        db.query(SODEntry)
        .filter(SODEntry.employee_id == employee.id, SODEntry.submitted_for_date == today)
        .order_by(SODEntry.created_at.desc())
        .first()
    )
    eod_today = (
        db.query(EODEntry)
        .filter(EODEntry.employee_id == employee.id, EODEntry.submitted_for_date == today)
        .order_by(EODEntry.created_at.desc())
        .first()
    )
    my_tasks = (
        db.query(func.count(ProjectTask.id))
        .filter(ProjectTask.assigned_employee_id == employee.id, ProjectTask.status != "completed")
        .scalar()
        or 0
    )

    return {
        "name": current_user.name,
        "employee_id": employee.employee_code,
        "department": employee.department,
        "designation": employee.designation,
        "today_attendance": {
            "checked_in": today_attendance is not None,
            "check_in": today_attendance.check_in.isoformat() if today_attendance else None,
            "check_out": today_attendance.check_out.isoformat() if today_attendance and today_attendance.check_out else None,
            "work_duration": today_attendance.work_duration if today_attendance else None,
            "ip_address": today_attendance.ip_address if today_attendance else None,
        },
        "pending_leaves": pending_leaves,
        "sod_status": sod_today.review_status if sod_today else "not_submitted",
        "eod_status": eod_today.review_status if eod_today else "not_submitted",
        "open_tasks": my_tasks,
    }
