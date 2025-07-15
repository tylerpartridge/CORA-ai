# CORA Security Hardening Guide

## 1. Enable 2FA on DigitalOcean
- Log in to your DigitalOcean account.
- Go to **Account > Security**.
- Under **Two-Factor Authentication**, click **Enable**.
- Choose an authenticator app (e.g., Google Authenticator, Authy) and scan the QR code.
- Enter the generated code to confirm.
- Save backup codes in a secure location.
- **Result:** 2FA is now required for all logins to your DigitalOcean account.

## 2. Automated Database Backups
- Use `tools/backup_db.py` to back up your database (SQLite or PostgreSQL).
- Backups are stored in `/data/archive/` with timestamped filenames.
- Schedule with cron (Linux) or Task Scheduler (Windows) for daily backups.
- See `tools/backup_db_README.md` for details.

## 3. API Rate Limiting
- Rate limiting is enabled via SlowAPI middleware.
- Default: 100 requests/minute per IP (configurable via `RATE_LIMIT_REQUESTS_PER_MINUTE` env var).
- Exceeding the limit returns HTTP 429 with rate limit headers.

## 4. CORS (Cross-Origin Resource Sharing)
- Only requests from `https://coraai.tech`, `https://www.coraai.tech`, and localhost are allowed.
- All other origins are blocked by default.

## 5. Security Headers
- The following headers are set on all responses:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Content-Security-Policy` (restricts scripts, styles, images, etc.)
  - `Permissions-Policy` (restricts browser features)

## 6. Logging & Error Handling
- All requests and responses are logged to `logs/cora_requests.log`.
- Errors are handled globally and logged for review.

## 7. Next Steps
- Review this checklist before each deployment.
- Store all secrets and backup codes securely (use a password manager).
- Regularly test backup and restore procedures.
- Monitor logs and rate limit alerts for abuse. 