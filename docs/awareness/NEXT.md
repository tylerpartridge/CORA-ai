### Skim Summary
- Exec Mode: OFF (enable before merges/walkthroughs)
- Last checkpoint: 2025-09-11T11:22Z
- Top 3 Next: PR1 export fix -> PR2 date-range -> PR3 purge (then verify PR5/PR6)

## Next - Merge PR1->walkthrough; Merge PR2->date-range walkthrough; Merge PR3->purge dry-run; then verify PR5/PR6

### 1. PR1 Export Manager Merge -> Production Walkthrough
- [ ] **Merge PR1** -> run export walkthrough in production
- [ ] **Verify** JavaScript console errors resolved in production
- [ ] **Test** all export functionality post-merge (UTC timestamp required)

### 2. PR2 Date Range Merge -> Enhanced Export Testing  
- [ ] **Merge PR2** -> run date-range walkthrough
- [ ] **Test** start/end date parameters in production
- [ ] **Verify** timezone handling and filename generation

### 3. PR3 Account Purge Merge -> Non-Prod Dry Run
- [ ] **Merge PR3** -> run purge dry-run (non-prod only)
- [ ] **Test** 30-day deletion lifecycle
- [ ] **Verify** data cascade and audit logging

### 4. Wave 4 Business Profile Verification (Post-PR5/PR6)
- [ ] **Verify PR5** -> Onboarding progress save/resume functionality per walkthrough
- [ ] **Verify PR6** -> Job type selection + many-to-many relationships per walkthrough

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

- After PR7 merge: verify prune summary & ensure df -h stays <80%



