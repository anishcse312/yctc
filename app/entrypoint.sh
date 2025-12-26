#!/bin/sh
set -e

python - <<'PY'
import os
import time
import psycopg2

host = os.getenv("POSTGRES_HOST", "localhost")
port = int(os.getenv("POSTGRES_PORT", "5432"))
db = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")

if not all([db, user, password]):
    raise SystemExit("Missing Postgres env vars")

for _ in range(60):
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=db,
            user=user,
            password=password,
        )
        conn.close()
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("Postgres did not become ready in time")
PY

INIT_NEEDED=$(python - <<'PY'
import os
import psycopg2

host = os.getenv("POSTGRES_HOST", "localhost")
port = int(os.getenv("POSTGRES_PORT", "5432"))
db = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")

conn = psycopg2.connect(
    host=host,
    port=port,
    dbname=db,
    user=user,
    password=password,
)
conn.autocommit = True
with conn.cursor() as cur:
    cur.execute(
        "CREATE TABLE IF NOT EXISTS db_init_state ("
        "key TEXT PRIMARY KEY, "
        "created_at TIMESTAMP DEFAULT NOW()"
        ")"
    )
    cur.execute("SELECT 1 FROM db_init_state WHERE key = 'done'")
    needs_init = cur.fetchone() is None
print("1" if needs_init else "0")
conn.close()
PY
)

if [ "$INIT_NEEDED" = "1" ]; then
  python migrate_schema.py
  python migrate_data.py
  python make_db.py

  python - <<'PY'
import os
import psycopg2

host = os.getenv("POSTGRES_HOST", "localhost")
port = int(os.getenv("POSTGRES_PORT", "5432"))
db = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")

conn = psycopg2.connect(
    host=host,
    port=port,
    dbname=db,
    user=user,
    password=password,
)
conn.autocommit = True
with conn.cursor() as cur:
    cur.execute(
        "INSERT INTO db_init_state (key) VALUES ('done') "
        "ON CONFLICT (key) DO NOTHING"
    )
conn.close()
PY
fi

MISSING_BRANCHES=$(python - <<'PY'
import os
import re
import psycopg2
from pathlib import Path

host = os.getenv("POSTGRES_HOST", "localhost")
port = int(os.getenv("POSTGRES_PORT", "5432"))
db = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")

root = Path("/app")
pattern = re.compile(r"^[A-Z]+\d+$")
branches = [p.name for p in root.iterdir() if p.is_dir() and pattern.match(p.name)]
if not branches:
    print("")
    raise SystemExit

conn = psycopg2.connect(
    host=host,
    port=port,
    dbname=db,
    user=user,
    password=password,
)
conn.autocommit = True
missing = []
with conn.cursor() as cur:
    cur.execute("SELECT datname FROM pg_database")
    existing_dbs = {row[0] for row in cur.fetchall()}

for branch in branches:
    db_name = f"yctc_{branch}"
    if db_name not in existing_dbs:
        missing.append(branch)
        continue
    try:
        bconn = psycopg2.connect(
            host=host,
            port=port,
            dbname=db_name,
            user=user,
            password=password,
        )
    except Exception:
        missing.append(branch)
        continue
    with bconn.cursor() as bcur:
        bcur.execute(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name LIKE %s LIMIT 1",
            ("%_stuadmn",),
        )
        has_stu = bcur.fetchone() is not None
    bconn.close()
    if not has_stu:
        missing.append(branch)

conn.close()
print(",".join(sorted(set(missing))))
PY
)

if [ -n "$MISSING_BRANCHES" ]; then
  BRANCH_FOLDERS="$MISSING_BRANCHES" python make_db.py
fi

exec "$@"
