-- Employee profile expansion (run via migrate.py or manually)

ALTER TABLE employees ADD COLUMN IF NOT EXISTS employee_id VARCHAR(50) UNIQUE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS employment_type VARCHAR(50);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS reporting_manager VARCHAR(120);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS project_lead VARCHAR(120);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS tech_owner VARCHAR(120);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS company_email VARCHAR(255);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS employment_status VARCHAR(30) DEFAULT 'active';
ALTER TABLE employees ADD COLUMN IF NOT EXISTS title VARCHAR(20);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS first_name VARCHAR(80);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS middle_name VARCHAR(80);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS last_name VARCHAR(80);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS gender VARCHAR(20);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS father_name VARCHAR(120);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS date_of_birth DATE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS nationality VARCHAR(80);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS marital_status VARCHAR(30);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS anniversary_date DATE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS number_of_children INTEGER;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS blood_group VARCHAR(10);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS profile_photo_path VARCHAR(500);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS pan_number VARCHAR(20);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS aadhaar_number VARCHAR(20);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS passport_number VARCHAR(30);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS passport_issue_date DATE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS passport_expiry_date DATE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS passport_issue_place VARCHAR(120);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS mobile_number VARCHAR(20);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS alternate_number VARCHAR(20);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS personal_email VARCHAR(255);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();

CREATE TABLE IF NOT EXISTS employee_addresses (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    address_type VARCHAR(20) NOT NULL,
    address_line_1 VARCHAR(255),
    address_line_2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    pin_code VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS employee_documents (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    original_filename VARCHAR(255),
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS employee_family (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    name VARCHAR(120) NOT NULL,
    relationship VARCHAR(50),
    date_of_birth DATE,
    occupation VARCHAR(120),
    company VARCHAR(120)
);

CREATE TABLE IF NOT EXISTS employee_bank_details (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER UNIQUE NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    bank_name VARCHAR(120),
    account_number VARCHAR(40),
    ifsc_code VARCHAR(20),
    branch_name VARCHAR(120),
    branch_address TEXT
);

CREATE TABLE IF NOT EXISTS employee_education (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    degree VARCHAR(120),
    institute VARCHAR(200),
    board_university VARCHAR(200),
    year_of_passing VARCHAR(10),
    percentage VARCHAR(20),
    major_subjects VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS employee_experience (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    company_name VARCHAR(200),
    industry VARCHAR(120),
    designation VARCHAR(120),
    employment_type VARCHAR(50),
    start_date DATE,
    end_date DATE,
    reason_for_leaving TEXT
);

CREATE TABLE IF NOT EXISTS employee_skills (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER UNIQUE NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    certification_name VARCHAR(200),
    certification_provider VARCHAR(200),
    certification_issue_date DATE,
    certification_expiry_date DATE,
    technical_skills TEXT,
    soft_skills TEXT,
    programming_languages TEXT,
    frameworks TEXT,
    tools TEXT
);

CREATE TABLE IF NOT EXISTS employee_languages (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    language VARCHAR(80) NOT NULL,
    can_speak BOOLEAN NOT NULL DEFAULT FALSE,
    can_read BOOLEAN NOT NULL DEFAULT FALSE,
    can_write BOOLEAN NOT NULL DEFAULT FALSE,
    can_understand BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS employee_interests (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    interest VARCHAR(80) NOT NULL
);
