from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EmployeeEducation(Base):
    __tablename__ = "employee_education"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    degree: Mapped[str | None] = mapped_column(String(120), nullable=True)
    institute: Mapped[str | None] = mapped_column(String(200), nullable=True)
    board_university: Mapped[str | None] = mapped_column(String(200), nullable=True)
    year_of_passing: Mapped[str | None] = mapped_column(String(10), nullable=True)
    percentage: Mapped[str | None] = mapped_column(String(20), nullable=True)
    major_subjects: Mapped[str | None] = mapped_column(String(255), nullable=True)

    employee = relationship("Employee", back_populates="education")
