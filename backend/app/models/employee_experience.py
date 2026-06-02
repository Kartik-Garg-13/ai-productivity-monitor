from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EmployeeExperience(Base):
    __tablename__ = "employee_experience"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    company_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True)
    designation: Mapped[str | None] = mapped_column(String(120), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    reason_for_leaving: Mapped[str | None] = mapped_column(Text, nullable=True)

    employee = relationship("Employee", back_populates="experience")
