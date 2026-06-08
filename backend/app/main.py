from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import (
    announcements,
    attendance,
    audit,
    auth,
    company_documents,
    company_settings,
    dashboard,
    employees,
    expenses,
    holidays,
    leave,
    projects,
    salary,
    sod_eod,
    tasks,
)
from app.core.config import get_settings
from app.db.init_db import seed_admin, seed_default_employee
from app.db.migrate import run_migrations
from app.db.session import SessionLocal, engine
import app.models  # noqa: F401  # register all SQLAlchemy models (do not shadow API modules)

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    run_migrations(engine)
    db = SessionLocal()
    try:
        seed_admin(db)
        seed_default_employee(db)
    finally:
        db.close()


app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(employees.router, prefix=settings.api_v1_prefix)
app.include_router(attendance.router, prefix=settings.api_v1_prefix)
app.include_router(sod_eod.router, prefix=settings.api_v1_prefix)
app.include_router(leave.router, prefix=settings.api_v1_prefix)
app.include_router(dashboard.router, prefix=settings.api_v1_prefix)
app.include_router(projects.router, prefix=settings.api_v1_prefix)
app.include_router(tasks.router, prefix=settings.api_v1_prefix)
app.include_router(announcements.router, prefix=settings.api_v1_prefix)
app.include_router(holidays.router, prefix=settings.api_v1_prefix)
app.include_router(company_documents.router, prefix=settings.api_v1_prefix)
app.include_router(company_settings.router, prefix=settings.api_v1_prefix)
app.include_router(expenses.router, prefix=settings.api_v1_prefix)
app.include_router(salary.router, prefix=settings.api_v1_prefix)
app.include_router(audit.router, prefix=settings.api_v1_prefix)

uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


@app.get("/")
def health():
    return {"status": "ok", "service": settings.app_name}
