param(
  [ValidateSet('qms', 'platform', 'all')]
  [string]$Stack = 'qms',
  [int]$TimeoutSec = 180
)

$ErrorActionPreference = 'Stop'

function Get-RepoRoot {
  $start = Split-Path -Parent $PSScriptRoot
  $here = $start
  while ($true) {
    if (Test-Path (Join-Path $here 'docker-compose.yml')) { return $here }
    $parent = Split-Path -Parent $here
    if ($parent -eq $here) { throw "Could not find docker-compose.yml above $start" }
    $here = $parent
  }
}

function Require-Docker {
  try {
    docker version | Out-Null
  } catch {
    throw "Docker is not available. Start Docker Desktop and retry."
  }
}

function Invoke-ComposeUp {
  param([string[]]$Services)
  Push-Location (Get-RepoRoot)
  try {
    if ($Services.Count -eq 0) { throw "No services provided" }
    docker compose up -d @Services | Out-Host
  } finally {
    Pop-Location
  }
}

function Wait-HttpOk {
  param(
    [string]$Url,
    [int]$TimeoutSecLocal
  )
  $deadline = (Get-Date).AddSeconds($TimeoutSecLocal)
  while ((Get-Date) -lt $deadline) {
    try {
      $resp = Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 -Uri $Url
      if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) { return $true }
    } catch {
      Start-Sleep -Seconds 2
    }
  }
  return $false
}

Require-Docker

$infra = @('postgres', 'redis', 'zookeeper', 'kafka', 'schema-registry', 'minio')

$platform = @(
  'auth-service-init', 'auth-service', 'tenant-service', 'user-service', 'audit-service', 'gateway-service',
  'notification-service', 'config-service', 'workflow-engine', 'file-service', 'schedule-service',
  'reporting-service', 'analytics-service'
)

$qms = @(
  'document-service', 'quality-event-service', 'capa-service', 'training-service', 'equipment-service'
)

switch ($Stack) {
  'platform' { Invoke-ComposeUp -Services ($infra + $platform) }
  'qms'      { Invoke-ComposeUp -Services ($infra + @('auth-service-init', 'auth-service', 'gateway-service', 'workflow-engine', 'file-service') + $qms) }
  'all'      { Invoke-ComposeUp -Services ($infra + $platform + $qms) }
}

Write-Host ""
Write-Host "Waiting for core Swagger endpoints..."

$checks = @(
  @{ name = 'gateway'; url = 'http://localhost:8000/docs' },
  @{ name = 'documents'; url = 'http://localhost:8020/docs' },
  @{ name = 'quality-events'; url = 'http://localhost:8021/docs' }
)

foreach ($c in $checks) {
  $ok = Wait-HttpOk -Url $c.url -TimeoutSecLocal $TimeoutSec
  $status = if ($ok) { 'OK' } else { 'NOT READY' }
  Write-Host ("- {0,-15} {1}  ({2})" -f $c.name, $status, $c.url)
}

Write-Host ""
Write-Host "Tip: run backend/scripts/dev-check.ps1 to see port status."
