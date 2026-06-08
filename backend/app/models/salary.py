from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SalarySlip(Base):
    __tablename__ = "salary_slips"
    __table_args__ = (UniqueConstraint("employee_id", "month", name="uq_salary_employee_month"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    month: Mapped[date] = mapped_column(Date, nullable=False)
    basic_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    hra: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    bonus: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    deductions: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    net_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="generated", nullable=False)
    pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    da: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    conveyance_allowance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    medical_allowance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    internet_allowance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    special_allowance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    incentive: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    overtime_pay: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    project_bonus: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    other_earnings: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    total_earnings: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    pf: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    esi: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    professional_tax: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    tds: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    loan_deduction: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    advance_salary_recovery: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    leave_deduction: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    late_attendance_deduction: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    penalty_deduction: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    other_deductions: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    gross_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    in_hand_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    amount_in_words: Mapped[str | None] = mapped_column(Text, nullable=True)
    payroll_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    bank_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    attendance_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    leave_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    employee_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    company_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    transaction_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    employee = relationship("Employee")

    def earnings_fields(self) -> list[tuple[str, Decimal]]:
        return [
            ("Basic Salary", self.basic_salary),
            ("House Rent Allowance", self.hra),
            ("Dearness Allowance", self.da),
            ("Conveyance Allowance", self.conveyance_allowance),
            ("Medical Allowance", self.medical_allowance),
            ("Internet Allowance", self.internet_allowance),
            ("Special Allowance", self.special_allowance),
            ("Performance Bonus", self.bonus),
            ("Incentives", self.incentive),
            ("Overtime Pay", self.overtime_pay),
            ("Project Bonus", self.project_bonus),
            ("Other Earnings", self.other_earnings),
        ]

    def deduction_fields(self) -> list[tuple[str, Decimal]]:
        return [
            ("Provident Fund", self.pf),
            ("Employee State Insurance", self.esi),
            ("Professional Tax", self.professional_tax),
            ("Income Tax (TDS)", self.tds),
            ("Loan Deduction", self.loan_deduction),
            ("Advance Salary Recovery", self.advance_salary_recovery),
            ("Leave Deduction", self.leave_deduction),
            ("Late Attendance Deduction", self.late_attendance_deduction),
            ("Penalty Deduction", self.penalty_deduction),
            ("Other Deductions", self.other_deductions),
        ]
