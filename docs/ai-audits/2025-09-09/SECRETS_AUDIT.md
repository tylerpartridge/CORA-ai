# Secrets & Credentials Audit — CORA (2025-09-09)

## Executive Summary
Risk: **HIGH** — Real secrets are present in repository history and in the working tree. Immediate rotation and repository hygiene required.

## Critical Findings
1) Hardcoded DB password in deployment script (local/docker path)
   - Fix: read from env var; never commit credentials. (Separate code PR)

2) Committed secrets in `.env` files (JWT keys, API keys, Redis/admin/backup keys)
   - Fix: remove from VCS, rotate all exposed secrets, replace with `.env.example`.

## High/Medium
- Demo/test credentials printed or hardcoded
  - Fix: stop printing secrets; use env `DEMO_PASSWORD` and randomize defaults.

## Immediate Remediation Plan (P0)
- Remove `.env` files from git (keep local copies).
- Rotate the following immediately (generate new values; update prod envs):
  - JWT signing keys (SECRET_KEY, JWT_SECRET_KEY)
  - OpenAI API key
  - Stripe live secret + webhook secret
  - Redis password
  - Admin password
  - Backup encryption key
- Add `detect-secrets` pre-commit + CI scanning.

## Follow-up Remediation (P1)
- Patch scripts to use env-based secrets:
  - `scripts/postgresql_deployment.sh`: prompt/read env `DATABASE_PASSWORD`
  - `demo/setup_demo_data.py`: use `DEMO_PASSWORD` (no printing)
  - `scripts/create_demo_user.py`: use `DEMO_PASSWORD` (no hardcode)
- Remove token/password prints from tests.

## Rotation Commands (examples)
```bash
python -c "import secrets; print('SECRET_KEY='+secrets.token_urlsafe(64))"
python -c "import secrets; print('JWT_SECRET_KEY='+secrets.token_urlsafe(64))"
# Rotate other provider secrets in their dashboards; update server env files.
```

## Tracking
Open issues/PRs:

- PR-1 (this): docs audit + untrack .env
- PR-2: script patches (env-based, no prints)
- PR-3: add detect-secrets pre-commit + CI
- PR-4: history purge plan (BFG filter-repo) after rotations complete
