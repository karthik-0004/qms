param(
  [ValidateSet('qms', 'platform', 'em', 'ccv', 'all')]
  [string]$Stack = 'qms',
  [int]$TimeoutSec = 180
)

$ErrorActionPreference = 'Stop'

function Get-RepoRoot {
  $start = Split-Path -Parent $PSScriptRoot
  $here = $start
  while ($true) {
    if (Test-Path (Join-Path $here 'docker-compose.infra.yml')) { return $here }
    $parent = Split-Path -Parent $here
    if ($parent -eq $here) { throw "Could not find docker-compose.infra.yml above $start" }
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

function Start-Stack {
  param([string]$ComposeFile)
  Push-Location (Get-RepoRoot)
  try {
    docker compose -f docker-compose.infra.yml up -d | Out-Host
    docker compose -f $ComposeFile up -d | Out-Host
  } finally {
    Pop-Location
  }
}

function Wait-HttpOk {
  param([string]$Url, [int]$TimeoutSecLocal)
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

switch ($Stack) {
  'platform' { Start-Stack -ComposeFile 'docker-compose.platform.yml' }
  'qms'      { Start-Stack -ComposeFile 'docker-compose.qms.yml' }
  'em'       { Start-Stack -ComposeFile 'docker-compose.em.yml' }
  'ccv'      { Start-Stack -ComposeFile 'docker-compose.ccv.yml' }
  'all'      {
    Start-Stack -ComposeFile 'docker-compose.platform.yml'
    docker compose -f (Join-Path (Get-RepoRoot) 'docker-compose.qms.yml') up -d | Out-Host
    docker compose -f (Join-Path (Get-RepoRoot) 'docker-compose.em.yml') up -d | Out-Host
    docker compose -f (Join-Path (Get-RepoRoot) 'docker-compose.ccv.yml') up -d | Out-Host
  }
}

Write-Host ""
Write-Host "Waiting for gateway..."
$ok = Wait-HttpOk -Url 'http://localhost:8000/docs' -TimeoutSecLocal $TimeoutSec
$status = if ($ok) { 'OK' } else { 'NOT READY' }
Write-Host "- gateway $status  (http://localhost:8000/docs)"

if ($Stack -in @('qms', 'all')) {
  $ok = Wait-HttpOk -Url 'http://localhost:8020/docs' -TimeoutSecLocal $TimeoutSec
  $status = if ($ok) { 'OK' } else { 'NOT READY' }
  Write-Host "- documents $status  (http://localhost:8020/docs)"
}

Write-Host ""
Write-Host "Containers are grouped in Docker Desktop as:"
Write-Host "  infra / platform / qms / em / ccv"
