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
