# Backups Runbook

Policy
- Keep last 3 days for `system/` and `progress/` under `/var/backups/cora`.
- Keep 14 days for `ai-awareness` logs/archives (managed by ops job pruning `ai-logs-*.tgz`).

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
- `ai-awareness` retention is enforced by a separate ops task; not part of prune_backups.py.
