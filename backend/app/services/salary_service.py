from datetime import date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.company_settings import CompanySettings
from app.models.employee import Employee
from app.models.salary import SalarySlip
from app.services.attendance_summary_service import get_attendance_summary
from app.services.leave_service import compute_excess_unpaid_leave
from app.utils.number_to_words import amount_in_words_rupees


def _d(value) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def get_company_settings(db: Session) -> CompanySettings:
    row = db.query(CompanySettings).first()
    if not row:
        row = CompanySettings(
            company_name="Goldilocks Tech",
            company_address="Bangalore, Karnataka, India",
        )
        db.add(row)
        db.flush()
    return row


def earnings_from_payload(data: dict) -> dict[str, Decimal]:
    return {
        "basic_salary": _d(data.get("basic_salary", 0)),
        "hra": _d(data.get("hra", 0)),
        "da": _d(data.get("da", 0)),
        "conveyance_allowance": _d(data.get("conveyance_allowance", 0)),
        "medical_allowance": _d(data.get("medical_allowance", 0)),
        "internet_allowance": _d(data.get("internet_allowance", 0)),
        "special_allowance": _d(data.get("special_allowance", 0)),
        "bonus": _d(data.get("bonus", 0)),
        "incentive": _d(data.get("incentive", 0)),
        "overtime_pay": _d(data.get("overtime_pay", 0)),
        "project_bonus": _d(data.get("project_bonus", 0)),
        "other_earnings": _d(data.get("other_earnings", 0)),
    }


def deductions_from_payload(data: dict, auto_leave_deduction: Decimal = Decimal("0")) -> dict[str, Decimal]:
    leave_ded = _d(data.get("leave_deduction", 0))
    if leave_ded == 0 and auto_leave_deduction > 0:
        leave_ded = auto_leave_deduction
    return {
        "pf": _d(data.get("pf", 0)),
        "esi": _d(data.get("esi", 0)),
        "professional_tax": _d(data.get("professional_tax", 0)),
        "tds": _d(data.get("tds", 0)),
        "loan_deduction": _d(data.get("loan_deduction", 0)),
        "advance_salary_recovery": _d(data.get("advance_salary_recovery", 0)),
        "leave_deduction": leave_ded,
        "late_attendance_deduction": _d(data.get("late_attendance_deduction", 0)),
        "penalty_deduction": _d(data.get("penalty_deduction", 0)),
        "other_deductions": _d(data.get("other_deductions", 0)),
    }


def calc_auto_leave_deduction(db: Session, employee_id: int, payroll_month: date, basic_salary: Decimal) -> Decimal:
    import calendar

    working_days = sum(
        1
        for d in range(1, calendar.monthrange(payroll_month.year, payroll_month.month)[1] + 1)
        if date(payroll_month.year, payroll_month.month, d).weekday() < 5
    )
    if working_days <= 0:
        return Decimal("0")
    excess = compute_excess_unpaid_leave(db, employee_id, payroll_month)
    if excess <= 0:
        attendance = get_attendance_summary(db, employee_id, payroll_month)
        excess = attendance.get("unpaid_leave_days", 0)
    per_day = basic_salary / Decimal(working_days)
    return (per_day * Decimal(excess)).quantize(Decimal("0.01"))


def calculate_payroll(
    db: Session,
    employee: Employee,
    payroll_month: date,
    payload: dict,
    *,
    apply_auto_leave_deduction: bool = True,
) -> dict:
    earnings = earnings_from_payload(payload)
    basic = earnings["basic_salary"]
    auto_leave = calc_auto_leave_deduction(db, employee.id, payroll_month, basic) if apply_auto_leave_deduction else Decimal("0")
    deductions = deductions_from_payload(payload, auto_leave)

    total_earnings = sum(earnings.values())
    total_deductions = sum(deductions.values())
    gross_salary = total_earnings
    net_salary = total_earnings - total_deductions
    in_hand = net_salary - deductions["advance_salary_recovery"]

    attendance_snapshot = get_attendance_summary(db, employee.id, payroll_month)
    company = get_company_settings(db)
    bank = employee.bank_details

    employee_snapshot = {
        "name": employee.full_name,
        "employee_id": employee.employee_id or employee.employee_code,
        "employee_code": employee.employee_code,
        "designation": employee.designation,
        "department": employee.department,
        "joining_date": employee.joining_date.isoformat() if employee.joining_date else None,
        "pan_number": employee.pan_number,
        "uan_number": employee.uan_number,
        "pf_number": employee.pf_number,
        "work_location": employee.work_location,
    }
    bank_snapshot = {
        "bank_name": bank.bank_name if bank else None,
        "account_number": bank.account_number if bank else None,
        "ifsc_code": bank.ifsc_code if bank else None,
    }
    company_snapshot = {
        "company_name": company.company_name,
        "company_logo_path": company.company_logo_path,
        "company_address": company.company_address,
        "gst_number": company.gst_number,
    }

    return {
        "earnings": earnings,
        "deductions": deductions,
        "total_earnings": total_earnings,
        "total_deductions": total_deductions,
        "gross_salary": gross_salary,
        "net_salary": net_salary,
        "in_hand_salary": in_hand,
        "amount_in_words": amount_in_words_rupees(net_salary),
        "payroll_year": payroll_month.year,
        "attendance_snapshot": attendance_snapshot,
        "leave_snapshot": {
            "casual_leave_days": attendance_snapshot["casual_leave_days"],
            "sick_leave_days": attendance_snapshot["sick_leave_days"],
            "paid_leave_days": attendance_snapshot["paid_leave_days"],
            "unpaid_leave_days": attendance_snapshot["unpaid_leave_days"],
        },
        "employee_snapshot": employee_snapshot,
        "company_snapshot": company_snapshot,
        "bank_snapshot": bank_snapshot,
    }


def apply_calculation_to_slip(slip: SalarySlip, calc: dict) -> None:
    for k, v in calc["earnings"].items():
        setattr(slip, k, v)
    for k, v in calc["deductions"].items():
        setattr(slip, k, v)
    slip.total_earnings = calc["total_earnings"]
    slip.total_deductions = calc["total_deductions"]
    slip.deductions = calc["total_deductions"]  # legacy column sync
    slip.gross_salary = calc["gross_salary"]
    slip.net_salary = calc["net_salary"]
    slip.in_hand_salary = calc["in_hand_salary"]
    slip.amount_in_words = calc["amount_in_words"]
    slip.payroll_year = calc["payroll_year"]
    slip.attendance_snapshot = calc["attendance_snapshot"]
    slip.leave_snapshot = calc["leave_snapshot"]
    slip.employee_snapshot = calc["employee_snapshot"]
    slip.company_snapshot = calc["company_snapshot"]
    slip.bank_snapshot = calc["bank_snapshot"]
    slip.generated_at = datetime.utcnow()


def payload_from_slip(slip: SalarySlip) -> dict:
    data = {}
    for field in [
        "basic_salary", "hra", "da", "conveyance_allowance", "medical_allowance",
        "internet_allowance", "special_allowance", "bonus", "incentive",
        "overtime_pay", "project_bonus", "other_earnings",
        "pf", "esi", "professional_tax", "tds", "loan_deduction",
        "advance_salary_recovery", "leave_deduction", "late_attendance_deduction",
        "penalty_deduction", "other_deductions",
    ]:
        data[field] = getattr(slip, field, 0)
    return data
