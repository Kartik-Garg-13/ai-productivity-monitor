CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    department VARCHAR(120),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    employee_code VARCHAR(50) UNIQUE NOT NULL,
    designation VARCHAR(120) NOT NULL,
    department VARCHAR(120) NOT NULL,
    joining_date DATE NOT NULL,
    manager_name VARCHAR(120),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    date DATE NOT NULL,
    check_in TIMESTAMP NOT NULL,
    check_out TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'present',
    work_duration VARCHAR(20)
);

CREATE TABLE sod_entries (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    submitted_for_date DATE NOT NULL,
    type VARCHAR(80) NOT NULL,
    category VARCHAR(120) NOT NULL,
    subcategory VARCHAR(120),
    project VARCHAR(120) NOT NULL,
    work_type VARCHAR(30) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    duration VARCHAR(30) NOT NULL,
    completion_percentage INTEGER NOT NULL,
    ticket_number VARCHAR(80),
    review_status VARCHAR(30) NOT NULL DEFAULT 'pending',
    admin_remarks TEXT,
    day_flag VARCHAR(20) NOT NULL DEFAULT 'full-day',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE eod_entries (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    submitted_for_date DATE NOT NULL,
    morning_activity TEXT NOT NULL,
    incomplete_reason TEXT,
    completion_remarks TEXT,
    review_status VARCHAR(30) NOT NULL DEFAULT 'pending',
    admin_remarks TEXT,
    day_flag VARCHAR(20) NOT NULL DEFAULT 'full-day',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE leave_balances (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER UNIQUE NOT NULL REFERENCES employees(id),
    leave_type VARCHAR(50) NOT NULL DEFAULT 'annual',
    total_leave INTEGER NOT NULL DEFAULT 24,
    leave_taken INTEGER NOT NULL DEFAULT 0,
    remaining_leave INTEGER NOT NULL DEFAULT 24
);

CREATE TABLE leave_applications (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    leave_type VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    duration_days INTEGER NOT NULL,
    reason TEXT NOT NULL,
    mitigation_plan TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    admin_remarks TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
