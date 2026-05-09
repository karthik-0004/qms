param(
  [int]$TimeoutSec = 3
)

$ErrorActionPreference = 'Stop'

function Test-Http {
  param([string]$Url)
  try {
    $resp = Invoke-WebRequest -UseBasicParsing -TimeoutSec $TimeoutSec -Uri $Url
    return [int]$resp.StatusCode
  } catch {
    return $null
  }
}

$targets = @(
  @{ name = 'gateway swagger'; url = 'http://localhost:8000/docs' },
  @{ name = 'auth swagger'; url = 'http://localhost:8001/docs' },
  @{ name = 'documents swagger'; url = 'http://localhost:8020/docs' },
  @{ name = 'quality-events swagger'; url = 'http://localhost:8021/docs' },
  @{ name = 'capa swagger'; url = 'http://localhost:8022/docs' },
  @{ name = 'training swagger'; url = 'http://localhost:8023/docs' },
  @{ name = 'equipment swagger'; url = 'http://localhost:8024/docs' }
)

Write-Host "HTTP checks (null = refused/unreachable):"
foreach ($t in $targets) {
  $code = Test-Http -Url $t.url
  $codeText = if ($null -eq $code) { 'null' } else { $code.ToString() }
  Write-Host ("- {0,-22} {1,-4}  {2}" -f $t.name, $codeText, $t.url)
}

Write-Host ""
Write-Host "Docker containers (filtered):"
try {
  docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Select-String "qms-clubed-|document-service|quality-event-service|gateway-service|auth-service"
} catch {
  Write-Host "Docker not available/running."
}
