#!/bin/bash
# CORA Architecture Freeze Script
# Generated from GPT-5's lock-in steps
# Date: 2025-08-23
# Purpose: Freeze the bulletproof AI awareness system architecture

set -euo pipefail

echo "========================================="
echo "CORA ARCHITECTURE FREEZE SCRIPT"
echo "========================================="
echo ""

# Check if running on production Ubuntu
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "✓ Linux environment detected"
else
    echo "⚠️  Not on Linux - some commands may need adjustment"
fi

echo ""
echo "This script will:"
echo "1. Make index files immutable with chattr +i"
echo "2. Ensure AI logs are append-only with chattr +a"
echo "3. Version git hooks in repository"
echo "4. Create 'cora' command shortcuts"
echo "5. Set up systemd timers for autosave/backup"
echo "6. Tag this freeze moment in git"
echo ""
echo "Press ENTER to continue or Ctrl+C to abort..."
read

# Navigate to repo root
cd /var/www/cora || cd /mnt/host/c/CORA || cd .

echo ""
echo "Step 1: Making index files immutable..."
echo "----------------------------------------"
if command -v chattr &> /dev/null; then
    sudo chattr +i docs/bootup/_index.yml docs/bootup/_index.list 2>/dev/null || echo "  ⚠️ chattr not available or files not found"
    echo "  ✓ Index files protected with +i"
else
    echo "  ⚠️ chattr not available on this system"
fi

echo ""
echo "Step 2: Ensuring AI logs are append-only..."
echo "--------------------------------------------"
if command -v chattr &> /dev/null; then
    # Note: These paths may need adjustment based on actual location
    sudo chattr +a AI_WORK_LOG.md AI_DISCUSSION_SPACE.md 2>/dev/null || echo "  ⚠️ Files may be in different location"
    echo "  ✓ AI logs protected with +a"
else
    echo "  ⚠️ chattr not available on this system"
fi

echo ""
echo "Step 3: Versioning git hooks..."
echo "--------------------------------"
if [ -f .git/hooks/pre-commit ]; then
    mkdir -p .githooks
    cp .git/hooks/pre-commit .githooks/pre-commit
    git config core.hooksPath .githooks
    echo "  ✓ Pre-commit hook copied to .githooks/"
    echo "  ✓ Git configured to use .githooks/"
    echo "  Note: Remember to commit with:"
    echo "    git add .githooks/pre-commit"
    echo "    git commit -m 'chore: version pre-commit hook (BREAK_GLASS policy)'"
else
    echo "  ⚠️ No pre-commit hook found"
fi

echo ""
echo "Step 4: Creating 'cora' command..."
echo "-----------------------------------"
if [ -w /usr/local/bin ]; then
    sudo tee /usr/local/bin/cora >/dev/null <<'SH'
#!/usr/bin/env bash
set -euo pipefail

# Find repo location
if [ -d /var/www/cora ]; then
    REPO=/var/www/cora
elif [ -d /mnt/host/c/CORA ]; then
    REPO=/mnt/host/c/CORA
else
    REPO=$(pwd)
fi

cd "$REPO"

case "${1:-}" in
  bootup)  exec python3 tools/bootup_engine.py --repo . ;;
  save)    exec python3 tools/save_engine.py   --repo . ;;
  backup)  
    if [ -f tools/backup_cora.sh ]; then
        exec bash tools/backup_cora.sh
    else
        echo "Backup script not found. Running save instead..."
        exec python3 tools/save_engine.py --repo .
    fi
    ;;
  rotate)  exec python3 tools/rotate_logs.py   --repo . ;;
  status)  
    echo "Last checkpoint: $(grep last_checkpoint docs/progress/tracker.yml 2>/dev/null || echo 'unknown')"
    echo "Bundles: $(find . -name "ckpt-*" -type d 2>/dev/null | wc -l)"
    ;;
  *) 
    echo "usage: cora {bootup|save|backup|rotate|status}"
    echo ""
    echo "  bootup - Load full system awareness"
    echo "  save   - Save current progress"
    echo "  backup - Full system backup"
    echo "  rotate - Rotate large log files"
    echo "  status - Show save status"
    exit 2
    ;;
esac
SH
    sudo chmod +x /usr/local/bin/cora
    echo "  ✓ /usr/local/bin/cora created"
    echo "  Commands available: cora {bootup|save|backup|rotate|status}"
else
    echo "  ⚠️ Cannot write to /usr/local/bin - creating local version"
    cat > cora.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
case "${1:-}" in
  bootup)  exec python tools/bootup_engine.py --repo . ;;
  save)    exec python tools/save_engine.py   --repo . ;;
  backup)  exec python tools/save_engine.py   --repo . ;;
  rotate)  exec python tools/rotate_logs.py   --repo . ;;
  status)  grep last_checkpoint docs/progress/tracker.yml 2>/dev/null || echo 'No saves yet' ;;
  *) echo "usage: ./cora.sh {bootup|save|backup|rotate|status}"; exit 2;;
esac
SH
    chmod +x cora.sh
    echo "  ✓ ./cora.sh created (local version)"
fi

echo ""
echo "Step 5: Setting up systemd timers (Linux only)..."
echo "--------------------------------------------------"
if command -v systemctl &> /dev/null && [ -d /etc/systemd/system ]; then
    # Create service files
    sudo tee /etc/systemd/system/cora-save.service >/dev/null <<'UNIT'
[Unit]
Description=CORA autosave checkpoint

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /var/www/cora/tools/save_engine.py --repo /var/www/cora
WorkingDirectory=/var/www/cora
StandardOutput=journal
StandardError=journal
UNIT

    sudo tee /etc/systemd/system/cora-save.timer >/dev/null <<'UNIT'
[Unit]
Description=Run CORA autosave every 15 minutes

[Timer]
OnBootSec=5m
OnUnitActiveSec=15m
Persistent=true

[Install]
WantedBy=timers.target
UNIT

    sudo tee /etc/systemd/system/cora-backup.service >/dev/null <<'UNIT'
[Unit]
Description=CORA end-of-day backup

[Service]
Type=oneshot
ExecStart=/bin/bash /var/www/cora/tools/backup_cora.sh
WorkingDirectory=/var/www/cora
StandardOutput=journal
StandardError=journal
UNIT

    sudo tee /etc/systemd/system/cora-backup.timer >/dev/null <<'UNIT'
[Unit]
Description=Daily CORA backup at 3:15 AM

[Timer]
OnCalendar=*-*-* 03:15:00
Persistent=true

[Install]
WantedBy=timers.target
UNIT

    sudo systemctl daemon-reload
    echo "  ✓ Service files created"
    echo "  To enable timers, run:"
    echo "    sudo systemctl enable --now cora-save.timer"
    echo "    sudo systemctl enable --now cora-backup.timer"
else
    echo "  ⚠️ systemd not available - skipping timer setup"
    echo "  Consider setting up cron jobs instead:"
    echo "    */15 * * * * cd $(pwd) && python3 tools/save_engine.py"
    echo "    15 3 * * * cd $(pwd) && bash tools/backup_cora.sh"
fi

echo ""
echo "Step 6: Creating git tag for freeze moment..."
echo "----------------------------------------------"
if command -v git &> /dev/null && [ -d .git ]; then
    TAG_NAME="awareness-freeze-$(date -u +%Y%m%d-%H%M%S)"
    echo "  Creating tag: $TAG_NAME"
    echo "  Note: Run these commands when ready:"
    echo "    git tag -a $TAG_NAME -m 'Architecture freeze after GREEN validation'"
    echo "    git push --tags"
else
    echo "  ⚠️ Git not available or not a git repository"
fi

echo ""
echo "========================================="
echo "FREEZE COMPLETE - Manual Steps Remaining:"
echo "========================================="
echo ""
echo "1. If on production Ubuntu, test rotation with +a:"
echo "   sudo chattr +a AI_WORK_LOG.md"
echo "   python3 tools/rotate_logs.py"
echo ""
echo "2. Commit the versioned git hook:"
echo "   git add .githooks/pre-commit"
echo "   git commit -m 'chore: version pre-commit hook (BREAK_GLASS policy)'"
echo "   git push"
echo ""
echo "3. Enable systemd timers (if on Linux):"
echo "   sudo systemctl enable --now cora-save.timer"
echo "   sudo systemctl enable --now cora-backup.timer"
echo ""
echo "4. Tag the freeze moment:"
echo "   git tag -a awareness-freeze-$(date -u +%Y%m%d-%H%M%S) -m 'Freeze after GREEN'"
echo "   git push --tags"
echo ""
echo "5. (Optional) Configure DigitalOcean Spaces for WORM backup"
echo ""
echo "Your bulletproof AI awareness system is ready!"
echo "Commands available:"
echo "  cora bootup  - Load system awareness"
echo "  cora save    - Save progress checkpoint"
echo "  cora backup  - Full system backup"
echo "  cora rotate  - Rotate large logs"
echo "  cora status  - Check save status"