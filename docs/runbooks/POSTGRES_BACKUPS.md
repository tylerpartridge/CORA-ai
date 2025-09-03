# Postgres Backups & Restore Verification

## Overview
- Nightly pg_dump (custom format) with N-day retention (default 7)
- Location: `/var/backups/cora/pg` (0700, postgres:postgres; dumps 600)
- Logs: `/var/log/cora_pg_backup.log` (backup), `/var/log/cora_pg_restore_verify.jsonl` (restore drill)
- DSN source: `/root/CORA_PROD_PG_DSN.env` (DATABASE_URL/PG_DSN)

## Systemd
- Service: `cora-pg-backup.service`
- Timer: `cora-pg-backup.timer` (OnCalendar=03:10 UTC, Persistent=true)

Enable & start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now cora-pg-backup.timer
sudo systemctl status cora-pg-backup.timer --no-pager
```

## Manual Backup
```bash
sudo -i
cd /var/www/cora
source /root/CORA_PROD_PG_DSN.env
CORA_PG_BACKUP_DIR=/var/backups/cora/pg tools/pg_backup.sh
ls -lah /var/backups/cora/pg | tail -n 5
```

## Restore Verification (Drill)
Creates a temp DB, restores latest dump, runs smoke queries, and drops the DB.
```bash
sudo -i
cd /var/www/cora
./tools/pg_restore_verify.sh
tail -n 3 /var/log/cora_pg_restore_verify.jsonl
```

JSONL example:
```json
{"ts":"2025-09-03T19:25:01Z","event":"restore_verify_start","dump":"/var/backups/cora/pg/cora_pg_20250903_192500.dump","verify_db":"cora_restore_verify_20250903_192501"}
{"ts":"2025-09-03T19:25:12Z","event":"restore_verify_result","users_count":1,"ok_users":1}
{"ts":"2025-09-03T19:25:14Z","status":"complete","dump":"/var/backups/cora/pg/cora_pg_20250903_192500.dump"}
```

## Failure Signals
- Backup log shows non-zero exit or missing new `cora_pg_*.dump`
- Restore JSONL contains `ok_users: 0` or missing entries
- Timer status shows failed `cora-pg-backup.service`

## Disaster Recovery (Single DB)
1) Identify latest good dump: `/var/backups/cora/pg/cora_pg_*.dump`
2) Stop app: `systemctl stop cora.service`
3) Restore into empty DB:
```bash
sudo -u postgres dropdb cora_prod || true
sudo -u postgres createdb -O cora_app cora_prod
pg_restore --no-owner --no-privileges --clean --if-exists --dbname "postgresql://postgres@localhost:5432/cora_prod" /var/backups/cora/pg/cora_pg_YYYYmmdd_HHMMSS.dump
```
4) Start app: `systemctl start cora.service`
5) Probe: `curl -s -o /dev/null -w "GET /api/status => %{http_code}\n" http://127.0.0.1:8000/api/status`

## Notes
- WAL archiving hook can be added later if PITR is required.
- Consider S3 offsite replication as a follow-up.


