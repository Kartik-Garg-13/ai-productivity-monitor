from datetime import date

from pydantic import BaseModel, EmailStr


class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    designation: str
    department: str
    joining_date: date
    manager_name: str | None = None


class EmployeeUpdate(BaseModel):
    name: str | None = None
    designation: str | None = None
    department: str | None = None
    joining_date: date | None = None
    manager_name: str | None = None


class EmployeeResponse(BaseModel):
    id: int
    employee_code: str
    name: str
    email: EmailStr
    designation: str
    department: str
    joining_date: date
    manager_name: str | None = None

    class Config:
        from_attributes = True
