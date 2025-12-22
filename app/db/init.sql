CREATE TABLE IF NOT EXISTS admins (
    employee_id TEXT PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    branch TEXT,
    auth_token TEXT,
    profile_picture TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sessions (
    session_num INTEGER PRIMARY KEY,
    year INTEGER
);

CREATE TABLE IF NOT EXISTS stuadmn (
    id SERIAL PRIMARY KEY,
    session_num INTEGER NOT NULL,
    reg_no TEXT NOT NULL,
    data JSONB NOT NULL,
    UNIQUE(session_num, reg_no)
);

CREATE TABLE IF NOT EXISTS formrecv (
    id SERIAL PRIMARY KEY,
    session_num INTEGER NOT NULL,
    reg_no TEXT NOT NULL,
    data JSONB NOT NULL,
    UNIQUE(session_num, reg_no)
);

CREATE TABLE IF NOT EXISTS reenroll (
    id SERIAL PRIMARY KEY,
    session_num INTEGER NOT NULL,
    reg_no TEXT NOT NULL,
    data JSONB NOT NULL,
    UNIQUE(session_num, reg_no)
);

CREATE TABLE IF NOT EXISTS receipt (
    id SERIAL PRIMARY KEY,
    session_num INTEGER NOT NULL,
    reg_no TEXT NOT NULL,
    data JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS marks (
    id SERIAL PRIMARY KEY,
    session_num INTEGER NOT NULL,
    reg_no TEXT NOT NULL,
    data JSONB NOT NULL,
    UNIQUE(session_num, reg_no)
);

CREATE TABLE IF NOT EXISTS instreg (
    id SERIAL PRIMARY KEY,
    session_num INTEGER NOT NULL,
    reg_no TEXT NOT NULL,
    data JSONB NOT NULL,
    UNIQUE(session_num, reg_no)
);

CREATE INDEX IF NOT EXISTS idx_formrecv_name ON formrecv ((data->>'name'));
CREATE INDEX IF NOT EXISTS idx_formrecv_reg ON formrecv (reg_no);
CREATE INDEX IF NOT EXISTS idx_receipt_reg ON receipt (reg_no);
