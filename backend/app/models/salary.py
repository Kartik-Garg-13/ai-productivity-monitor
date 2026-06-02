from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
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

    employee = relationship("Employee")
