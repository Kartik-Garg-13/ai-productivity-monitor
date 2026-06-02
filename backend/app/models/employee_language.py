from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EmployeeLanguage(Base):
    __tablename__ = "employee_languages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(80), nullable=False)
    can_speak: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_write: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_understand: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    employee = relationship("Employee", back_populates="languages")
