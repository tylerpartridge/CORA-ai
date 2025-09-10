#!/usr/bin/env bash
# LOCATION: tools/ops/install_backup_cron.sh
# PURPOSE: Install once-daily backup (03:20 UTC) + prune to keep 3 days
set -euo pipefail
CRON=/etc/cron.d/cora-backups
cat > "$CRON" <<'EOF'
# cora backups — once daily at 03:20 UTC
# Requires BACKUP_CMD to exist and return 0
# After backup, prune to keep 3 days
MAILTO=""
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
20 3 * * * root /var/www/cora/tools/backup.sh && /usr/bin/env CORA_BACKUP_KEEP_DAYS=3 python3 /var/www/cora/tools/prune_backups.py
EOF
chmod 0644 "$CRON"
echo "Installed $CRON"
# end
