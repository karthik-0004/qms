import json, os, glob

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DOCS_DIR = os.path.join(ROOT_DIR, 'docs', 'APIs')
OUTPUT_FILE = os.path.join(ROOT_DIR, 'openapi.json')

merged = {
    "openapi": "3.1.0",
    "info": {
        "title": "Rainer Platform",
        "description": "Combined OpenAPI spec for all services",
        "version": "0.1.0"
    },
    "paths": {},
    "components": {"schemas": {}, "securitySchemes": {}, "responses": {}, "parameters": {}}
}

# Find all JSON files under docs/APIs (including subfolders)
for json_path in glob.glob(os.path.join(DOCS_DIR, '*', '*.json')):
    with open(json_path, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    # Merge top‑level keys (paths, components)
    for path, definition in spec.get('paths', {}).items():
        if path in merged['paths']:
            # If a path already exists, we keep the existing definition (should not happen)
            continue
        merged['paths'][path] = definition
    for comp_type, comp_dict in spec.get('components', {}).items():
        if comp_type not in merged['components']:
            merged['components'][comp_type] = {}
        for name, schema in comp_dict.items():
            if name in merged['components'][comp_type]:
                continue
            merged['components'][comp_type][name] = schema

# Write the combined spec
with open(OUTPUT_FILE, 'w', encoding='utf-8') as out_f:
    json.dump(merged, out_f, indent=4, ensure_ascii=False)

print(f"Combined OpenAPI spec written to {OUTPUT_FILE}")
