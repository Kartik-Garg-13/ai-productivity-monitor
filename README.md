# Goldilocks Tech HRMS + Productivity + Workflow System

Production-ready Phase 1 implementation (Days 1-7) for an internal remote-work company portal.

## Tech Stack

- Frontend: React, Vite, Tailwind CSS, Axios, React Router DOM
- Backend: FastAPI, SQLAlchemy ORM, JWT auth, bcrypt hashing
- Database: PostgreSQL
- Integrations: SMTP email notifications

## Monorepo Structure

```text
backend/
  app/
    api/
    core/
    db/
    middleware/
    models/
    schemas/
    services/
  sql/
frontend/
  src/
    components/
    context/
    hooks/
    layouts/
    pages/
    routes/
    services/
```

## Implemented Day-wise Scope

### Day 1: Setup and Architecture
- Vite frontend + Tailwind setup
- FastAPI backend with CORS and env-based config
- PostgreSQL connection via SQLAlchemy
- Modular folder structure for scale

### Day 2: Authentication
- Admin and employee login
- JWT token generation and validation
- bcrypt password hashing
- role-based guards on APIs and frontend routes
- protected layouts and logout flow

### Day 3: Employee CRUD
- Admin create/read/update/delete employee
- Employee profile endpoint/page
- welcome email trigger on employee creation

### Day 4: Attendance
- Employee check-in/check-out
- duplicate check-in prevention
- auto duration calculation
- employee history + admin attendance monitor

### Day 5: SOD / EOD Workflow
- SOD and EOD submissions
- time cutoff validation for half-day flags
- admin review endpoints for approve/clarification status

### Day 6: Leave Management
- leave apply + reason + mitigation
- leave balance tracking and deduction on approval
- leave history and pending admin approvals

### Day 7: Admin Dashboard UI
- KPI cards for workforce and pending actions
- sidebar navigation
- module pages for employee/attendance/workflow/leave reviews
- dark mode-ready Tailwind config

## Environment Variables

### Backend (`backend/.env`)

Use `backend/.env.example`:

```env
APP_NAME=Goldilocks HRMS API
APP_ENV=development
API_V1_PREFIX=/api/v1
SECRET_KEY=change_this_secret_in_production
ACCESS_TOKEN_EXPIRE_MINUTES=480
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/goldilocks_hrms
CORS_ORIGINS=http://localhost:5173
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_smtp_password
SMTP_FROM=no-reply@goldilocks.tech
```

### Frontend (`frontend/.env`)

Use `frontend/.env.example`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Setup Instructions

## 1) Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Backend URL: [http://localhost:8000](http://localhost:8000)  
Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## 2) Frontend Setup

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Frontend URL: [http://localhost:5173](http://localhost:5173)

## Default Admin Account

Seeded automatically on first backend startup:

- Email: `admin@goldilocks.tech`
- Password: `Admin@123`

## PostgreSQL Schema

- SQL reference: `backend/sql/schema.sql`
- SQLAlchemy models create tables automatically at startup

## Core API Endpoints

### Auth
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

### Employees
- `POST /api/v1/employees` (admin)
- `GET /api/v1/employees` (admin)
- `PUT /api/v1/employees/{employee_id}` (admin)
- `DELETE /api/v1/employees/{employee_id}` (admin)
- `GET /api/v1/employees/profile` (employee)

### Attendance
- `POST /api/v1/attendance/check-in`
- `POST /api/v1/attendance/check-out`
- `GET /api/v1/attendance/history`
- `GET /api/v1/attendance/admin` (admin)

### Workflow (SOD/EOD)
- `POST /api/v1/workflow/sod`
- `POST /api/v1/workflow/eod`
- `GET /api/v1/workflow/admin/sod` (admin)
- `GET /api/v1/workflow/admin/eod` (admin)
- `PATCH /api/v1/workflow/admin/sod/{id}` (admin)
- `PATCH /api/v1/workflow/admin/eod/{id}` (admin)

### Leave
- `POST /api/v1/leave/apply`
- `GET /api/v1/leave/history`
- `GET /api/v1/leave/admin/pending` (admin)
- `PATCH /api/v1/leave/admin/{leave_id}` (admin)

### Dashboard
- `GET /api/v1/dashboard/admin` (admin)

## Production Hardening Recommendations (next phase)

- Replace `create_all` with Alembic migrations
- Add refresh-token rotation and token blacklist/logout API
- Add Redis-backed caching and rate limiting
- Add audit logs and activity timeline
- Add unit/integration tests + CI pipeline
- Add stricter DTO validation and centralized exception handlers
