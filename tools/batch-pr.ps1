param(
  [ValidateSet("midday","eod","status")]
  [string]$mode = "status"
)

function Ensure-GH {
  if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI (gh) not found. Install: winget install --id GitHub.cli -e ; then run: gh auth login"
  }
}

# Ensure working on daily branch work/YYYY-MM-DD
$today = (Get-Date -Format "yyyy-MM-dd")
$branch = (git rev-parse --abbrev-ref HEAD 2>$null)
if (-not $branch -or $branch -eq "HEAD" -or -not ($branch -like "work/*")) {
  $branch = "work/$today"
  git checkout -B $branch | Out-Null
}

if ($mode -eq "status") {
  Ensure-GH
  gh pr view $branch --json number,state,mergeStateStatus,url | Out-String | Write-Host
  exit 0
}

# Snapshot → rebase pull → push
git add -A
git commit -m "wip: batch snapshot ($mode)" --no-verify 2>$null | Out-Null
git pull --rebase | Out-Null
git push -u origin $branch | Out-Null

# PR create/update
Ensure-GH
$todayTitle = "daily batch — $today — $mode"
$prExists = $false
try { gh pr view $branch 1>$null 2>$null; $prExists = $true } catch {}

if (-not $prExists) {
  $draft = ($mode -eq "midday") ? "--draft" : ""
  gh pr create --base main --head $branch --title "$todayTitle" --body "$mode batch" $draft
} else {
  if ($mode -eq "midday") {
    gh pr edit $branch --title "$todayTitle" --draft
  } else {
    gh pr ready $branch
    gh pr edit  $branch --title "$todayTitle"
  }
}

if ($mode -eq "eod") {
  # Auto-merge with squash when CI passes
  gh pr merge $branch --squash --auto
}

Write-Host "✅ $mode batch complete on $branch"
