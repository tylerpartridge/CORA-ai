# Backups Runbook

Policy
- Keep last 3 days for `system/` and `progress/` under `/var/backups/cora`.

Commands
- Dry-run:
  - `python3 tools/prune_backups.py --dry-run`
- Live:
  - `python3 tools/prune_backups.py`
- Per subdir:
  - `python3 tools/prune_backups.py --only system`
  - `python3 tools/prune_backups.py --only progress`
- Change retention:
  - `CORA_BACKUP_KEEP_DAYS=5 python3 tools/prune_backups.py`

Notes
- Script is idempotent and refuses to delete outside `/var/backups/cora`.
- Output is JSON-formatted summary with kept/removed days per target.
