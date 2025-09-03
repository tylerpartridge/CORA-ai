$ErrorActionPreference = "Stop"
$log = "C:\CORA\backups\scheduled.log"
Start-Transcript -Path $log -Append | Out-Null
try {
  & "C:\CORA\tools\backup\nightly_backup.ps1"
  $code = $LASTEXITCODE
} catch {
  $code = 1
  Write-Error $_
}
Stop-Transcript | Out-Null
# Intentionally do NOT call 'exit' to avoid closing interactive shells.
# Task Scheduler will still run this in its own process.