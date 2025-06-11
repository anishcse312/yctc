import os
import pyodbc
import pandas as pd

# Base path where the MS Access databases are stored
access_base_path = r"C:\Youth\N24"

# Directory where you're running this script (output folders exist here)
output_base_path = os.getcwd()

# List of consistent table names
table_names = [
    "BATCH", "EXAMTIME", "FORMRECV", "ICARDBOOKISSUE", "INSTREG", "LETTER",
    "MARKS", "RECEIPT", "REENROLL", "SCHOLARLIST", "STUADMN"
]

# Access DB password
db_password = "asa2012"

# Loop through all 82 folders/databases
for i in range(1, 83):
    db_folder = f"N24{i}"
    db_file = f"{db_folder}.accdb"
    db_path = os.path.join(access_base_path, db_file)

    # Skip if database is missing
    if not os.path.isfile(db_path):
        print(f"[SKIP] Missing DB: {db_path}")
        continue

    # Output folder
    output_folder = os.path.join(output_base_path, db_folder)
    os.makedirs(output_folder, exist_ok=True)

    # Connection string with password
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={db_path};"
        rf"PWD={db_password};"
    )

    try:
        conn = pyodbc.connect(conn_str)
        for table in table_names:
            try:
                df = pd.read_sql(f"SELECT * FROM [{table}]", conn)
                df.to_csv(os.path.join(output_folder, f"{table}.csv"), index=False, encoding='utf-8')
                print(f"[OK] Exported {table}.csv to {db_folder}")
            except Exception as e:
                print(f"[ERROR] Table {table} in {db_folder}: {e}")
        conn.close()
    except Exception as e:
        print(f"[ERROR] Cannot connect to {db_path}: {e}")
