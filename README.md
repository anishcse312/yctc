# yctc

## Docker (app + database)
- Ensure `.env` has `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`.
- Build and start containers:
  ```bash
  docker compose up --build
  ```
- App listens on `http://localhost:8080`. Postgres is exposed on `localhost:5432`.
- Stop containers:
  ```bash
  docker compose down
  ```

## SQL schema (`app/db/init.sql`)
- The Postgres container runs `app/db/init.sql` automatically on first startup
  (only when the `pg_data` volume is empty).
- If you need to re-run the schema on a fresh database, remove the volume:
  ```bash
  docker compose down -v
  docker compose up --build
  ```
- If you want to re-run the SQL without recreating the volume, use the same
  credentials as in `.env`:
  ```powershell
  docker exec -i yctc_postgres psql -U $env:POSTGRES_USER -d $env:POSTGRES_DB -f /docker-entrypoint-initdb.d/init.sql
  ```

## Data loading (`make_db.py`)
`make_db.py` loads CSV data from branch folders (like `N24/`) into the hierarchical tables.

When to run it:
- After the database schema exists (via `init.sql`).
- Whenever you add new CSV data to the branch/session folders and want it imported.

How to run it:
1) Start the database container (`docker compose up --build`).
2) Set the branch folders to load in `make_db.py` (`BRANCH_FOLDERS`), or leave
   it empty to auto-discover folders that match the pattern (e.g., `N24`).
3) Run:
   ```bash
   python make_db.py
   ```

Notes:
- The script uses the same DB credentials as `.env`; install dependencies from
  `app/requirements.txt` if you run it outside Docker.
- The script inserts rows; it does not de-duplicate. Re-running it on the same
  data will create duplicates unless you reset the database.
