from pathlib import Path

from sqlalchemy import inspect, text

from app.db.base import Base


def _run_sql_file(conn, path: Path) -> None:
    if not path.exists():
        return
    sql = path.read_text(encoding="utf-8")
    for statement in sql.split(";"):
        stmt = statement.strip()
        if stmt:
            conn.execute(text(stmt))


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
