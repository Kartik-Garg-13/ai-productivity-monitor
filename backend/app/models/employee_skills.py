from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EmployeeSkills(Base):
    __tablename__ = "employee_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    certification_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    certification_provider: Mapped[str | None] = mapped_column(String(200), nullable=True)
    certification_issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    certification_expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    technical_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    soft_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    programming_languages: Mapped[str | None] = mapped_column(Text, nullable=True)
    frameworks: Mapped[str | None] = mapped_column(Text, nullable=True)
    tools: Mapped[str | None] = mapped_column(Text, nullable=True)

    employee = relationship("Employee", back_populates="skills")
