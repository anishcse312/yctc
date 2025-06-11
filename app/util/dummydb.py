import os
import pandas as pd
from database import *


# Path to your root directory with N24 folders
base_path = r"C:\yctc\N24"

# Process all N24[1-82] folders
for i in range(1, 83):
    folder_name = f"N24{i}"
    folder_path = os.path.join(base_path, folder_name)

    if not os.path.isdir(folder_path):
        print(f"[SKIP] Folder not found: {folder_path}")
        continue

    print(f"[INFO] Processing {folder_name}")
    db = createNewDB(folder_name)

    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(".csv"):
            collection_name = file_name.rsplit(".", 1)[0]
            file_path = os.path.join(folder_path, file_name)

            try:
                df = pd.read_csv(file_path)
                records = df.to_dict(orient="records")
                if records:
                    db[collection_name].insert_many(records)
                    print(f"  [OK] Inserted {len(records)} docs into {collection_name}")
                else:
                    print(f"  [WARN] Empty CSV: {file_name}")
            except Exception as e:
                print(f"  [ERROR] Failed to insert {file_name}: {e}")
