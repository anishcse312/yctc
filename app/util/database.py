import os
import json
import psycopg2
from contextlib import contextmanager
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor, execute_values
from dotenv import load_dotenv

load_dotenv()


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

if not all([POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD]):
    raise RuntimeError("PostgreSQL credentials are not fully set in environment.")


MASTER_DB = POSTGRES_DB
POOLS = {}


def _new_pool(db_name):
    return pool.SimpleConnectionPool(
        1,
        10,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=db_name,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )


def get_pool(db_name):
    if db_name not in POOLS:
        POOLS[db_name] = _new_pool(db_name)
    return POOLS[db_name]


@contextmanager
def get_conn(db_name):
    conn = get_pool(db_name).getconn()
    try:
        yield conn
    finally:
        get_pool(db_name).putconn(conn)


def _execute(
    query,
    params=None,
    fetchone=False,
    fetchall=False,
    commit=False,
    db_name=None,
    cursor_name=None,
):
    target_db = db_name or MASTER_DB
    with get_conn(target_db) as conn:
        cursor_kwargs = {"cursor_factory": RealDictCursor}
        if cursor_name and (fetchone or fetchall):
            cursor_kwargs["name"] = cursor_name
        with conn.cursor(**cursor_kwargs) as cur:
            cur.execute(query, params or [])
            data = None
            if fetchone:
                data = cur.fetchone()
            elif fetchall:
                data = cur.fetchall()
            if commit:
                conn.commit()
            return data


def ensure_master_schema():
    schema_sql = """
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
    """
    with get_conn(MASTER_DB) as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
            conn.commit()


def ensure_branch_schema(db_name, cursor_name=None):
    schema_sql = """
    CREATE TABLE IF NOT EXISTS sessions (
        session_num INTEGER PRIMARY KEY,
        year INTEGER
    );
    """
    with get_conn(db_name) as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
            conn.commit()


def ensure_branch_db(branch_code):
    db_name = branch_db_name(branch_code)
    create_database_if_missing(db_name)
    ensure_branch_schema(db_name)
    return db_name


def list_branch_codes():
    query = "SELECT datname FROM pg_database WHERE datname LIKE 'yctc\\_%'"
    with get_conn(MASTER_DB) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    codes = []
    for (name,) in rows:
        if name.startswith("yctc_"):
            codes.append(name[len("yctc_"):])
    return sorted(set(codes))


def get_sessions_for_branches(branch_codes):
    sessions = {}
    for code in branch_codes:
        try:
            for session_num, year in get_sessions(code):
                sessions[session_num] = year
        except psycopg2.Error:
            continue
    return [[k, sessions[k]] for k in sorted(sessions.keys())]


def table_exists(db_name, table_name):
    query = "SELECT to_regclass(%s)"
    with get_conn(db_name) as conn:
        with conn.cursor() as cur:
            cur.execute(query, [table_name])
            return cur.fetchone()[0] is not None

if os.getenv("SKIP_DB_INIT") != "1":
    ensure_master_schema()


def admin_row_to_dict(row):
    if not row:
        return None
    branch_value = row.get("branches")
    if branch_value is None:
        branch_value = row.get("branch")
    branches = branch_value
    if isinstance(branch_value, str):
        cleaned = branch_value.strip()
        if cleaned.startswith("[") and cleaned.endswith("]"):
            try:
                branches = json.loads(cleaned)
            except json.JSONDecodeError:
                branches = cleaned
        elif "," in cleaned:
            branches = [item.strip() for item in cleaned.split(",") if item.strip()]
    return {
        "employeeId": row.get("employee_id"),
        "username": row.get("username"),
        "password": row.get("password"),
        "firstName": row.get("first_name"),
        "lastName": row.get("last_name"),
        "email": row.get("email"),
        "branch": branches,
        "auth_token": row.get("auth_token"),
        "profilePicture": row.get("profile_picture"),
    }


def get_admin_by_auth_token(auth_token_hash):
    row = _execute(
        "SELECT * FROM admins WHERE auth_token = %s",
        [auth_token_hash],
        fetchone=True,
        db_name=MASTER_DB,
    )
    return admin_row_to_dict(row)


def get_admin_by_username(username):
    row = _execute(
        "SELECT * FROM admins WHERE username = %s",
        [username],
        fetchone=True,
        db_name=MASTER_DB,
    )
    return admin_row_to_dict(row)


def get_admin_by_employee_id(employee_id):
    row = _execute(
        "SELECT * FROM admins WHERE employee_id = %s",
        [employee_id],
        fetchone=True,
        db_name=MASTER_DB,
    )
    return admin_row_to_dict(row)


def username_exists(username):
    row = _execute(
        "SELECT 1 FROM admins WHERE username = %s",
        [username],
        fetchone=True,
        db_name=MASTER_DB,
    )
    return row is not None


def update_admin_auth_token(username, auth_token_hash):
    _execute(
        "UPDATE admins SET auth_token = %s WHERE username = %s",
        [auth_token_hash, username],
        commit=True,
        db_name=MASTER_DB,
    )


def clear_admin_auth_token(auth_token_hash):
    _execute(
        "UPDATE admins SET auth_token = '' WHERE auth_token = %s",
        [auth_token_hash],
        commit=True,
        db_name=MASTER_DB,
    )


def update_admin_registration(employee_id, username, password_hash):
    _execute(
        "UPDATE admins SET username = %s, password = %s WHERE employee_id = %s",
        [username, password_hash, employee_id],
        commit=True,
        db_name=MASTER_DB,
    )


def get_sessions(branch_code):
    db_name = ensure_branch_db(branch_code)
    rows = _execute(
        "SELECT session_num, year FROM sessions ORDER BY session_num",
        fetchall=True,
        db_name=db_name,
        cursor_name=branch_code,
    )
    return [[row["session_num"], row["year"]] for row in rows] if rows else []


def upsert_session(branch_code, session_num, year):
    db_name = ensure_branch_db(branch_code)
    _execute(
        """
        INSERT INTO sessions (session_num, year)
        VALUES (%s, %s)
        ON CONFLICT (session_num) DO UPDATE SET year = EXCLUDED.year
        """,
        [session_num, year],
        commit=True,
        db_name=db_name,
        cursor_name=branch_code,
    )


def branch_db_name(branch_code):
    return f"yctc_{branch_code}"


def create_database_if_missing(db_name):
    with get_conn(MASTER_DB) as conn:
        old_autocommit = conn.autocommit
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s",
                    [db_name],
                )
                exists = cur.fetchone() is not None
                if not exists:
                    cur.execute(
                        sql.SQL("CREATE DATABASE {}").format(
                            sql.Identifier(db_name)
                        )
                    )
        finally:
            conn.autocommit = old_autocommit


def ensure_data_table(db_name, table_name, columns, cursor_name=None):
    column_defs = sql.SQL(", ").join(
        sql.SQL("{} TEXT").format(sql.Identifier(col)) for col in columns
    )
    query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
        sql.Identifier(table_name),
        column_defs,
    )
    with get_conn(db_name) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            conn.commit()


def insert_rows(table, columns, values, db_name=None, cursor_name=None):
    if not values:
        return
    target_db = db_name or MASTER_DB
    with get_conn(target_db) as conn:
        with conn.cursor() as cur:
            query = sql.SQL("INSERT INTO {} ({}) VALUES %s").format(
                sql.Identifier(table),
                sql.SQL(", ").join(sql.Identifier(col) for col in columns),
            )
            execute_values(cur, query.as_string(conn), values)
            conn.commit()


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
    with get_conn(MASTER_DB) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO receipt (session_num, reg_no, data) VALUES (%s, %s, %s)",
                [(session_num, reg_no, json.dumps(payload)) for payload in payloads],
            )
            conn.commit()


def session_table_name(session_num, base):
    return f"{int(session_num)}_{base}"


def fetch_student_by_reg(branch_code, session_num, reg_no):
    db_name = ensure_branch_db(branch_code)
    cursor_name = branch_code

    def fetch_one(base):
        table = session_table_name(session_num, base)
        if not table_exists(db_name, table):
            return None
        query = sql.SQL("SELECT * FROM {} WHERE reg_no ILIKE %s").format(
            sql.Identifier(table)
        )
        with get_conn(db_name) as conn:
            cursor_kwargs = {"cursor_factory": RealDictCursor, "name": cursor_name}
            with conn.cursor(**cursor_kwargs) as cur:
                cur.execute(query, [reg_no])
                return cur.fetchone()

    def fetch_receipts():
        table = session_table_name(session_num, "receipt")
        if not table_exists(db_name, table):
            return []
        query = sql.SQL("SELECT * FROM {} WHERE reg_no ILIKE %s").format(
            sql.Identifier(table)
        )
        with get_conn(db_name) as conn:
            cursor_kwargs = {"cursor_factory": RealDictCursor, "name": cursor_name}
            with conn.cursor(**cursor_kwargs) as cur:
                cur.execute(query, [reg_no])
                return cur.fetchall()

    return {
        "stuadmn": fetch_one("stuadmn"),
        "formrecv": fetch_one("formrecv"),
        "reenroll": fetch_one("reenroll"),
        "marks": fetch_one("marks"),
        "instreg": fetch_one("instreg"),
        "receipts": fetch_receipts() or [],
    }


def search_stuadmn_by_name(branch_code, session_num, name):
    db_name = ensure_branch_db(branch_code)
    cursor_name = branch_code
    table = session_table_name(session_num, "stuadmn")
    if not table_exists(db_name, table):
        return []
    query = sql.SQL(
        """
        SELECT reg_no,
               name,
               f_name,
               COALESCE(session, %s::text) AS session
        FROM {}
        WHERE name ILIKE %s
        """
    ).format(sql.Identifier(table))
    pattern = f"%{name}%"
    with get_conn(db_name) as conn:
        cursor_kwargs = {"cursor_factory": RealDictCursor, "name": cursor_name}
        with conn.cursor(**cursor_kwargs) as cur:
            try:
                cur.execute(query, [str(session_num), pattern])
                rows = cur.fetchall()
            except psycopg2.errors.UndefinedTable:
                rows = []
    return rows or []
