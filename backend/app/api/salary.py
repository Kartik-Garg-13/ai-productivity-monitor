from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, require_admin
from app.core.request_utils import get_client_ip
from app.db.session import get_db
from app.models.employee import Employee
from app.models.salary import SalarySlip
from app.models.user import User
from app.schemas.salary import (
    SalaryListResponse,
    SalaryMarkPaid,
    SalarySlipCreate,
    SalarySlipResponse,
    SalarySlipUpdate,
)
from app.services.audit_service import log_action
from app.services.notification_service import NotificationService
from app.services.salary_pdf_service import generate_salary_pdf
from app.services.salary_service import apply_calculation_to_slip, calculate_payroll, payload_from_slip

router = APIRouter(prefix="/salary", tags=["salary"])

UPLOADS_ROOT = Path(__file__).resolve().parents[2] / "uploads"


def _to_response(slip: SalarySlip) -> SalarySlipResponse:
    return SalarySlipResponse(
        id=slip.id,
        employee_id=slip.employee_id,
        employee_name=slip.employee.full_name if slip.employee else (slip.employee_snapshot or {}).get("name"),
        employee_code=slip.employee.employee_code if slip.employee else (slip.employee_snapshot or {}).get("employee_code"),
        month=slip.month,
        basic_salary=slip.basic_salary,
        hra=slip.hra,
        bonus=slip.bonus,
        deductions=slip.deductions,
        net_salary=slip.net_salary,
        status=slip.status,
        pdf_path=slip.pdf_path,
        paid_at=slip.paid_at,
        created_at=slip.created_at,
        da=getattr(slip, "da", 0) or 0,
        conveyance_allowance=getattr(slip, "conveyance_allowance", 0) or 0,
        medical_allowance=getattr(slip, "medical_allowance", 0) or 0,
        internet_allowance=getattr(slip, "internet_allowance", 0) or 0,
        special_allowance=getattr(slip, "special_allowance", 0) or 0,
        incentive=getattr(slip, "incentive", 0) or 0,
        overtime_pay=getattr(slip, "overtime_pay", 0) or 0,
        project_bonus=getattr(slip, "project_bonus", 0) or 0,
        other_earnings=getattr(slip, "other_earnings", 0) or 0,
        total_earnings=getattr(slip, "total_earnings", 0) or slip.net_salary,
        pf=getattr(slip, "pf", 0) or 0,
        esi=getattr(slip, "esi", 0) or 0,
        professional_tax=getattr(slip, "professional_tax", 0) or 0,
        tds=getattr(slip, "tds", 0) or 0,
        loan_deduction=getattr(slip, "loan_deduction", 0) or 0,
        advance_salary_recovery=getattr(slip, "advance_salary_recovery", 0) or 0,
        leave_deduction=getattr(slip, "leave_deduction", 0) or 0,
        late_attendance_deduction=getattr(slip, "late_attendance_deduction", 0) or 0,
        penalty_deduction=getattr(slip, "penalty_deduction", 0) or 0,
        other_deductions=getattr(slip, "other_deductions", 0) or 0,
        total_deductions=getattr(slip, "total_deductions", 0) or slip.deductions,
        gross_salary=getattr(slip, "gross_salary", 0) or slip.net_salary,
        in_hand_salary=getattr(slip, "in_hand_salary", 0) or slip.net_salary,
        amount_in_words=getattr(slip, "amount_in_words", None),
        payroll_year=getattr(slip, "payroll_year", None),
        generated_at=getattr(slip, "generated_at", None),
        bank_snapshot=getattr(slip, "bank_snapshot", None),
        attendance_snapshot=getattr(slip, "attendance_snapshot", None),
        leave_snapshot=getattr(slip, "leave_snapshot", None),
        employee_snapshot=getattr(slip, "employee_snapshot", None),
        company_snapshot=getattr(slip, "company_snapshot", None),
        payment_date=getattr(slip, "payment_date", None),
        transaction_id=getattr(slip, "transaction_id", None),
    )


def _load_employee(db: Session, employee_id: int) -> Employee | None:
    return (
        db.query(Employee)
        .options(joinedload(Employee.bank_details), joinedload(Employee.user))
        .filter(Employee.id == employee_id)
        .first()
    )


def _generate_slip_pdf(db: Session, slip: SalarySlip, employee: Employee) -> None:
    slip.pdf_path = generate_salary_pdf(slip, employee)


@router.get("", response_model=SalaryListResponse)
def list_salary_slips(
    search: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(SalarySlip).options(joinedload(SalarySlip.employee))
    if current_user.role != "admin":
        employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not employee:
            return SalaryListResponse(items=[], total=0, page=page, page_size=page_size)
        query = query.filter(SalarySlip.employee_id == employee.id)
    if status:
        query = query.filter(SalarySlip.status == status)
    if search:
        query = query.join(Employee).filter(Employee.employee_code.ilike(f"%{search}%"))
    query = query.order_by(SalarySlip.month.desc())
    total = query.count()
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    return SalaryListResponse(items=[_to_response(s) for s in rows], total=total, page=page, page_size=page_size)


@router.get("/{slip_id}", response_model=SalarySlipResponse)
def get_salary_slip(
    slip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    slip = db.query(SalarySlip).options(joinedload(SalarySlip.employee)).filter(SalarySlip.id == slip_id).first()
    if not slip:
        raise HTTPException(status_code=404, detail="Salary slip not found")
    if current_user.role != "admin":
        employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not employee or slip.employee_id != employee.id:
            raise HTTPException(status_code=403, detail="Access denied")
    return _to_response(slip)


@router.get("/{slip_id}/preview", response_model=SalarySlipResponse)
def preview_salary_slip(slip_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_salary_slip(slip_id, db, current_user)


@router.get("/{slip_id}/download")
def download_salary_slip(
    slip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    slip = db.query(SalarySlip).filter(SalarySlip.id == slip_id).first()
    if not slip:
        raise HTTPException(status_code=404, detail="Salary slip not found")
    if current_user.role != "admin":
        employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not employee or slip.employee_id != employee.id:
            raise HTTPException(status_code=403, detail="Access denied")
    if not slip.pdf_path:
        raise HTTPException(status_code=404, detail="PDF not generated")
    file_path = UPLOADS_ROOT.parent / slip.pdf_path if not slip.pdf_path.startswith("uploads") else UPLOADS_ROOT.parent / slip.pdf_path
    if not file_path.exists():
        file_path = UPLOADS_ROOT / Path(slip.pdf_path).name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF file missing")
    return FileResponse(str(file_path), filename=file_path.name, media_type="application/pdf")


@router.post("/generate", response_model=SalarySlipResponse, status_code=status.HTTP_201_CREATED)
def generate_salary(
    payload: SalarySlipCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    employee = _load_employee(db, payload.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    existing = (
        db.query(SalarySlip)
        .filter(SalarySlip.employee_id == payload.employee_id, SalarySlip.month == payload.month)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Salary slip already exists for this month")

    data = payload.model_dump()
    if data.get("deductions") and not any(data.get(k) for k in ("pf", "tds", "leave_deduction")):
        data["other_deductions"] = data.get("other_deductions", 0) + float(data["deductions"])

    calc = calculate_payroll(
        db,
        employee,
        payload.month,
        data,
        apply_auto_leave_deduction=payload.apply_auto_leave_deduction,
    )
    slip = SalarySlip(employee_id=payload.employee_id, month=payload.month, status="generated")
    apply_calculation_to_slip(slip, calc)
    db.add(slip)
    db.flush()
    _generate_slip_pdf(db, slip, employee)
    db.commit()
    db.refresh(slip)
    log_action(
        db,
        user=current_user,
        action="Salary Slip Generated",
        entity_type="salary",
        entity_id=slip.id,
        ip_address=get_client_ip(request),
    )
    db.commit()
    if employee.user:
        NotificationService.salary_slip_generated(employee.user.email, slip.month.strftime("%B %Y"))
    slip = db.query(SalarySlip).options(joinedload(SalarySlip.employee)).filter(SalarySlip.id == slip.id).first()
    return _to_response(slip)


@router.patch("/{slip_id}", response_model=SalarySlipResponse)
def update_salary_slip(
    slip_id: int,
    payload: SalarySlipUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    slip = db.query(SalarySlip).options(joinedload(SalarySlip.employee)).filter(SalarySlip.id == slip_id).first()
    if not slip:
        raise HTTPException(status_code=404, detail="Salary slip not found")
    employee = _load_employee(db, slip.employee_id)
    data = payload_from_slip(slip)
    for k, v in payload.model_dump(exclude_unset=True).items():
        if k != "apply_auto_leave_deduction" and v is not None:
            data[k] = v
    calc = calculate_payroll(
        db,
        employee,
        slip.month,
        data,
        apply_auto_leave_deduction=payload.apply_auto_leave_deduction,
    )
    apply_calculation_to_slip(slip, calc)
    _generate_slip_pdf(db, slip, employee)
    db.commit()
    log_action(db, user=current_user, action="Salary Slip Updated", entity_type="salary", entity_id=slip.id, ip_address=get_client_ip(request))
    db.commit()
    return _to_response(slip)


@router.post("/{slip_id}/regenerate", response_model=SalarySlipResponse)
def regenerate_salary_slip(
    slip_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    slip = db.query(SalarySlip).options(joinedload(SalarySlip.employee)).filter(SalarySlip.id == slip_id).first()
    if not slip:
        raise HTTPException(status_code=404, detail="Salary slip not found")
    employee = _load_employee(db, slip.employee_id)
    data = payload_from_slip(slip)
    calc = calculate_payroll(db, employee, slip.month, data, apply_auto_leave_deduction=True)
    apply_calculation_to_slip(slip, calc)
    _generate_slip_pdf(db, slip, employee)
    db.commit()
    log_action(db, user=current_user, action="Salary Slip Regenerated", entity_type="salary", entity_id=slip.id, ip_address=get_client_ip(request))
    db.commit()
    return _to_response(slip)


@router.patch("/{slip_id}/paid", response_model=SalarySlipResponse)
def mark_paid(
    slip_id: int,
    payload: SalaryMarkPaid,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    slip = db.query(SalarySlip).options(joinedload(SalarySlip.employee)).filter(SalarySlip.id == slip_id).first()
    if not slip:
        raise HTTPException(status_code=404, detail="Salary slip not found")
    slip.status = "paid"
    slip.paid_at = datetime.utcnow()
    if payload.payment_date:
        slip.payment_date = payload.payment_date
    if payload.transaction_id:
        slip.transaction_id = payload.transaction_id
    db.commit()
    log_action(db, user=current_user, action="Salary Paid", entity_type="salary", entity_id=slip.id, ip_address=get_client_ip(request))
    db.commit()
    if slip.employee and slip.employee.user:
        NotificationService.salary_paid(
            slip.employee.user.email, slip.month.strftime("%B %Y"), str(slip.net_salary)
        )
    return _to_response(slip)


@router.delete("/{slip_id}")
def delete_salary(
    slip_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    slip = db.query(SalarySlip).filter(SalarySlip.id == slip_id).first()
    if not slip:
        raise HTTPException(status_code=404, detail="Salary slip not found")
    db.delete(slip)
    log_action(db, user=current_user, action="Salary Slip Deleted", entity_type="salary", entity_id=slip_id, ip_address=get_client_ip(request))
    db.commit()
    return {"message": "Salary slip deleted"}
