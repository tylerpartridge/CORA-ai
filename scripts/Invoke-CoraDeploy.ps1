param(
  [string]$Server = "159.203.183.48",
  [string]$Path = "/var/www/cora",
  [int]$TimeoutSec = 8
)

$ErrorActionPreference = "Stop"

function Invoke-Remote {
  param([string]$Cmd)
  ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new "root@$Server" $Cmd
}

Write-Host "==> Deploying to $Server ..." 

# 1) Pull latest code and restart service
$remoteScript = @"
set -euo pipefail
cd $Path
git pull --prune
systemctl restart cora.service
sleep 1
systemctl status cora.service --no-pager || true
"@

Invoke-Remote $remoteScript

# 2) Lightweight smokes (origin requests)
function Test-HttpOk {
  param([string]$Url)
  try {
    $res = curl.exe --max-time $TimeoutSec -s -o NUL -w "%{http_code}" "$Url"
    if ($res -ge 200 -and $res -lt 300) { return $true } else { return $false }
  } catch { return $false }
}

$health = Test-HttpOk "https://coraai.tech/health"
$status = Test-HttpOk "https://coraai.tech/api/status"

if ($health -and $status) {
  Write-Host "✅ Post-deploy smokes passed: /health + /api/status OK"
  exit 0
} else {
  Write-Warning "⚠️ One or more smokes failed."
  Write-Host "Try: journalctl -u cora.service -n 200 --no-pager"
  exit 1
}
