from pathlib import Path

import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()

SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"


def get_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def iter_sql_files():
    if not SCHEMA_DIR.exists():
        raise RuntimeError(f"Schema directory not found: {SCHEMA_DIR}")
    return sorted(SCHEMA_DIR.glob("*.sql"))


def apply_sql_file(conn, path):
    sql_text = path.read_text(encoding="utf-8")
    if not sql_text.strip():
        print(f"[SKIP] Empty schema file: {path.name}")
        return
    with conn.cursor() as cur:
        cur.execute(sql_text)
    conn.commit()
    print(f"[OK] Applied {path.name}")


def main():
    sql_files = iter_sql_files()
    if not sql_files:
        print(f"[WARN] No schema files found in {SCHEMA_DIR}")
        return
    with get_conn() as conn:
        for path in sql_files:
            apply_sql_file(conn, path)


if __name__ == "__main__":
    main()
