import csv
import os
import re

from app.util.database import (
    upsert_json_row,
    insert_receipt_rows,
    upsert_session,
)


BASE_PATH = r"C:\yctc\N24"
SESSION_DIR_PATTERN = re.compile(r"N24(\d+)")

TABLE_MAP = {
    "STUADMN": "stuadmn",
    "FORMRECV": "formrecv",
    "REENROLL": "reenroll",
    "RECEIPT": "receipt",
    "MARKS": "marks",
    "INSTREG": "instreg",
}


def get_reg_no(record):
    for key in ("reg_no", "regno", "registration_no", "registrationNumber", "RegNo"):
        if key in record and record[key]:
            return str(record[key]).strip()
    return None


def load_csv(file_path):
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]


def process_session_folder(folder_path, session_num):
    for file_name in os.listdir(folder_path):
        if not file_name.lower().endswith(".csv"):
            continue
        raw_table = file_name.rsplit(".", 1)[0].upper()
        table = TABLE_MAP.get(raw_table)
        if not table:
            print(f"[SKIP] Unknown table for {file_name}")
            continue

        file_path = os.path.join(folder_path, file_name)
        rows = load_csv(file_path)
        if not rows:
            print(f"[WARN] Empty CSV: {file_name}")
            continue

        print(f"  [INFO] Loading {len(rows)} rows into {table}")
        if table == "receipt":
            payloads = []
            for row in rows:
                reg_no = get_reg_no(row)
                if not reg_no:
                    continue
                payload = {k: v for k, v in row.items()}
                payloads.append((reg_no, payload))
            grouped = {}
            for reg_no, payload in payloads:
                grouped.setdefault(reg_no, []).append(payload)
            for reg_no, payload_list in grouped.items():
                insert_receipt_rows(session_num, reg_no, payload_list)
            continue

        for row in rows:
            reg_no = get_reg_no(row)
            if not reg_no:
                continue
            payload = {k: v for k, v in row.items()}
            upsert_json_row(table, session_num, reg_no, payload)


def main():
    for folder_name in os.listdir(BASE_PATH):
        match = SESSION_DIR_PATTERN.fullmatch(folder_name)
        if not match:
            continue
        session_num = int(match.group(1))
        folder_path = os.path.join(BASE_PATH, folder_name)
        if not os.path.isdir(folder_path):
            continue
        print(f"[INFO] Processing {folder_name}")
        upsert_session(session_num, 0)
        process_session_folder(folder_path, session_num)


if __name__ == "__main__":
    main()
