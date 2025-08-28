# (paste the whole script from above here)

# CI top guard: bail out early in GitHub Actions; infra checks enforced on PROD only.
if ($env:GITHUB_ACTIONS -eq "true") {
  Write-Output "✅ CI mode: infra checks skipped (enforced on PROD only)"
  exit 0
}


