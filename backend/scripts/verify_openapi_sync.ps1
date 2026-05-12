$openapi = Get-Content -Raw -Path "$(Resolve-Path "..\..\openapi.json")" | ConvertFrom-Json
$paths = $openapi.paths.Keys

$backendRoot = Resolve-Path "..\.."

$missing = @()
foreach ($p in $paths) {
    $escaped = [regex]::Escape($p)
    $found = Get-ChildItem -Path $backendRoot -Recurse -Include *.py |
        Select-String -Pattern "@router\.[a-z]+\s*\(\s*['\"]$escaped['\"]" -SimpleMatch
    if (-not $found) {
        $missing += $p
    }
}
if ($missing.Count -eq 0) {
    Write-Host "All OpenAPI paths are present in backend code."
} else {
    Write-Host "Missing paths in backend:"
    $missing | ForEach-Object { Write-Host $_ }
}
