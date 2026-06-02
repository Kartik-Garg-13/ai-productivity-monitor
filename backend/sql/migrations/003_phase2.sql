-- Phase 2 HRMS modules

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    client_name VARCHAR(200),
    description TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    project_lead_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
    tech_owner_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS project_members (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    UNIQUE(project_id, employee_id)
);

CREATE TABLE IF NOT EXISTS project_tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    assigned_employee_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
    assigned_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    due_date DATE,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS task_comments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES project_tasks(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    comment TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS announcements (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'general',
    content TEXT NOT NULL,
    publish_date TIMESTAMP NOT NULL,
    expiry_date TIMESTAMP,
    is_pinned BOOLEAN NOT NULL DEFAULT FALSE,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS holidays (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    date DATE NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'public',
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS company_documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(80) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    original_filename VARCHAR(255),
    uploaded_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS document_downloads (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES company_documents(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    downloaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    expense_date DATE NOT NULL,
    expense_type VARCHAR(80) NOT NULL,
    expense_category VARCHAR(80) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    description TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    payment_date DATE,
    transaction_id VARCHAR(100),
    admin_remarks TEXT,
    reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS expense_attachments (
    id SERIAL PRIMARY KEY,
    expense_id INTEGER NOT NULL REFERENCES expenses(id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    original_filename VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS salary_slips (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    month DATE NOT NULL,
    basic_salary NUMERIC(12, 2) NOT NULL DEFAULT 0,
    hra NUMERIC(12, 2) NOT NULL DEFAULT 0,
    bonus NUMERIC(12, 2) NOT NULL DEFAULT 0,
    deductions NUMERIC(12, 2) NOT NULL DEFAULT 0,
    net_salary NUMERIC(12, 2) NOT NULL DEFAULT 0,
    status VARCHAR(30) NOT NULL DEFAULT 'generated',
    pdf_path VARCHAR(500),
    paid_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(employee_id, month)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(120) NOT NULL,
    entity_type VARCHAR(80),
    entity_id INTEGER,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
