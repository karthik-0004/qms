import importlib
import json
import sys
import argparse
from fastapi import FastAPI

def extract_openapi(import_path: str):
    """
    Import a FastAPI app from an import path (e.g. 'app.main:app')
    and return its OpenAPI schema as a JSON string.
    """
    try:
        module_path, app_name = import_path.split(":")
    except ValueError:
        print(f"Error: Invalid import path '{import_path}'. Expected format 'module.path:app_name'", file=sys.stderr)
        sys.exit(1)

    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        print(f"Error: Could not import module '{module_path}': {e}", file=sys.stderr)
        sys.exit(1)

    app = getattr(module, app_name, None)
    if not isinstance(app, FastAPI):
        print(f"Error: '{app_name}' in '{module_path}' is not a FastAPI instance", file=sys.stderr)
        sys.exit(1)

    return json.dumps(app.openapi(), indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract OpenAPI schema from a FastAPI app.")
    parser.add_argument("import_path", help="Import path to the FastAPI app (e.g., 'app.main:app')")
    args = parser.parse_args()

    print(extract_openapi(args.import_path))
