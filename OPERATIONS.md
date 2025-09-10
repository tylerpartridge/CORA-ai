# OPERATIONS

## Bootup Discipline
- Bootup must honor Optional block: `# present` → hydrate, `# optional` → skip

### Dev Launch (Windows)
- Run locally with `python -m uvicorn app:app --reload` to ensure the virtualenv interpreter is used for the reloader.

## Checkpoint Discipline

### Mandatory Checkpoint Rules
- **Before merges** → Must have valid checkpoint in all awareness files
- **Before major operations** → Database migrations, production deploys, architecture changes
- **Before multi-agent tasks** → Deploy checkpoint before parallel agent operations
- **Before handoffs** → AI session transfers require synchronized awareness state

### Checkpoint Requirements
- All 5 core files updated: STATE.md, NEXT.md, AI_WORK_LOG.md, HANDOFF.md, AIM.md
- Each file must have checkpoint capsule with timestamp and status
- Files must be synchronized and consistent across all awareness data

### Compaction & Archiving Policies
- **AI_WORK_LOG.md** → Archive when >300 lines, keep last 2 weeks active
- **SPARKS.md** → Prune completed items every Friday
- **NEXT.md** → Prune at sprint close, archive old priorities

**Reference:** Complete checkpoint system defined in `/docs/ai-awareness/CHECKPOINT_SYSTEM.md`

## TLS Renewal

Renew Let's Encrypt TLS **before Sep 19, 2025**.

**Commands:**
sudo certbot renew --dry-run
sudo certbot renew

**Reference:** nginx on :443; renewal managed on the prod droplet.

## Monitoring (Minimal Set)

Run lightweight monitoring without adding infrastructure, aligned with docs/INFRASTRUCTURE.md.

- One-time Sentry test (only if `SENTRY_DSN` is configured):
  - `python tools/sentry_test.py`

- Local uptime probe (every 5 minutes):
  - Default base URL is `http://127.0.0.1:8000` (override with `BASE` env).
  - Appends lines to `logs/cora_uptime_probe.log` like: `2025-09-09T15:00:00Z health=200 status=200`.

Windows (Task Scheduler):
- Example (adjust paths, ensure venv):
  - `schtasks /Create /TN "CORA Uptime Probe" /SC MINUTE /MO 5 /TR "cmd /c cd C:\CORA && C:\CORA\.venv\Scripts\python.exe tools\uptime_probe.py" /F`

Linux (cron):
- Example (runs every 5 minutes):
  - `*/5 * * * * BASE=http://127.0.0.1:8000 /usr/bin/python3 /var/www/cora/tools/uptime_probe.py >> /var/log/cora_uptime_probe.log 2>&1`

Notes:
- For systemd timers, set `Environment=BASE=...` and `ExecStart=/usr/bin/python3 /var/www/cora/tools/uptime_probe.py`.
- Sentry test prints "Sentry DSN not set; skipping" when DSN is absent and exits 0.

## Monitoring – Batch Windows

- Windows Scheduled Task: "CORA Monitoring Minimal Set" runs daily at 17:30Z (local next run: 2025-09-09 15:00)
- Command used (run in elevated PowerShell):
  - schtasks /Create /TN "CORA Monitoring Minimal Set" /TR "powershell -ExecutionPolicy Bypass -NoProfile -NonInteractive -File \"C:\CORA\scripts\run_monitoring.ps1\"" /SC DAILY /ST 15:00 /RU SYSTEM /RL HIGHEST /F

- Exported XML: C:\CORA\scheduled_task_export.xml
- Check next run:
  - schtasks /Query /TN "CORA Monitoring Minimal Set" /FO LIST | sls "Next Run Time"

### Verification (Windows)
- Daily assertion task to re-check and log:
  - Script: C:\CORA\scripts\verify_monitoring_task.ps1
  - Schedule suggestion: 15:05 local, SYSTEM
  - Create (elevated PowerShell):
    - schtasks /Create /TN "CORA Monitoring Verify" /TR "powershell -ExecutionPolicy Bypass -NoProfile -NonInteractive -File \"C:\CORA\scripts\verify_monitoring_task.ps1\"" /SC DAILY /ST 15:05 /RU SYSTEM /RL HIGHEST /F

## CORS & Security

Configure production hardening with environment variables:

- CORS (disabled by default):
  - `CORS_ENABLED=true`
  - `CORS_ORIGINS=https://coraai.tech,https://app.coraai.tech`
  - Optional: `CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS`
  - Optional: `CORS_HEADERS=*`
  - Optional: `CORS_CREDENTIALS=true`

- Trusted hosts and HTTPS:
  - `TRUSTED_HOSTS=coraai.tech,api.coraai.tech,www.coraai.tech`
  - `ENV=prod` (or `CORA_ENV=prod`) to enable HTTPS redirects

Security headers are added automatically to all responses:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: no-referrer`
- `Strict-Transport-Security` is sent only over HTTPS.

## Structured Logging

Enable JSON logs and optional file output via env:

```
LOG_FORMAT=json
LOG_LEVEL=INFO
LOG_FILE=/var/log/cora/app.log
```

Notes:
- Default (unset): human-readable text logs remain.
- JSON logs include `request_id` (X-Request-ID); per-request access lines have `message="access"` and fields `method`, `path`, `status_code`, `duration_ms`, `user_agent`, `client_ip`.
- If `LOG_FILE` is set, logs are also written with rotation (10MB x5) and console continues.

## HTTP Smoke (no deps)

Run an end-to-end HTTP smoke using only stdlib (good for CI and prod probes):

Local:
```
BASE=http://127.0.0.1:8000 python tools/smoke_http.py
```

Production (admin token required for /smoke):
```
BASE=https://coraai.tech ADMIN_TOKEN=YOUR_TOKEN python tools/smoke_http.py
```

Checks performed:
- /ping → 200, JSON {"ok": true}, echoes X-Request-ID; security headers present
- /version → 200, JSON semver
- /metrics → 200, text/plain with standard metrics
- /smoke → 200 with token (or localhost when no token); JSON status + checks; Cache-Control no-store

Output prints PASS/FAIL per check and a final OVERALL line; non-zero exit on failures.

## CI Smoke

GitHub Actions runs a lightweight HTTP smoke on push/PR to `main`.

Badge:

```
![Smoke](https://github.com/tylerpartridge/CORA-ai/actions/workflows/smoke.yml/badge.svg)
```

Notes:
- The workflow boots the app with uvicorn on port 8001 and runs `tools/smoke_http.py` against it.
- If `ADMIN_TOKEN` is set in repo/org secrets, it is passed to the smoke; otherwise /smoke is allowed only for localhost.
- On failures, the last ~200 lines of the app log are printed in the job output; the job must pass for merges.

Secrets:
- `ADMIN_TOKEN` is optional. When set, the smoke will authenticate to `/smoke`; when not set, the smoke still passes (it exercises `/smoke` in localhost-only mode).

Workflow link:
- https://github.com/tylerpartridge/CORA-ai/actions/workflows/smoke.yml

## External Uptime Monitoring

Keep external uptime checks in sync with UptimeRobot.

- Secret: `UPTIME_API_KEY_ROBOT` (UptimeRobot Main API Key)
- Trigger: `gh workflow run uptime-sync.yml` or push to `main` touching `.github/workflows/uptime-sync.yml` or `docs/OPERATIONS.md`
- No-op when the secret is absent; safely idempotent when present.
 - Interval: defaults to `300` seconds (free tier). On paid plans, set a repo/org variable `UPTIME_INTERVAL=60` to use 60-second checks (no code changes required).

Workflow:
- `.github/workflows/uptime-sync.yml` creates (if missing) and validates monitors:
  - `https://coraai.tech/health` (CORA Health Check)
  - `https://coraai.tech/api/status` (CORA API Status)
- Fails CI if any monitor is DOWN for >5 minutes at check time.

### External Uptime – Maintenance Mode

**Pause monitors before deploy:**
```bash
IDS=$(curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "api_key=$UPTIME_API_KEY&format=json" "https://api.uptimerobot.com/v2/getMonitors" \
 | jq -r '.monitors[]? | select(.friendly_name=="CORA Health Check" or .friendly_name=="CORA API Status") | .id'); \
for ID in $IDS; do curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "api_key=$UPTIME_API_KEY&format=json&id=$ID&status=0" "https://api.uptimerobot.com/v2/editMonitor"; done
```

**Resume monitors after deploy:**
```bash
for ID in $IDS; do curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "api_key=$UPTIME_API_KEY&format=json&id=$ID&status=1" "https://api.uptimerobot.com/v2/editMonitor"; done
```

**Check status:**
```bash
curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "api_key=$UPTIME_API_KEY&format=json" "https://api.uptimerobot.com/v2/getMonitors" \
 | jq '.monitors[]? | {name: .friendly_name, status: .status}'
```

### Fetch last Smoke logs (gh)

PowerShell example using GitHub CLI:

```
$wfId = gh api repos/tylerpartridge/CORA-ai/actions/workflows --jq '.workflows[] | select(.path==".github/workflows/smoke.yml") | .id'
$runId = gh api repos/tylerpartridge/CORA-ai/actions/workflows/$wfId/runs --jq '.workflow_runs[0].id'
gh run view $runId --web
# Or list jobs and tail the first job logs:
gh api repos/tylerpartridge/CORA-ai/actions/runs/$runId/jobs --jq '.jobs[] | {id,name,status,conclusion}'
$jobId = gh api repos/tylerpartridge/CORA-ai/actions/runs/$runId/jobs --jq '.jobs[0].id'
gh run view --job $jobId --log
```
- Next run (local): 2025-09-10 3:05:00 PM
