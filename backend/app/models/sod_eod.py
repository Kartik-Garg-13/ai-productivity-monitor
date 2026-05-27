from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SODEntry(Base):
    __tablename__ = "sod_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    submitted_for_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(80), nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    subcategory: Mapped[str] = mapped_column(String(120), nullable=True)
    project: Mapped[str] = mapped_column(String(120), nullable=False)
    work_type: Mapped[str] = mapped_column(String(30), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    duration: Mapped[str] = mapped_column(String(30), nullable=False)
    completion_percentage: Mapped[int] = mapped_column(Integer, nullable=False)
    ticket_number: Mapped[str] = mapped_column(String(80), nullable=True)
    review_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    admin_remarks: Mapped[str] = mapped_column(Text, nullable=True)
    day_flag: Mapped[str] = mapped_column(String(20), default="full-day", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class EODEntry(Base):
    __tablename__ = "eod_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    submitted_for_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    morning_activity: Mapped[str] = mapped_column(Text, nullable=False)
    incomplete_reason: Mapped[str] = mapped_column(Text, nullable=True)
    completion_remarks: Mapped[str] = mapped_column(Text, nullable=True)
    review_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    admin_remarks: Mapped[str] = mapped_column(Text, nullable=True)
    day_flag: Mapped[str] = mapped_column(String(20), default="full-day", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
