# CORA Deploy Runbook

**Purpose:** One-liner deploy to production with basic smoke checks.  
**Windows host assumed** (PowerShell + OpenSSH). Linux/Mac users can adapt easily.

---

## Prereqs
- SSH access to `root@159.203.183.48` 
- Repo cloned locally with a clean `main` (no uncommitted changes)
- Batch deploy windows: **12:30** and **17:30 UTC** (ad-hoc only if RED)

---

## Standard Deploy

```powershell
# From repo root on your machine
. .\scripts\Invoke-CoraDeploy.ps1
Invoke-CoraDeploy

# Or explicitly:
& .\scripts\Invoke-CoraDeploy.ps1 -Server 159.203.183.48
```

**What it does:**
1. SSH to server → `git pull --prune` in `/var/www/cora`
2. `systemctl restart cora.service` and show status
3. Smokes: GET `https://coraai.tech/health` and `https://coraai.tech/api/status`

**Success criteria:**
- `/health` returns JSON (HTTP 200)
- `/api/status` returns HTTP 200
- No systemd service failures

**Expected runtime:** 30-60 seconds

---

## Manual Deploy (Fallback)

If the PowerShell script isn't available:

```bash
# SSH to production server
ssh root@159.203.183.48

# Navigate to app directory
cd /var/www/cora

# Pull latest changes
git pull --prune origin main

# Restart the service
systemctl restart cora.service

# Check service status
systemctl status cora.service

# Verify health endpoints
curl -f https://coraai.tech/health
curl -f https://coraai.tech/api/status
```

---

## Smoke Tests (Detail)

The deploy script automatically runs these checks:

### 1. Health Check
```bash
curl -f https://coraai.tech/health
```
**Expected:** JSON response like `{"status":"healthy","timestamp":"..."}`

### 2. API Status Check
```bash
curl -f https://coraai.tech/api/status
```
**Expected:** HTTP 200 with application status info

### 3. Service Status
```bash
systemctl is-active cora.service
```
**Expected:** `active`

---

## Troubleshooting

### Deploy Script Fails

**Symptom:** PowerShell script errors or timeouts
```powershell
# Check SSH connectivity first
ssh root@159.203.183.48 "echo 'SSH working'"

# Run deploy with verbose output
& .\scripts\Invoke-CoraDeploy.ps1 -Verbose
```

### Service Won't Start

**Symptom:** `systemctl restart cora.service` fails
```bash
# Check service logs
journalctl -u cora.service --since "5 minutes ago" -f

# Check for Python/dependency issues
cd /var/www/cora
python3 -c "import app; print('Import OK')"

# Check port conflicts
lsof -i :8000
```

**Common fixes:**
- Missing dependencies: `pip3 install -r requirements.txt`
- Port in use: Kill conflicting process or change port
- Permission issues: `chown -R www-data:www-data /var/www/cora`

### Health Endpoints Return 5xx

**Symptom:** `/health` or `/api/status` return server errors
```bash
# Check nginx logs
tail -f /var/log/nginx/error.log

# Check application logs
journalctl -u cora.service -f

# Verify nginx → app proxy
curl http://localhost:8000/health  # Direct to app
curl https://coraai.tech/health    # Through nginx
```

**Common fixes:**
- Nginx config issues: Check `/etc/nginx/sites-available/coraai.tech`
- App not listening: Verify uvicorn binds to `0.0.0.0:8000`
- Database connection: Check SQLite file permissions

### SSL/Certificate Issues

**Symptom:** HTTPS endpoints fail, HTTP works
```bash
# Check SSL certificate
openssl s_client -connect coraai.tech:443 -servername coraai.tech

# Check nginx SSL config
nginx -t
```

**Common fixes:**
- Certificate expired: Renew SSL certificate
- Nginx SSL config: Verify cert/key paths in nginx config

### Database Issues

**Symptom:** App starts but API calls fail with DB errors
```bash
# Check SQLite database
cd /var/www/cora
ls -la cora.db
sqlite3 cora.db ".tables"

# Check file permissions
chmod 664 cora.db
chown www-data:www-data cora.db
```

---

## Emergency Procedures

### Immediate Rollback

If the deploy causes critical issues:
```bash
# SSH to server
ssh root@159.203.183.48
cd /var/www/cora

# Rollback to previous commit
git log --oneline -5  # Find last working commit
git reset --hard <commit-hash>

# Restart service
systemctl restart cora.service
```

### Take Site Offline (Maintenance Mode)

```bash
# Create maintenance page
echo '<h1>Under Maintenance</h1><p>Back soon!</p>' > /var/www/html/maintenance.html

# Redirect all traffic to maintenance page
# Edit /etc/nginx/sites-available/coraai.tech
# Replace location / block with:
# location / { return 503; }
# error_page 503 @maintenance;
# location @maintenance { root /var/www/html; rewrite ^(.*)$ /maintenance.html break; }

nginx -s reload
```

---

## Health Monitoring

### Key Metrics to Watch
- **Response time**: `/health` should respond < 500ms
- **Error rate**: Monitor 5xx responses in nginx logs
- **Memory usage**: `free -h` (Python app should use < 512MB)
- **Disk space**: `df -h` (ensure adequate space for logs)

### Log Locations
- **Application**: `journalctl -u cora.service`
- **Nginx access**: `/var/log/nginx/access.log`
- **Nginx errors**: `/var/log/nginx/error.log`
- **System**: `/var/log/syslog`

### Monitoring Commands
```bash
# Watch service status
watch systemctl status cora.service

# Monitor logs in real-time
journalctl -u cora.service -f

# Check recent HTTP status codes
tail -f /var/log/nginx/access.log | grep -E '[45][0-9]{2}'
```

---

## Post-Deploy Checklist

After successful deployment:
- [ ] Health endpoints respond correctly
- [ ] Key user flows work (login, expense entry)
- [ ] No increase in error rates
- [ ] Performance within normal ranges
- [ ] Update deployment tracking (if applicable)

---

## Contact Information

**Escalation:** If deploy fails and you can't resolve within 30 minutes, escalate to system administrator.

**Production Server:**
- IP: `159.203.183.48`
- Domain: `coraai.tech`
- OS: Ubuntu 24.10
- Service: `cora.service` (systemd)
- App path: `/var/www/cora`

---

*Last updated: 2025-09-01*  
*Next review: 2025-10-01*