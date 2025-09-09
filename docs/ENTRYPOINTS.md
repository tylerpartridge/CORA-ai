# Entry Points — Developer Map

This quick map lists where to start for common tasks, with tests/guards and notes.

## Weekly Insights
- Files: routes/weekly_insights.py, services/weekly_report_service.py, services/email_service.py
- Tests: (manual) generate endpoint; CI covers basics via /ping /version
- Workflows/Guards: /smoke includes EmailService().health() (via facade), rate limits exempted for /smoke
- Notes: Uses BackgroundTasks; email is optional via null facade

## Export Filenames
- Files: utils/filenames.py; search in routes/* where exports occur; utils/pdf_exporter.py
- Tests: —
- Workflows/Guards: SYSTEM_RULES size guidance; naming policy by convention
- Notes: Target pattern cora_{type}_{email}_{YYYYMMDD}.csv

## Monitoring (uptime-sync)
- Files: .github/workflows/uptime-sync.yml
- Tests: Workflow behavior itself
- Workflows/Guards: Secret UPTIME_API_KEY_ROBOT; Var UPTIME_INTERVAL (defaults 300)
- Notes: Idempotent create of monitors for /health and /api/status

## Monitoring (postcheck)
- Files: .github/workflows/monitoring-postcheck.yml
- Tests: Workflow behavior itself
- Workflows/Guards: Secrets PROD_HOST, PROD_SSH_USER, PROD_SSH_KEY
- Notes: Fails if one-shot log stale (>90m) or probe log stale (>10m)

## TLS Renew
- Files: docs/INFRASTRUCTURE.md (nginx/vhost, cert/key paths)
- Tests: —
- Workflows/Guards: Manual runbook steps in OPERATIONS/INFRASTRUCTURE
- Notes: Use snap/apt instructions; dry-run first

## Auth / Session
- Files: routes/auth_coordinator.py, dependencies/auth.py
- Tests: CI smoke (unauth only); add targeted tests as needed
- Workflows/Guards: SlowAPI 10/min limit for /api/auth/login*
- Notes: JSON and form endpoints; cookie/token issuance paths

## Onboarding Skip
- Files: routes/onboarding_routes.py
- Tests: —
- Workflows/Guards: Feature exposed in STATUS/NOW; add tests as needed
- Notes: Search for “onboarding” actions to extend

## CSV / Exports
- Files: routes/*export*, utils/pdf_exporter.py
- Tests: —
- Workflows/Guards: Watch memory/size; large files split policy
- Notes: Confirm filename pattern integration

## Deploy
- Files: docs/FINAL_DEPLOYMENT_GUIDE.md, docs/DEPLOY_GUIDE.md, docs/INFRASTRUCTURE.md
- Tests: —
- Workflows/Guards: CI “Smoke” must be green; batch deploy windows (12:30/17:30 UTC)
- Notes: Follow runbooks; verify /ping, /version, /metrics, /smoke
