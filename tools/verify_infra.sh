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

# --- 1) Root cleanliness ---
ALLOWED_FILES="BOOTUP.md STATE.md MISSION.md OPERATIONS.md MEMORY.md README.md app.py Makefile requirements.txt Dockerfile AI_WORK_LOG.md"
BANNED_DIRS_REGEX='^(backups|__pycache__)$'

unknown=()
while IFS= read -r item; do
  # ignore dotfiles like .env, .gitignore, etc.
  [[ "$item" == .* ]] && continue

  # allow directories by default (except banned)
  if [[ -d "$item" ]]; then
    [[ "$item" =~ $BANNED_DIRS_REGEX ]] && unknown+=("$item")
    continue
  fi

  # allow only known top-level files
  if grep -qw "$item" <<< "$ALLOWED_FILES"; then
    continue
  fi

  unknown+=("$item")
done < <(ls -1A)

if (( ${#unknown[@]} )); then
  printf "❌ Root cleanliness FAILED. Unknown items:\n"
  for u in "${unknown[@]}"; do printf "   - %s\n" "$u"; done
  exit 1
else
  pass "Root cleanliness OK"
fi

# --- 2) Backup timer active ---
systemctl is-active --quiet "$TIMER" && pass "Backup timer active ($TIMER)" || fail "Backup timer inactive ($TIMER)"

# --- 3) Backup script present ---
[[ -x "$SCRIPT" ]] && pass "Backup script present ($SCRIPT)" || fail "Backup script missing or not executable ($SCRIPT)"

# --- 4) Backup freshness (< BACKUP_MAX_HOURS old) ---
if find "$BACKUP_DIR" -type f -name "docs-*.tar.gz" -mmin -$((BACKUP_MAX_HOURS*60)) | grep -q .; then
  pass "Backup freshness OK (<${BACKUP_MAX_HOURS}h)"
else
  fail "No fresh backup (<${BACKUP_MAX_HOURS}h) in $BACKUP_DIR"
fi

# --- 5) Awareness symlink correct ---
if [[ -L "$AWARENESS_LINK" ]] && [[ "$(readlink "$AWARENESS_LINK")" == "$AWARENESS_TARGET" ]]; then
  pass "Awareness link OK ($AWARENESS_LINK -> $AWARENESS_TARGET)"
else
  fail "Awareness link BROKEN (expected $AWARENESS_LINK -> $AWARENESS_TARGET)"
fi

pass "ALL CHECKS PASSED"
