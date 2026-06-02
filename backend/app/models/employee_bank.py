from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EmployeeBankDetail(Base):
    __tablename__ = "employee_bank_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    bank_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    account_number: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ifsc_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    branch_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    branch_address: Mapped[str | None] = mapped_column(Text, nullable=True)

    employee = relationship("Employee", back_populates="bank_details")
