from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EmployeeInterest(Base):
    __tablename__ = "employee_interests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    interest: Mapped[str] = mapped_column(String(80), nullable=False)

    employee = relationship("Employee", back_populates="interests")
