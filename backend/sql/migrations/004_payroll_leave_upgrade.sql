-- Payroll & Leave upgrade (additive — preserves existing columns)

CREATE TABLE IF NOT EXISTS company_settings (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL DEFAULT 'Goldilocks Tech',
    company_logo_path VARCHAR(500),
    company_address TEXT,
    gst_number VARCHAR(20),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

ALTER TABLE employees ADD COLUMN IF NOT EXISTS uan_number VARCHAR(20);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS pf_number VARCHAR(30);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS work_location VARCHAR(100);

-- Earnings
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS da NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS conveyance_allowance NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS medical_allowance NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS internet_allowance NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS special_allowance NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS incentive NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS overtime_pay NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS project_bonus NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS other_earnings NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS total_earnings NUMERIC(12, 2) NOT NULL DEFAULT 0;

-- Deductions (keeps legacy `deductions` column for backward compatibility)
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS pf NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS esi NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS professional_tax NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS tds NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS loan_deduction NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS advance_salary_recovery NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS leave_deduction NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS late_attendance_deduction NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS penalty_deduction NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS other_deductions NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS total_deductions NUMERIC(12, 2) NOT NULL DEFAULT 0;

-- Summary & snapshots
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS gross_salary NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS in_hand_salary NUMERIC(12, 2) NOT NULL DEFAULT 0;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS amount_in_words TEXT;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS payroll_year INTEGER;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS generated_at TIMESTAMP;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS bank_snapshot JSONB;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS attendance_snapshot JSONB;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS leave_snapshot JSONB;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS employee_snapshot JSONB;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS company_snapshot JSONB;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS payment_date DATE;
ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS transaction_id VARCHAR(100);

ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS emergency_contact_number VARCHAR(20);
ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP;
ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL;

-- Allow multiple leave balance rows per employee (one per leave type)
ALTER TABLE leave_balances DROP CONSTRAINT IF EXISTS leave_balances_employee_id_key;
