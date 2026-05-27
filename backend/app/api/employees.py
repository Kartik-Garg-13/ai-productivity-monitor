from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.employee import Employee
from app.models.leave import LeaveBalance
from app.models.user import User
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services.email_service import send_email

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("", response_model=EmployeeResponse)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    user = User(
        name=payload.name,
        email=payload.email,
        password=get_password_hash(payload.password),
        role="employee",
        department=payload.department,
    )
    db.add(user)
    db.flush()
    employee = Employee(
        user_id=user.id,
        employee_code=f"GLD-{user.id:05d}",
        designation=payload.designation,
        department=payload.department,
        joining_date=payload.joining_date,
        manager_name=payload.manager_name,
    )
    db.add(employee)
    db.add(LeaveBalance(employee_id=employee.id))
    db.commit()
    db.refresh(employee)

    send_email(
        subject="Welcome to Goldilocks Tech",
        recipient=user.email,
        body=f"Hi {user.name}, your employee account has been created.",
    )
    return EmployeeResponse(
        id=employee.id,
        employee_code=employee.employee_code,
        name=user.name,
        email=user.email,
        designation=employee.designation,
        department=employee.department,
        joining_date=employee.joining_date,
        manager_name=employee.manager_name,
    )


@router.get("", response_model=list[EmployeeResponse])
def list_employees(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    employees = db.query(Employee).join(User, Employee.user_id == User.id).all()
    return [
        EmployeeResponse(
            id=emp.id,
            employee_code=emp.employee_code,
            name=emp.user.name,
            email=emp.user.email,
            designation=emp.designation,
            department=emp.department,
            joining_date=emp.joining_date,
            manager_name=emp.manager_name,
        )
        for emp in employees
    ]


@router.get("/profile", response_model=EmployeeResponse)
def my_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    return EmployeeResponse(
        id=employee.id,
        employee_code=employee.employee_code,
        name=current_user.name,
        email=current_user.email,
        designation=employee.designation,
        department=employee.department,
        joining_date=employee.joining_date,
        manager_name=employee.manager_name,
    )


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int, payload: EmployeeUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    user = db.query(User).filter(User.id == employee.user_id).first()
    if payload.name:
        user.name = payload.name
    for field in ["designation", "department", "joining_date", "manager_name"]:
        value = getattr(payload, field)
        if value is not None:
            setattr(employee, field, value)
    db.commit()
    db.refresh(employee)
    return EmployeeResponse(
        id=employee.id,
        employee_code=employee.employee_code,
        name=user.name,
        email=user.email,
        designation=employee.designation,
        department=employee.department,
        joining_date=employee.joining_date,
        manager_name=employee.manager_name,
    )


@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    user = db.query(User).filter(User.id == employee.user_id).first()
    db.delete(employee)
    if user:
        db.delete(user)
    db.commit()
    return {"message": "Employee deleted"}
