import os
import sys

from dotenv import load_dotenv
import psycopg2


def main():
    load_dotenv()

    host = os.getenv("POSTGRES_HOST", "localhost")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    dbname = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")

    if not all([dbname, user, password]):
        print("Missing PostgreSQL env vars in .env (POSTGRES_DB/USER/PASSWORD).")
        sys.exit(1)

    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            connect_timeout=5,
        )
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM public.admins;")
            result = cur.fetchone()
        conn.close()
        print(f"PostgreSQL connection OK (SELECT 1 -> {result[0]}).")
    except Exception as exc:
        print(f"PostgreSQL connection failed: {exc}")
        sys.exit(2)


if __name__ == "__main__":
    main()
