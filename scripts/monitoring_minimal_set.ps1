Param(
  [string]$HostName = "159.203.183.48"
)
$ErrorActionPreference = "Stop"
if (-not (Test-Path scripts/monitoring_minimal_set.sh)) {
  Write-Error "scripts/monitoring_minimal_set.sh not found in C:\CORA"
  exit 1
}
Write-Host "[CORA] Executing monitoring_minimal_set.sh on $HostName..."
ssh -o BatchMode=yes root@$HostName "bash -s" < scripts/monitoring_minimal_set.sh
Write-Host "[CORA] Remote one-shot completed."

