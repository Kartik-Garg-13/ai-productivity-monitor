from pathlib import Path

from sqlalchemy import inspect, text

from app.core.leave_constants import DEFAULT_LEAVE_TOTALS, LEAVE_TYPES
from app.db.base import Base


def _run_sql_file(conn, path: Path) -> None:
    if not path.exists():
        return
    sql = path.read_text(encoding="utf-8")
    for statement in sql.split(";"):
        stmt = statement.strip()
        if stmt:
            conn.execute(text(stmt))


def _migrate_legacy_leave_balances(engine) -> None:
    from sqlalchemy.orm import Session

    from app.models.employee import Employee
    from app.models.leave import LeaveBalance

    with Session(engine) as db:
        employees = db.query(Employee.id).all()
        for (eid,) in employees:
            rows = db.query(LeaveBalance).filter(LeaveBalance.employee_id == eid).all()
            if not rows:
                for lt in LEAVE_TYPES:
                    total = DEFAULT_LEAVE_TOTALS[lt]
                    db.add(
                        LeaveBalance(
                            employee_id=eid,
                            leave_type=lt,
                            total_leave=total,
                            leave_taken=0,
                            remaining_leave=total,
                        )
                    )
                continue
            types = {r.leave_type for r in rows}
            if types <= {"annual"} and len(rows) == 1:
                old = rows[0]
                paid_taken = old.leave_taken
                db.delete(old)
                db.flush()
                for lt in LEAVE_TYPES:
                    total = DEFAULT_LEAVE_TOTALS[lt]
                    taken = min(paid_taken, total) if lt == "paid" else 0
                    db.add(
                        LeaveBalance(
                            employee_id=eid,
                            leave_type=lt,
                            total_leave=total,
                            leave_taken=taken,
                            remaining_leave=max(0, total - taken),
                        )
                    )
            elif len(rows) < len(LEAVE_TYPES):
                existing_types = {r.leave_type for r in rows}
                for lt in LEAVE_TYPES:
                    if lt not in existing_types:
                        total = DEFAULT_LEAVE_TOTALS[lt]
                        db.add(
                            LeaveBalance(
                                employee_id=eid,
                                leave_type=lt,
                                total_leave=total,
                                leave_taken=0,
                                remaining_leave=total,
                            )
                        )
        db.commit()


def _ensure_leave_balance_unique_constraint(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE leave_balances DROP CONSTRAINT IF EXISTS uq_leave_balance_employee_type"))
        conn.execute(
            text(
                "ALTER TABLE leave_balances ADD CONSTRAINT uq_leave_balance_employee_type "
                "UNIQUE (employee_id, leave_type)"
            )
        )


def _seed_company_settings(engine) -> None:
    from sqlalchemy.orm import Session

    from app.models.company_settings import CompanySettings

    with Session(engine) as db:
        if not db.query(CompanySettings).first():
            db.add(
                CompanySettings(
                    company_name="Goldilocks Tech",
                    company_address="Bangalore, Karnataka, India",
                )
            )
            db.commit()


def _backfill_salary_slips(engine) -> None:
    from sqlalchemy.orm import Session

    from app.models.salary import SalarySlip

    with Session(engine) as db:
        slips = db.query(SalarySlip).all()
        for slip in slips:
            if not slip.total_earnings or float(slip.total_earnings) == 0:
                slip.total_earnings = slip.basic_salary + slip.hra + slip.bonus
            if not slip.total_deductions or float(slip.total_deductions) == 0:
                slip.total_deductions = slip.deductions
            if not slip.gross_salary or float(slip.gross_salary) == 0:
                slip.gross_salary = slip.total_earnings or slip.net_salary
            if not slip.in_hand_salary or float(slip.in_hand_salary) == 0:
                slip.in_hand_salary = slip.net_salary
            if not slip.payroll_year:
                slip.payroll_year = slip.month.year
        db.commit()


def run_migrations(engine) -> None:
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)

    if "attendance" in inspector.get_table_names():
        columns = {col["name"] for col in inspector.get_columns("attendance")}
        if "ip_address" not in columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE attendance ADD COLUMN ip_address VARCHAR(45)"))

    if "employees" in inspector.get_table_names():
        migration_path = Path(__file__).resolve().parents[2] / "sql" / "migrations" / "002_employee_profile.sql"
        with engine.begin() as conn:
            _run_sql_file(conn, migration_path)

        emp_columns = {col["name"] for col in inspector.get_columns("employees")}
        with engine.begin() as conn:
            if "employment_status" not in emp_columns:
                conn.execute(
                    text("ALTER TABLE employees ADD COLUMN employment_status VARCHAR(30) DEFAULT 'active'")
                )
                conn.execute(text("UPDATE employees SET employment_status = 'active' WHERE employment_status IS NULL"))

    phase2_path = Path(__file__).resolve().parents[2] / "sql" / "migrations" / "003_phase2.sql"
    with engine.begin() as conn:
        _run_sql_file(conn, phase2_path)

    phase4_path = Path(__file__).resolve().parents[2] / "sql" / "migrations" / "004_payroll_leave_upgrade.sql"
    with engine.begin() as conn:
        _run_sql_file(conn, phase4_path)

    _seed_company_settings(engine)
    _migrate_legacy_leave_balances(engine)
    _ensure_leave_balance_unique_constraint(engine)
    _backfill_salary_slips(engine)
