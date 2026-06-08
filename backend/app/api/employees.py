from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, require_admin
from app.core.request_utils import get_client_ip
from app.db.session import get_db
from app.models.employee import Employee
from app.models.user import User
from app.schemas.employee import (
    EmployeeListResponse,
    EmployeeProfileCreate,
    EmployeeProfileFull,
    EmployeeProfileUpdate,
    EmployeeResponse,
)
from app.utils.file_validation import validate_upload_file
from app.services.audit_service import log_action
from app.services.employee_service import (
    build_profile_response,
    create_employee_profile,
    delete_employee_profile,
    get_employee_full,
    list_employees,
    save_document,
    update_employee_profile,
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/employees", tags=["employees"])


def _legacy_response(employee: Employee, user: User) -> EmployeeResponse:
    return EmployeeResponse(
        id=employee.id,
        employee_code=employee.employee_code,
        name=employee.full_name or user.name,
        email=user.email,
        designation=employee.designation,
        department=employee.department,
        joining_date=employee.joining_date,
        manager_name=employee.reporting_manager or employee.manager_name,
    )


@router.get("/profile", response_model=EmployeeResponse)
def my_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).options(joinedload(Employee.user)).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    return _legacy_response(employee, current_user)


@router.get("", response_model=EmployeeListResponse)
def list_employees_api(
    search: str | None = None,
    department: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    items, total = list_employees(db, search, department, page, page_size)
    return EmployeeListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{employee_id}/full", response_model=EmployeeProfileFull)
def get_employee_full_api(employee_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    employee = get_employee_full(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return build_profile_response(db, employee)


@router.get("/{employee_id}", response_model=EmployeeProfileFull)
def get_employee(employee_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    employee = get_employee_full(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return build_profile_response(db, employee)


@router.post("", response_model=EmployeeProfileFull, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeProfileCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        employee = create_employee_profile(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    employee = get_employee_full(db, employee.id)
    NotificationService.employee_created(str(payload.company_email), employee.full_name)
    log_action(db, user=current_user, action="Employee Created", entity_type="employee", entity_id=employee.id, ip_address=get_client_ip(request))
    db.commit()
    return build_profile_response(db, employee)


@router.put("/{employee_id}", response_model=EmployeeProfileFull)
def update_employee(
    employee_id: int, payload: EmployeeProfileUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)
):
    employee = get_employee_full(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    try:
        update_employee_profile(db, employee, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    employee = get_employee_full(db, employee_id)
    return build_profile_response(db, employee)


@router.post("/{employee_id}/documents")
async def upload_document(
    employee_id: int,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    content = await file.read()
    validate_upload_file(file.filename, content, image_only=document_type == "profile_photo")
    doc = save_document(db, employee_id, document_type, file.filename or "upload", content)
    return {"id": doc.id, "document_type": doc.document_type, "file_path": doc.file_path}


@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    employee = db.query(Employee).options(joinedload(Employee.user)).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    delete_employee_profile(db, employee)
    log_action(db, user=current_user, action="Employee Deleted", entity_type="employee", entity_id=employee_id, ip_address=get_client_ip(request))
    db.commit()
    return {"message": "Employee deleted successfully"}
