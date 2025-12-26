import csv
import re
from pathlib import Path

from util.database import (
    branch_db_name,
    create_database_if_missing,
    ensure_branch_schema,
    ensure_data_table,
    insert_rows,
    session_table_name,
    upsert_session,
)


DATA_ROOT = Path(__file__).resolve().parent / "data"
BATCH_SIZE = 1000

# Optional: set explicit branch folders to load (e.g., ["N24", "M32"]).
# Leave empty to auto-discover folders in data/ that match BRANCH_PATTERN.
BRANCH_FOLDERS = ['N24','M32']

BRANCH_PATTERN = re.compile(r"^[A-Z]+\d+$")

TABLE_MAP = {
    "BATCH": "batch",
    "EXAMTIME": "examtime",
    "FORMRECV": "formrecv",
    "ICARDBOOKISSUE": "icardbookissue",
    "INSTREG": "instreg",
    "LETTER": "letter",
    "MARKS": "marks",
    "RECEIPT": "receipt",
    "REENROLL": "reenroll",
    "SCHOLARLIST": "scholarlist",
    "STUADMN": "stuadmn",
}


def normalize_header(name):
    cleaned = re.sub(r"[^0-9a-zA-Z_]+", "_", name.strip())
    cleaned = cleaned.strip("_").lower()
    if cleaned == "user":
        return "user_name"
    return cleaned


def clean_value(value):
    if value is None:
        return None
    value = str(value).strip()
    return value if value else None


def iter_branch_folders():
    if BRANCH_FOLDERS:
        for name in BRANCH_FOLDERS:
            yield DATA_ROOT / name
        return

    if not DATA_ROOT.exists():
        print(f"[WARN] Data directory not found: {DATA_ROOT}")
        return

    for path in DATA_ROOT.iterdir():
        if path.is_dir() and BRANCH_PATTERN.match(path.name):
            yield path


def parse_session_num(branch_code, folder_name):
    if not folder_name.startswith(branch_code):
        return None
    suffix = folder_name[len(branch_code):]
    if not suffix.isdigit():
        return None
    return int(suffix)


def process_csv(file_path, table, branch_code, session_num):
    db_name = branch_db_name(branch_code)
    table_name = session_table_name(session_num, table)
    with file_path.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        if not reader.fieldnames:
            print(f"  [WARN] Empty CSV: {file_path.name}")
            return

        original_headers = reader.fieldnames
        normalized_headers = [normalize_header(h) for h in original_headers]
        ensure_data_table(db_name, table_name, normalized_headers, cursor_name=branch_code)

        batch = []
        saw_rows = False
        for row in reader:
            saw_rows = True
            values = [clean_value(row.get(h)) for h in original_headers]
            batch.append(values)
            if len(batch) >= BATCH_SIZE:
                insert_rows(
                    table_name,
                    normalized_headers,
                    batch,
                    db_name=db_name,
                    cursor_name=branch_code,
                )
                batch = []

        if batch:
            insert_rows(
                table_name,
                normalized_headers,
                batch,
                db_name=db_name,
                cursor_name=branch_code,
            )

        if not saw_rows:
            print(f"  [WARN] Empty CSV: {file_path.name}")


def process_session_folder(folder_path, branch_code, session_num):
    for csv_file in sorted(folder_path.glob("*.csv")):
        raw_table = csv_file.stem.upper()
        base_table = TABLE_MAP.get(raw_table)
        if not base_table:
            print(f"  [SKIP] Unknown table for {csv_file.name}")
            continue
        table_name = session_table_name(session_num, base_table)
        print(f"  [INFO] Loading {csv_file.name} -> {table_name}")
        process_csv(csv_file, base_table, branch_code, session_num)


def main():
    for branch_path in sorted(iter_branch_folders(), key=lambda p: p.name):
        if not branch_path.exists():
            print(f"[WARN] Missing branch folder: {branch_path}")
            continue

        branch_code = branch_path.name
        db_name = branch_db_name(branch_code)
        create_database_if_missing(db_name)
        ensure_branch_schema(db_name, cursor_name=branch_code)
        print(f"[INFO] Processing branch {branch_code}")

        for session_path in sorted(branch_path.iterdir(), key=lambda p: p.name):
            if not session_path.is_dir():
                continue
            session_num = parse_session_num(branch_code, session_path.name)
            if session_num is None:
                continue
            print(f"[INFO]  Session {session_num} ({session_path.name})")
            upsert_session(branch_code, session_num, None)
            process_session_folder(session_path, branch_code, session_num)


if __name__ == "__main__":
    main()
