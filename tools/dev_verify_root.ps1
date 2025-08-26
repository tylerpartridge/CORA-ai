$keep = @(
  'BOOTUP.md','STATE.md','MISSION.md','OPERATIONS.md','MEMORY.md','README.md','AI_WORK_LOG.md',
  'app.py','Makefile','requirements.txt','Dockerfile',
  '.gitignore','.gitattributes','.editorconfig','.env','.env.example','NO_TOOL_BACKUPS.md',
  'pyproject.toml','backups'
)
$files  = Get-ChildItem -File -Force -Name
$links  = Get-ChildItem -Force | Where-Object { $_.LinkType } | Select-Object -ExpandProperty Name
$unknown = @()
$unknown += $files | Where-Object { $keep -notcontains $_ }
$unknown += $links | Where-Object { $keep -notcontains $_ }
if ($unknown.Count -gt 0) {
  Write-Host "❌ Dev root verify FAILED. Unknown files:" -ForegroundColor Red
  $unknown | ForEach-Object { "  - $_" } | Write-Host
  exit 1
}
Write-Host "✅ Dev root verify PASSED" -ForegroundColor Green
