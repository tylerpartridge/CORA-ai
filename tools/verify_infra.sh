#!/usr/bin/env bash
set -euo pipefail

ROOT="/var/www/cora"
BACKUP_DIR="/var/backups/cora/docs"
BACKUP_MAX_HOURS=26
AWARENESS_LINK="docs/awareness"
AWARENESS_TARGET="docs/ai-awareness"
TIMER="cora-docs-backup.timer"
SCRIPT="/usr/local/bin/cora-docs-backup.sh"

pass() { echo "✅ $1"; }
fail() { echo "❌ $1"; exit 1; }

cd "$ROOT"

# 1) Root cleanliness (must not contain unknown files)
allowed="BOOTUP.md STATE.md MISSION.md OPERATIONS.md MEMORY.md README.md app.py Makefile requirements.txt Dockerfile"
for f in * .*; do
  [[ "$f" =~ ^(\.|\.\.|\.git|docs|tools|scripts|CORA|node_modules|static|assets|migrations|tests|frontend|backend)$ ]] && continue
  if ! grep -qw "$f" <<< "$allowed"; then
    fail "Unexpected file/dir in root: $f"
  fi
done
pass "Root cleanliness OK"

# 2) Backup timer active
systemctl is-active --quiet "$TIMER" && pass "Backup timer active" || fail "Backup timer inactive"

# 3) Backup script present
[[ -x "$SCRIPT" ]] && pass "Backup script present" || fail "Backup script missing or not executable"

# 4) Backup freshness
if find "$BACKUP_DIR" -type f -name "docs-*.tar.gz" -mmin -$((BACKUP_MAX_HOURS*60)) | grep -q .; then
  pass "Backup freshness OK (<${BACKUP_MAX_HOURS}h)"
else
  fail "No fresh backup (<${BACKUP_MAX_HOURS}h)"
fi

# 5) Awareness symlink
if [[ -L "$AWARENESS_LINK" ]] && [[ "$(readlink "$AWARENESS_LINK")" == "$AWARENESS_TARGET" ]]; then
  pass "Awareness link OK"
else
  fail "Awareness link broken"
fi

pass "ALL CHECKS PASSED"
