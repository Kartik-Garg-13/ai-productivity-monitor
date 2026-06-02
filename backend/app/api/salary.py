from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, require_admin
from app.core.request_utils import get_client_ip
from app.db.session import get_db
from app.models.employee import Employee
from app.models.salary import SalarySlip
from app.models.user import User
from app.schemas.salary import SalaryListResponse, SalaryMarkPaid, SalarySlipCreate, SalarySlipResponse
from app.services.audit_service import log_action
from app.services.notification_service import NotificationService
from app.services.salary_pdf_service import generate_salary_pdf

router = APIRouter(prefix="/salary", tags=["salary"])


def _calc_net(basic, hra, bonus, deductions):
    return basic + hra + bonus - deductions


def _to_response(slip: SalarySlip) -> SalarySlipResponse:
    return SalarySlipResponse(
        id=slip.id,
        employee_id=slip.employee_id,
        employee_name=slip.employee.full_name if slip.employee else None,
        employee_code=slip.employee.employee_code if slip.employee else None,
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
    )


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


@router.post("/generate", response_model=SalarySlipResponse, status_code=status.HTTP_201_CREATED)
def generate_salary(
    payload: SalarySlipCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    employee = db.query(Employee).filter(Employee.id == payload.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    existing = (
        db.query(SalarySlip)
        .filter(SalarySlip.employee_id == payload.employee_id, SalarySlip.month == payload.month)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Salary slip already exists for this month")
    net = _calc_net(payload.basic_salary, payload.hra, payload.bonus, payload.deductions)
    slip = SalarySlip(
        employee_id=payload.employee_id,
        month=payload.month,
        basic_salary=payload.basic_salary,
        hra=payload.hra,
        bonus=payload.bonus,
        deductions=payload.deductions,
        net_salary=net,
        status="generated",
    )
    db.add(slip)
    db.flush()
    slip.pdf_path = generate_salary_pdf(slip, employee)
    db.commit()
    db.refresh(slip)
    log_action(db, user=current_user, action="Salary Slip Generated", entity_type="salary", entity_id=slip.id, ip_address=get_client_ip(request))
    db.commit()
    if employee.user:
        NotificationService.salary_slip_generated(employee.user.email, slip.month.strftime("%B %Y"))
    slip = db.query(SalarySlip).options(joinedload(SalarySlip.employee)).filter(SalarySlip.id == slip.id).first()
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
