# INFRASTRUCTURE

Last verified: 2025-08-25 UTC

## Overview
FastAPI monolith served by uvicorn (systemd) on a DigitalOcean Ubuntu host. nginx terminates HTTP(S) and proxies to the app on :8000.

## Domains & TLS
- Domain: coraai.tech
- TLS: nginx active on :443

## Hosts / OS
- Ubuntu 24.10 (prod)
- System service: cora.service (uvicorn)

## Runtime / Ports
- App: 0.0.0.0:8000 (uvicorn via systemd)
- Frontend proxy: nginx on :80 and :443 → proxy to :8000 (see nginx include with upstream 8000)

## Data / DB
- Current DB: **SQLite** (default) → `sqlite:///./cora.db`
- Client binaries present: `psql 16.9` (not used), `sqlite3 3.46.1` (used by scripts)

## Env & Secrets
- `/var/www/cora/.env`
  - REQUIRED: SECRET_KEY, OPENAI_API_KEY
  - Optional: SENTRY_DSN, SENDGRID, STRIPE, PLAID

## Deploy / Services
- Service unit: `/etc/systemd/system/cora.service` (+ override)
- Start/stop: `systemctl (re)start cora.service`
- Health: `curl -sS localhost:8000/health`

## Backups & Saves
- Timers: `cora-save.timer` (15m), `cora-backup.timer` (03:15 UTC)
- Manual: `cora save` and `cora-health`

## Monitoring
- Prometheus client, psutil metrics hooks
- (TODO) Sentry DSN and external uptime checks

## Runbooks (short)
- App down: `journalctl -u cora.service -n 100 -o cat`, fix, `systemctl restart cora.service`
- Port check: `ss -ltnp | grep -E ':8000|:80|:443'`
- Nginx: `systemctl status nginx`, reload after changes: `nginx -t && systemctl reload nginx`

## TODO (carry-forward)
- Confirm nginx site config checked into repo (proxy → :8000), document file path(s)
- SPF/DKIM/DMARC records for email provider
- Decide DB future (stick with SQLite or move to Postgres) + backup/restore policy
- Enable Sentry + uptime monitor
- (Optional) blue/green or zero-downtime restart pattern
