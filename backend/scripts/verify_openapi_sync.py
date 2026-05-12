import json, os, re, sys

def load_openapi(openapi_path: str) -> set:
    with open(openapi_path, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    return set(spec.get('paths', {}).keys())

def find_route_defs(root_dir: str) -> set:
    # Look for FastAPI route decorations like @router.get("/api/v1/..."), @router.post, etc.
    route_pattern = re.compile(r'@router\.(get|post|put|patch|delete)\s*\(\s*"([^"]+)"')
    found = set()
    for dirpath, _, filenames in os.walk(root_dir):
        for fn in filenames:
            if fn.endswith('.py'):
                path = os.path.join(dirpath, fn)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception:
                    continue
                for match in route_pattern.finditer(content):
                    found.add(match.group(2))
    return found

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    openapi_path = os.path.join(repo_root, 'openapi.json')
    openapi_paths = load_openapi(openapi_path)
    backend_root = os.path.join(repo_root, 'backend')
    backend_paths = find_route_defs(backend_root)
    missing_in_backend = openapi_paths - backend_paths
    extra_in_backend = backend_paths - openapi_paths
    if missing_in_backend:
        print('ERROR: The following paths are in openapi.json but NOT found in backend code:')
        for p in sorted(missing_in_backend):
            print('  ' + p)
    else:
        print('All openapi.json paths are present in backend code.')
    if extra_in_backend:
        print('\nNOTE: The following routes exist in backend but are not in openapi.json (may be intentional):')
        for p in sorted(extra_in_backend):
            print('  ' + p)
    else:
        print('No extra backend routes detected.')

if __name__ == '__main__':
    main()
