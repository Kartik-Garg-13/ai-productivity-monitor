from datetime import date

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.employee import Employee
from app.models.employee_skills import EmployeeSkills
from app.models.leave import LeaveBalance
from app.models.user import User


def seed_admin(db: Session) -> None:
    if db.query(User).filter(User.email == "admin@goldilocks.tech").first():
        return
    admin = User(
        name="System Admin",
        email="admin@goldilocks.tech",
        password=get_password_hash("Admin@123"),
        role="admin",
        department="Management",
    )
    db.add(admin)
    db.commit()


def seed_default_employee(db: Session) -> None:
    if db.query(User).filter(User.email == "employee@goldilocks.tech").first():
        return

    user = User(
        name="Default Employee",
        email="employee@goldilocks.tech",
        password=get_password_hash("Employee@123"),
        role="employee",
        department="Software Development",
    )
    db.add(user)
    db.flush()

    employee = Employee(
        user_id=user.id,
        employee_code=f"GLD-{user.id:05d}",
        employee_id=f"EMP-{user.id:05d}",
        designation="Software Developer",
        department="Software Development",
        joining_date=date.today(),
        reporting_manager="System Admin",
        manager_name="System Admin",
        company_email="employee@goldilocks.tech",
        employment_status="active",
        employment_type="full-time",
        first_name="Default",
        last_name="Employee",
        title="Mr",
        gender="Male",
        nationality="Indian",
        mobile_number="+91-9999999999",
    )
    db.add(employee)
    db.flush()
    db.add(LeaveBalance(employee_id=employee.id))
    db.add(
        EmployeeSkills(
            employee_id=employee.id,
            technical_skills="Python, JavaScript",
            programming_languages="Python, JavaScript",
            frameworks="React, FastAPI",
        )
    )
    db.commit()
