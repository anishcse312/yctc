import os
import json
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

    CREATE TABLE IF NOT EXISTS branches (
        branch_code TEXT PRIMARY KEY
    );

    CREATE TABLE IF NOT EXISTS branch_sessions (
        branch_code TEXT NOT NULL REFERENCES branches(branch_code) ON DELETE CASCADE,
        session_num INTEGER NOT NULL,
        PRIMARY KEY (branch_code, session_num)
    );

    CREATE TABLE IF NOT EXISTS batch (
        id BIGSERIAL PRIMARY KEY,
        branch_code TEXT NOT NULL,
        session_num INTEGER NOT NULL,
        batchcode TEXT,
        coursecode TEXT,
        courseid TEXT,
        batchday TEXT,
        batchtime TEXT,
        faculty TEXT,
        totalseat TEXT,
        alloted TEXT,
        classstart TEXT,
        terget TEXT,
        remarks TEXT,
        session TEXT,
        ses_half TEXT,
        centre TEXT,
        deleted TEXT,
        user_name TEXT,
        FOREIGN KEY (branch_code, session_num)
            REFERENCES branch_sessions (branch_code, session_num)
            ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS examtime (
        id BIGSERIAL PRIMARY KEY,
        branch_code TEXT NOT NULL,
        session_num INTEGER NOT NULL,
        rollno TEXT,
        reg_no TEXT,
        time TEXT,
        date TEXT,
        lab TEXT,
        batch TEXT,
        batch1 TEXT,
        term TEXT,
        session TEXT,
        ses_half TEXT,
        centre TEXT,
        user_name TEXT,
        remarks TEXT,
        FOREIGN KEY (branch_code, session_num)
            REFERENCES branch_sessions (branch_code, session_num)
            ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS formrecv_hier (
        id BIGSERIAL PRIMARY KEY,
        branch_code TEXT NOT NULL,
        session_num INTEGER NOT NULL,
        form_no TEXT,
        recv_date TEXT,
        name TEXT,
        dob TEXT,
        sex TEXT,
        caste TEXT,
        f_name TEXT,
        add_1 TEXT,
        add_2 TEXT,
        po TEXT,
        district TEXT,
        pin TEXT,
        phone TEXT,
        mobile TEXT,
        gq1 TEXT,
        gq2 TEXT,
        gq3 TEXT,
        gq4 TEXT,
        tq TEXT,
        course_id TEXT,
        centre_id TEXT,
        reg_no TEXT,
        scholar TEXT,
        session TEXT,
        ses_half TEXT,
        remarks TEXT,
        horemarks TEXT,
        semister TEXT,
        otheryctc TEXT,
        frontline TEXT,
        attend_by TEXT,
        user_name TEXT,
        prospectusissued TEXT,
        checkdob TEXT,
        checkcaste TEXT,
        checkgq1 TEXT,
        checkgq2 TEXT,
        checkgq3 TEXT,
        checkgq4 TEXT,
        checktq TEXT,
        aadharno TEXT,
        employername TEXT,
        employeradd TEXT,
        designame TEXT,
        actualsalary TEXT,
        jobjoindate TEXT,
        jobportaldate TEXT,
        salaryrem TEXT,
        e_mail TEXT,
        next_session TEXT,
        re_exam TEXT,
        exam_appear TEXT,
        FOREIGN KEY (branch_code, session_num)
            REFERENCES branch_sessions (branch_code, session_num)
            ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS icardbookissue (
        id BIGSERIAL PRIMARY KEY,
        branch_code TEXT NOT NULL,
        session_num INTEGER NOT NULL,
        reg_no TEXT,
        name TEXT,
        batch TEXT,
        icard TEXT,
        book1 TEXT,
        book2 TEXT,
        book3 TEXT,
        book4 TEXT,
        centrename TEXT,
        user_name TEXT,
        FOREIGN KEY (branch_code, session_num)
            REFERENCES branch_sessions (branch_code, session_num)
            ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS instreg_hier (
        id BIGSERIAL PRIMARY KEY,
        branch_code TEXT NOT NULL,
        session_num INTEGER NOT NULL,
        reg_no TEXT,
        admission TEXT,
        admn_recpt TEXT,
        inst_1_due TEXT,
        inst_1_dt TEXT,
        i_1_recpt TEXT,
        inst_2_due TEXT,
        inst_2_dt TEXT,
        i_2_recpt TEXT,
        inst_3_due TEXT,
        inst_3_dt TEXT,
        i_3_recpt TEXT,
        inst_4_due TEXT,
        inst_4_dt TEXT,
        i_4_recpt TEXT,
        inst_5_due TEXT,
        inst_5_dt TEXT,
        i_5_recpt TEXT,
        inst_6_due TEXT,
        inst_6_dt TEXT,
        i_6_recpt TEXT,
        inst_7_due TEXT,
        inst_7_dt TEXT,
        i_7_recpt TEXT,
        inst_8_due TEXT,
        inst_8_dt TEXT,
        i_8_recpt TEXT,
        session TEXT,
        ses_half TEXT,
        centre_id TEXT,
        sem_payabl TEXT,
        sem_paypart TEXT,
        user_name TEXT,
        FOREIGN KEY (branch_code, session_num)
            REFERENCES branch_sessions (branch_code, session_num)
            ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS letter (
        id BIGSERIAL PRIMARY KEY,
        branch_code TEXT NOT NULL,
        session_num INTEGER NOT NULL,
        reference TEXT,
        srl TEXT,
        reg_no TEXT,
        name TEXT,
        "lateral" TEXT,
        course TEXT,
        batch TEXT,
        date TEXT,
        time TEXT,
        reminder TEXT,
        sender TEXT,
        remarks TEXT,
        faculty TEXT,
        centre TEXT,
        session TEXT,
        user_name TEXT,
        deleted TEXT,
        FOREIGN KEY (branch_code, session_num)
            REFERENCES branch_sessions (branch_code, session_num)
            ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS marks_hier (
        id BIGSERIAL PRIMARY KEY,
        branch_code TEXT NOT NULL,
        session_num INTEGER NOT NULL,
        reg_no TEXT,
        batch_code TEXT,
        p1s1 TEXT,
        p2s1 TEXT,
        p3s1 TEXT,
        ts1 TEXT,
        as1 TEXT,
        gs1 TEXT,
        p1s2 TEXT,
        p2s2 TEXT,
        ts2 TEXT,
        as2 TEXT,
        gs2 TEXT,
        p1s3 TEXT,
        p2s3 TEXT,
        ts3 TEXT,
        as3 TEXT,
        gs3 TEXT,
        tot TEXT,
        avg TEXT,
        grade TEXT,
        centre TEXT,
        pre_reg_no TEXT,
        session TEXT,
        certi_no TEXT,
        certi_date TEXT,
        trans_no TEXT,
        trans_date TEXT,
        user_name TEXT,
        remarks TEXT,
        exam_appear TEXT,
        FOREIGN KEY (branch_code, session_num)
            REFERENCES branch_sessions (branch_code, session_num)
            ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS receipt_hier (
        id BIGSERIAL PRIMARY KEY,
        branch_code TEXT NOT NULL,
        session_num INTEGER NOT NULL,
        recpnopre TEXT,
        cnt_prefix TEXT,
        receiptno TEXT,
        recptdate TEXT,
        recpttime TEXT,
        amount TEXT,
        coursefees TEXT,
        admnfees TEXT,
        prospectus TEXT,
        batchchang TEXT,
        fine_amt TEXT,
        fine_days TEXT,
        instalment TEXT,
        reg_no TEXT,
        recpt_type TEXT,
        pay_mode TEXT,
        dd_no TEXT,
        dd_dt TEXT,
        draw_bank TEXT,
        remarks TEXT,
        "lateral" TEXT,
        centre_id TEXT,
        session TEXT,
        ses_half TEXT,
        frontline TEXT,
        user_name TEXT,
        deleted TEXT,
        dd_no_2 TEXT,
        FOREIGN KEY (branch_code, session_num)
            REFERENCES branch_sessions (branch_code, session_num)
            ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS reenroll_hier (
        id BIGSERIAL PRIMARY KEY,
        branch_code TEXT NOT NULL,
        session_num INTEGER NOT NULL,
        reg_no TEXT,
        batchcode TEXT,
        "lateral" TEXT,
        course_ap1 TEXT,
        course_ap2 TEXT,
        course_ap3 TEXT,
        n_reg_no_1 TEXT,
        course_ad1 TEXT,
        batch_no_1 TEXT,
        n_reg_no_2 TEXT,
        course_ad2 TEXT,
        batch_no_2 TEXT,
        n_reg_no_3 TEXT,
        course_ad3 TEXT,
        batch_no_3 TEXT,
        session TEXT,
        ses_half TEXT,
        already_dip TEXT,
        centre TEXT,
        user_name TEXT,
        FOREIGN KEY (branch_code, session_num)
            REFERENCES branch_sessions (branch_code, session_num)
            ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS scholarlist (
        id BIGSERIAL PRIMARY KEY,
        branch_code TEXT NOT NULL,
        session_num INTEGER NOT NULL,
        reg_no TEXT,
        course TEXT,
        batch TEXT,
        scholarsem TEXT,
        voucherno TEXT,
        voucherdate TEXT,
        amount TEXT,
        returndate TEXT,
        isreturned TEXT,
        centre TEXT,
        user_name TEXT,
        FOREIGN KEY (branch_code, session_num)
            REFERENCES branch_sessions (branch_code, session_num)
            ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS stuadmn_hier (
        id BIGSERIAL PRIMARY KEY,
        branch_code TEXT NOT NULL,
        session_num INTEGER NOT NULL,
        reg_no TEXT,
        name TEXT,
        f_name TEXT,
        course_id TEXT,
        batch TEXT,
        payday TEXT,
        form_no TEXT,
        pre_reg TEXT,
        centre_id TEXT,
        "lateral" TEXT,
        final_roll TEXT,
        remarks TEXT,
        session TEXT,
        ses_half TEXT,
        on_mid TEXT,
        on_final TEXT,
        scholar TEXT,
        semister TEXT,
        otheryctc TEXT,
        frontline TEXT,
        user_name TEXT,
        next_session TEXT,
        re_exam TEXT,
        exam_loginid TEXT,
        exam_password TEXT,
        exam_appear TEXT,
        exam_reg_on TEXT,
        exam_reg_by TEXT,
        exam_schedule TEXT,
        FOREIGN KEY (branch_code, session_num)
            REFERENCES branch_sessions (branch_code, session_num)
            ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_examtime_reg_no ON examtime (reg_no);
    CREATE INDEX IF NOT EXISTS idx_formrecv_hier_reg_no ON formrecv_hier (reg_no);
    CREATE INDEX IF NOT EXISTS idx_icardbookissue_reg_no ON icardbookissue (reg_no);
    CREATE INDEX IF NOT EXISTS idx_instreg_hier_reg_no ON instreg_hier (reg_no);
    CREATE INDEX IF NOT EXISTS idx_letter_reg_no ON letter (reg_no);
    CREATE INDEX IF NOT EXISTS idx_marks_hier_reg_no ON marks_hier (reg_no);
    CREATE INDEX IF NOT EXISTS idx_receipt_hier_reg_no ON receipt_hier (reg_no);
    CREATE INDEX IF NOT EXISTS idx_reenroll_hier_reg_no ON reenroll_hier (reg_no);
    CREATE INDEX IF NOT EXISTS idx_scholarlist_reg_no ON scholarlist (reg_no);
    CREATE INDEX IF NOT EXISTS idx_stuadmn_hier_reg_no ON stuadmn_hier (reg_no);
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


def upsert_branch(branch_code):
    _execute(
        """
        INSERT INTO branches (branch_code)
        VALUES (%s)
        ON CONFLICT (branch_code) DO NOTHING
        """,
        [branch_code],
        commit=True,
    )


def upsert_branch_session(branch_code, session_num):
    _execute(
        """
        INSERT INTO branch_sessions (branch_code, session_num)
        VALUES (%s, %s)
        ON CONFLICT (branch_code, session_num) DO NOTHING
        """,
        [branch_code, session_num],
        commit=True,
    )


def insert_rows(table, columns, values):
    if not values:
        return
    with get_conn() as conn:
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
