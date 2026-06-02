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
    employee_id VARCHAR(50) UNIQUE,
    employee_code VARCHAR(50) UNIQUE NOT NULL,
    designation VARCHAR(120) NOT NULL,
    department VARCHAR(120) NOT NULL,
    joining_date DATE NOT NULL,
    employment_type VARCHAR(50),
    reporting_manager VARCHAR(120),
    project_lead VARCHAR(120),
    tech_owner VARCHAR(120),
    company_email VARCHAR(255),
    employment_status VARCHAR(30) DEFAULT 'active',
    manager_name VARCHAR(120),
    title VARCHAR(20),
    first_name VARCHAR(80),
    middle_name VARCHAR(80),
    last_name VARCHAR(80),
    gender VARCHAR(20),
    father_name VARCHAR(120),
    date_of_birth DATE,
    nationality VARCHAR(80),
    marital_status VARCHAR(30),
    anniversary_date DATE,
    number_of_children INTEGER,
    blood_group VARCHAR(10),
    profile_photo_path VARCHAR(500),
    pan_number VARCHAR(20),
    aadhaar_number VARCHAR(20),
    passport_number VARCHAR(30),
    passport_issue_date DATE,
    passport_expiry_date DATE,
    passport_issue_place VARCHAR(120),
    mobile_number VARCHAR(20),
    alternate_number VARCHAR(20),
    personal_email VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- See sql/migrations/002_employee_profile.sql for child tables

CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    date DATE NOT NULL,
    check_in TIMESTAMP NOT NULL,
    check_out TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'present',
    work_duration VARCHAR(20),
    ip_address VARCHAR(45)
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
