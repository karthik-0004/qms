import json
import glob
import os

docs_dir = r"c:\Users\mail\Downloads\qms-clubed\qms-clubed\docs\APIs\qms"
files = glob.glob(os.path.join(docs_dir, "*.json"))

for file_path in files:
    filename = os.path.basename(file_path)
    print(f"\n--- {filename} ---")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            paths = data.get("paths", {})
            for path, methods in paths.items():
                for method in methods.keys():
                    # Only print standard HTTP methods
                    if method in ["get", "post", "put", "delete", "patch"]:
                        print(f"{method.upper()} {path}")
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
