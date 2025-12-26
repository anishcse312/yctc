CREATE TABLE IF NOT EXISTS admins (
    employee_id TEXT PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    branch TEXT,
    branches JSONB DEFAULT '[]',
    auth_token TEXT,
    profile_picture TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO admins (employee_id, username, password, first_name, last_name, email, branch, branches)
VALUES ('123456','anishban','$2b$12$cBZU0OMuOD01Rds9XXMYOeVGm03gA4KYeFQ5xggOzbuRp6Z686C7.','Anish','Banerjee','anishbanerjee2003@gmail.com','N24','["N24"]'::jsonb)
ON CONFLICT (employee_id) DO NOTHING;
