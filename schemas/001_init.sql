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
