import os
import json
from contextlib import contextmanager
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

if not all([POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD]):
    raise RuntimeError("PostgreSQL credentials are not fully set in environment.")


POOL = pool.SimpleConnectionPool(
    1,
    10,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
)


@contextmanager
def get_conn():
    conn = POOL.getconn()
    try:
        yield conn
    finally:
        POOL.putconn(conn)


def _execute(query, params=None, fetchone=False, fetchall=False, commit=False):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or [])
            data = None
            if fetchone:
                data = cur.fetchone()
            elif fetchall:
                data = cur.fetchall()
            if commit:
                conn.commit()
            return data


def ensure_schema():
    schema_sql = """
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
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
            conn.commit()


ensure_schema()


def admin_row_to_dict(row):
    if not row:
        return None
    return {
        "employeeId": row.get("employee_id"),
        "username": row.get("username"),
        "password": row.get("password"),
        "firstName": row.get("first_name"),
        "lastName": row.get("last_name"),
        "email": row.get("email"),
        "branch": row.get("branch"),
        "auth_token": row.get("auth_token"),
        "profilePicture": row.get("profile_picture"),
    }


def get_admin_by_auth_token(auth_token_hash):
    row = _execute(
        "SELECT * FROM admins WHERE auth_token = %s",
        [auth_token_hash],
        fetchone=True,
    )
    return admin_row_to_dict(row)


def get_admin_by_username(username):
    row = _execute("SELECT * FROM admins WHERE username = %s", [username], fetchone=True)
    return admin_row_to_dict(row)


def get_admin_by_employee_id(employee_id):
    row = _execute(
        "SELECT * FROM admins WHERE employee_id = %s", [employee_id], fetchone=True
    )
    return admin_row_to_dict(row)


def username_exists(username):
    row = _execute(
        "SELECT 1 FROM admins WHERE username = %s", [username], fetchone=True
    )
    return row is not None


def update_admin_auth_token(username, auth_token_hash):
    _execute(
        "UPDATE admins SET auth_token = %s WHERE username = %s",
        [auth_token_hash, username],
        commit=True,
    )


def clear_admin_auth_token(auth_token_hash):
    _execute(
        "UPDATE admins SET auth_token = '' WHERE auth_token = %s",
        [auth_token_hash],
        commit=True,
    )


def update_admin_registration(employee_id, username, password_hash):
    _execute(
        "UPDATE admins SET username = %s, password = %s WHERE employee_id = %s",
        [username, password_hash, employee_id],
        commit=True,
    )


def get_sessions():
    rows = _execute(
        "SELECT session_num, year FROM sessions ORDER BY session_num",
        fetchall=True,
    )
    return [[row["session_num"], row["year"]] for row in rows] if rows else []


def upsert_session(session_num, year):
    _execute(
        """
        INSERT INTO sessions (session_num, year)
        VALUES (%s, %s)
        ON CONFLICT (session_num) DO UPDATE SET year = EXCLUDED.year
        """,
        [session_num, year],
        commit=True,
    )


def upsert_json_row(table, session_num, reg_no, payload):
    _execute(
        f"""
        INSERT INTO {table} (session_num, reg_no, data)
        VALUES (%s, %s, %s)
        ON CONFLICT (session_num, reg_no) DO UPDATE SET data = EXCLUDED.data
        """,
        [session_num, reg_no, json.dumps(payload)],
        commit=True,
    )


def insert_receipt_rows(session_num, reg_no, payloads):
    if not payloads:
        return
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO receipt (session_num, reg_no, data) VALUES (%s, %s, %s)",
                [(session_num, reg_no, json.dumps(payload)) for payload in payloads],
            )
            conn.commit()


def fetch_student_by_reg(session_num, reg_no):
    def fetch_one(table):
        row = _execute(
            f"SELECT data FROM {table} WHERE session_num = %s AND reg_no = %s",
            [session_num, reg_no],
            fetchone=True,
        )
        return row["data"] if row else None

    return {
        "stuadmn": fetch_one("stuadmn"),
        "formrecv": fetch_one("formrecv"),
        "reenroll": fetch_one("reenroll"),
        "marks": fetch_one("marks"),
        "instreg": fetch_one("instreg"),
        "receipts": _execute(
            "SELECT data FROM receipt WHERE session_num = %s AND reg_no = %s",
            [session_num, reg_no],
            fetchall=True,
        )
        or [],
    }


def search_formrecv_by_name(session_num, name):
    rows = _execute(
        """
        SELECT reg_no,
               data->>'name' AS name,
               data->>'dob' AS dob,
               data->>'f_name' AS f_name,
               COALESCE(data->>'session', %s::text) AS session
        FROM formrecv
        WHERE session_num = %s AND data->>'name' = %s
        """,
        [str(session_num), session_num, name],
        fetchall=True,
    )
    return rows or []
