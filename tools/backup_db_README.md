# CORA Database Backup Script

## Usage

This script backs up the CORA database (SQLite or PostgreSQL) to the `/data/archive/` directory with a timestamped filename.

### Run Manually
```bash
python tools/backup_db.py
```

### Scheduling
- **Linux (cron):**
  - Add to crontab for daily backup at 2am:
    ```
    0 2 * * * /usr/bin/python3 /path/to/CORA/tools/backup_db.py
    ```
- **Windows (Task Scheduler):**
  - Create a task to run `python tools/backup_db.py` daily.

### Details
- **SQLite:** Copies the DB file to `/data/archive/`.
- **PostgreSQL:** Uses `pg_dump` (must be installed and in PATH).
- **Backups:** Named with timestamp, e.g. `cora_sqlite_backup_20250715_020000.db`.
- **Errors:** Script prints errors if backup fails or DB is not found.

## Restore
- To restore, copy the backup file to the original DB location (SQLite) or use `pg_restore` (Postgres). 