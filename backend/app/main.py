from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import attendance, auth, dashboard, employees, leave, sod_eod
from app.core.config import get_settings
from app.db.base import Base
from app.db.init_db import seed_admin
from app.db.session import SessionLocal, engine
from app.models import attendance as _attendance  # noqa
from app.models import employee as _employee  # noqa
from app.models import leave as _leave  # noqa
from app.models import sod_eod as _sod_eod  # noqa
from app.models import user as _user  # noqa

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
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_admin(db)
    finally:
        db.close()


app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(employees.router, prefix=settings.api_v1_prefix)
app.include_router(attendance.router, prefix=settings.api_v1_prefix)
app.include_router(sod_eod.router, prefix=settings.api_v1_prefix)
app.include_router(leave.router, prefix=settings.api_v1_prefix)
app.include_router(dashboard.router, prefix=settings.api_v1_prefix)


@app.get("/")
def health():
    return {"status": "ok", "service": settings.app_name}
