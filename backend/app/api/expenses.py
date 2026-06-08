import os
import uuid
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, require_admin
from app.core.request_utils import get_client_ip
from app.db.session import get_db
from app.models.employee import Employee
from app.models.expense import Expense, ExpenseAttachment
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseListResponse, ExpenseResponse, ExpenseReview
from app.utils.file_validation import validate_upload_file
from app.services.audit_service import log_action
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/expenses", tags=["expenses"])
UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "expenses"


def _to_response(exp: Expense) -> ExpenseResponse:
    return ExpenseResponse(
        id=exp.id,
        employee_id=exp.employee_id,
        employee_name=exp.employee.full_name if exp.employee else None,
        expense_date=exp.expense_date,
        expense_type=exp.expense_type,
        expense_category=exp.expense_category,
        amount=exp.amount,
        description=exp.description,
        status=exp.status,
        payment_date=exp.payment_date,
        transaction_id=exp.transaction_id,
        admin_remarks=exp.admin_remarks,
        attachments=[a.file_path for a in exp.attachments],
        created_at=exp.created_at,
    )


@router.get("", response_model=ExpenseListResponse)
def list_expenses(
    search: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Expense).options(joinedload(Expense.employee), joinedload(Expense.attachments))
    if current_user.role != "admin":
        employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not employee:
            return ExpenseListResponse(items=[], total=0, page=page, page_size=page_size)
        query = query.filter(Expense.employee_id == employee.id)
    if status:
        query = query.filter(Expense.status == status)
    if search:
        query = query.filter(Expense.description.ilike(f"%{search.lower()}%"))
    query = query.order_by(Expense.created_at.desc())
    total = query.count()
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    return ExpenseListResponse(items=[_to_response(e) for e in rows], total=total, page=page, page_size=page_size)


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def submit_expense(
    expense_date: str = Form(...),
    expense_type: str = Form(...),
    expense_category: str = Form(...),
    amount: str = Form(...),
    description: str = Form(""),
    bill: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import date as date_cls

    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    exp = Expense(
        employee_id=employee.id,
        expense_date=date_cls.fromisoformat(expense_date),
        expense_type=expense_type,
        expense_category=expense_category,
        amount=Decimal(amount),
        description=description or None,
    )
    db.add(exp)
    db.flush()
    if bill and bill.filename:
        bill_content = await bill.read()
        validate_upload_file(bill.filename, bill_content)
        UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
        ext = os.path.splitext(bill.filename)[1]
        stored = f"{uuid.uuid4().hex}{ext}"
        path = UPLOAD_ROOT / stored
        path.write_bytes(bill_content)
        db.add(ExpenseAttachment(expense_id=exp.id, file_path=f"uploads/expenses/{stored}", original_filename=bill.filename))
    db.commit()
    exp = db.query(Expense).options(joinedload(Expense.employee), joinedload(Expense.attachments)).filter(Expense.id == exp.id).first()
    return _to_response(exp)


@router.patch("/admin/{expense_id}", response_model=ExpenseResponse)
def review_expense(
    expense_id: int,
    payload: ExpenseReview,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    exp = db.query(Expense).options(joinedload(Expense.employee), joinedload(Expense.attachments)).filter(Expense.id == expense_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    exp.status = payload.status
    exp.admin_remarks = payload.admin_remarks
    exp.reviewed_by = current_user.id
    if payload.status == "paid":
        exp.payment_date = payload.payment_date
        exp.transaction_id = payload.transaction_id
    db.commit()
    action = f"Expense {payload.status.title()}"
    log_action(db, user=current_user, action=action, entity_type="expense", entity_id=exp.id, ip_address=get_client_ip(request))
    db.commit()
    if exp.employee and exp.employee.user:
        email = exp.employee.user.email
        if payload.status == "approved":
            NotificationService.expense_approved(email, str(exp.amount))
        elif payload.status == "rejected":
            NotificationService.expense_rejected(email, payload.admin_remarks)
        elif payload.status == "paid":
            NotificationService.expense_approved(email, str(exp.amount))
    exp = db.query(Expense).options(joinedload(Expense.employee), joinedload(Expense.attachments)).filter(Expense.id == expense_id).first()
    return _to_response(exp)


@router.delete("/admin/{expense_id}")
def delete_expense(
    expense_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    exp = db.query(Expense).filter(Expense.id == expense_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(exp)
    log_action(db, user=current_user, action="Expense Deleted", entity_type="expense", entity_id=expense_id, ip_address=get_client_ip(request))
    db.commit()
    return {"message": "Expense deleted"}
