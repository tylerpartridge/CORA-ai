- Queue: External uptime checks (Pingdom/UptimeRobot) after internal probe stable for 24h (added 2025-09-09T15:25Z)
## Next — Single Actions

- TLS renewal (due 2025-09-19)

Choose ONE path:

**Snap (preferred on Ubuntu):**
```bash
snap install certbot
ln -s /snap/bin/certbot /usr/bin/certbot
certbot renew --dry-run
# When ready:
# certbot renew
```

**APT:**
```bash
apt update && apt install -y certbot
certbot renew --dry-run
# When ready:
# certbot renew
```

Notes: use only one install method; dry-run first; production renew can be done closer to Sep 19.

- External uptime checks (Pingdom/UptimeRobot) after internal probe is stable for 24h.
 - After ~24h of internal probe stability, set UPTIME_API_KEY_ROBOT and trigger uptime-sync.yml (workflow_dispatch).
 - Keep UPTIME_INTERVAL=300 on free tier; switch to 60 on paid by setting repo/org variable UPTIME_INTERVAL=60 (no code changes).
 - Ensure monitoring-postcheck secrets (PROD_HOST/PROD_SSH_USER/PROD_SSH_KEY) are present so 18:00Z verification can run.
 - Optional: add SLACK_WEBHOOK_URL to uptime-sync and postcheck for failure alerts.
- After 24h internal probe stability, re-dispatch uptime-sync and monitoring-postcheck.
