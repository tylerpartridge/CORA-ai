# 2025-09-06 — PROD hotfix: auth, error handler, prefs persistence

## TL;DR
- PROD is **healthy**. Front-door `GET /api/status` and `/health` return **200**.
- Auth flow fixed; cookie-based login works; settings persistence (timezone/currency) verified end-to-end.
- Temporary on-box fixes are captured in **PR #73** (hotfix) — merge in batch window to align repo ↔ prod.

## What changed (code & config)
- **Error handling**
  - `ErrorHandler()` now initialized **with no args**.
  - Global error handler now calls `ErrorHandler.log_error(request, exception)` (argument order fixed).
- **Auth**
  - `routes/auth_coordinator.py`:
    - After `authenticate_user(...)`, explicitly guard `if not user: raise InvalidCredentialsError`.
    - Unified exception mapping to return 400/401/500 appropriately.
    - JSON login expects a JSON object: `{"email": "...", "password": "...", "remember_me": true|false}` and on success sets `Set-Cookie: access_token` (HttpOnly, SameSite=Lax, Secure; Max-Age 30d if remember_me).
- **PDF exporter**
  - `utils/pdf_exporter.py`: add compatibility alias `PDFExporter = ProfitIntelligencePDFExporter`.
- **Schema**
  - Add `users.currency VARCHAR(3) NOT NULL DEFAULT 'USD'`.
  - Idempotent SQL migration added: `schema/migrations/2025-09-06_add_user_currency.sql`.
- **Deps**
  - Add/ensure: `passlib>=1.7.4`, `bcrypt>=4.1.0` (bcrypt backend issue observed without pin).

## Prod actions performed (one-off, already done)
- Applied the **currency** column via SQL (`ALTER TABLE ... IF NOT EXISTS ...`).
- Corrected error handler usage in `app.py`.
- Patched `auth_coordinator.py` guard.
- Ensured login succeeds and emits cookie.
- **Freed disk space** (rotated large `/var/backups/cora/system` archives) to resolve 100% full root volume causing 502 startup issues.

> NOTE: A temporary password reset was performed on the `contact.cora.ai@gmail.com` prod user solely to validate the flow. **Do not record plaintext** here. After PR #73 merges and deploys, rotate credentials via normal process.

## Current state (verified)
- **Windows PowerShell (front door via Cloudflare/domain)**
  - `GET https://coraai.tech/api/status` → 200
  - `GET https://coraai.tech/health` → 200
  - Unauth `GET https://coraai.tech/api/user/settings` → 401
  - Auth flow:
    - `POST https://coraai.tech/api/auth/login` with JSON → 200 + `Set-Cookie: access_token`
    - `GET https://coraai.tech/api/user/settings` (with cookie) → 200 JSON
    - `PATCH https://coraai.tech/api/user/settings` with `{"timezone":"America/St_Johns","currency":"CAD"}` → 200; re-GET reflects values.

## Post-merge checks (runbook)
**Windows (PowerShell):**
```powershell
# Health
curl.exe -s -o NUL -w "status -> %{http_code}`n" https://coraai.tech/api/status
curl.exe -s -o NUL -w "health -> %{http_code}`n" https://coraai.tech/health

# Unauth gate
curl.exe -s -o NUL -w "settings (unauth) -> %{http_code}`n" https://coraai.tech/api/user/settings

# Auth (remember_me 30d)
$json = @{ email = "<your test user>"; password = "<secret>"; remember_me = $true } | ConvertTo-Json -Compress
curl.exe -s -c cookie.txt -X POST "https://coraai.tech/api/auth/login" -H "Content-Type: application/json" --data-binary $json -o NUL -w "login -> %{http_code}`n"
curl.exe -s -b cookie.txt -o NUL -w "settings (auth) -> %{http_code}`n" https://coraai.tech/api/user/settings
curl.exe -s -b cookie.txt -X PATCH "https://coraai.tech/api/user/settings" -H "Content-Type: application/json" --data-binary '{"timezone":"America/St_Johns","currency":"CAD"}' -o NUL -w "patch -> %{http_code}`n"
curl.exe -s -b cookie.txt https://coraai.tech/api/user/settings
Remove-Item cookie.txt -ErrorAction SilentlyContinue
```

**Server (SSH):**
```bash
systemctl status cora.service --no-pager -l
journalctl -u cora.service -n 120 --no-pager
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/api/status
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/health
```

## Open items / follow-ups
- Merge & deploy PR #73 (hotfix): hotfix/2025-09-06-prod-auth-and-errorhandler.
- Credential hygiene: rotate the temp-changed prod test user password; never store secrets in repo.
- Backups retention: keep last 1–2 tars in /var/backups/cora/system, automate pruning.
- Env hygiene: ensure backup key comes from env; logs should report “key loaded from env / not set,” never print raw key.
- Noise: Redis warnings (no impact); leave as is unless enabling Redis.

## Related PRs / refs
- #70 — Preference persistence (merged).
- #72 — Process/docs role-policy note (pending/merged per CI).
- #73 — Hotfix (this one): auth & errorhandler & currency migration & exporter alias.

## Acceptance criteria (for closure)
- PR #73 merged & deployed.
- Post-deploy smokes (bullets above) all green.
- Credentials rotated.
- Backup retention confirmed.
