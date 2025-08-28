Write-Host "🌙 CORA — End of Day" -ForegroundColor Cyan
.\tools\dev_verify_root.ps1 || exit 1

git status --short
$branch = (git rev-parse --abbrev-ref HEAD)
if ($branch -eq "main") {
  Write-Host "On main — committing any staged work…" -ForegroundColor Yellow
  git add -A
  git commit -m "chore: end-of-day checkpoint" 2>$null
  git pull --rebase origin main
  git push
} else {
  Write-Host "On branch '$branch' — checkpoint + push" -ForegroundColor Yellow
  git add -A
  git commit -m "chore: end-of-day checkpoint on $branch" 2>$null
  git pull --rebase origin $branch
  git push -u origin $branch
}
Write-Host "✅ EOD complete"
