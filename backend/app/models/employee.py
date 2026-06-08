from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    employee_id: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True, index=True)
    employee_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    designation: Mapped[str] = mapped_column(String(120), nullable=False)
    department: Mapped[str] = mapped_column(String(120), nullable=False)
    joining_date: Mapped[date] = mapped_column(Date, nullable=False)
    employment_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reporting_manager: Mapped[str | None] = mapped_column(String(120), nullable=True)
    project_lead: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tech_owner: Mapped[str | None] = mapped_column(String(120), nullable=True)
    company_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employment_status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    manager_name: Mapped[str | None] = mapped_column(String(120), nullable=True)

    title: Mapped[str | None] = mapped_column(String(20), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    middle_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    father_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(80), nullable=True)
    marital_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    anniversary_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    number_of_children: Mapped[int | None] = mapped_column(Integer, nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(10), nullable=True)
    profile_photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    pan_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    uan_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pf_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    work_location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    aadhaar_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    passport_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    passport_issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    passport_expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    passport_issue_place: Mapped[str | None] = mapped_column(String(120), nullable=True)

    mobile_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    alternate_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    personal_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    user = relationship("User", back_populates="employee_profile")
    addresses = relationship("EmployeeAddress", back_populates="employee", cascade="all, delete-orphan")
    documents = relationship("EmployeeDocument", back_populates="employee", cascade="all, delete-orphan")
    family_members = relationship("EmployeeFamily", back_populates="employee", cascade="all, delete-orphan")
    bank_details = relationship("EmployeeBankDetail", back_populates="employee", uselist=False, cascade="all, delete-orphan")
    education = relationship("EmployeeEducation", back_populates="employee", cascade="all, delete-orphan")
    experience = relationship("EmployeeExperience", back_populates="employee", cascade="all, delete-orphan")
    skills = relationship("EmployeeSkills", back_populates="employee", uselist=False, cascade="all, delete-orphan")
    languages = relationship("EmployeeLanguage", back_populates="employee", cascade="all, delete-orphan")
    interests = relationship("EmployeeInterest", back_populates="employee", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        parts = [self.first_name, self.middle_name, self.last_name]
        name = " ".join(p for p in parts if p)
        if name:
            return name
        return self.user.name if self.user else ""
