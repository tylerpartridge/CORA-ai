#!/usr/bin/env bash
# CORA Save Wrapper - Uses Python engine if available, falls back to oneshot
# This ensures saves always work, even if Python engines aren't deployed yet

set -euo pipefail
cd "$(dirname "$0")/.."

if [ -f tools/save_engine.py ]; then
  # Use the smart Python engine
  exec /usr/bin/python3 tools/save_engine.py --repo .
else
  # Portable oneshot fallback (repo-relative, not absolute paths)
  ts=$(date -u +%Y%m%d-%H%M%S)
  day=$(date -u +%Y/%m/%d)
  ck=/var/backups/cora/progress/$day/ckpt-$ts
  
  mkdir -p "$ck"
  
  # Capture git state
  git rev-parse --short HEAD > "$ck/commit.txt" 2>/dev/null || true
  git status -s > "$ck/status.txt" 2>/dev/null || true
  git diff > "$ck/patch.diff" 2>/dev/null || true
  
  # Create tarball of repo (excluding large/unnecessary files)
  tar -czf "$ck/repo.tgz" --warning=no-file-changed \
    --exclude='.git' --exclude='node_modules' --exclude='venv' \
    --exclude='__pycache__' --exclude='*.db' --exclude='*.db-*' \
    --exclude='logs/*.log*' -C . .
  
  # Log the save
  printf 'Saved checkpoint: %s at %s UTC\n' "$ck" "$(date -u -Is)" \
    | tee -a docs/ai-awareness/AI_WORK_LOG.md >/dev/null || \
    printf 'Saved checkpoint: %s at %s UTC\n' "$ck" "$(date -u -Is)" \
    | tee -a AI_WORK_LOG.md >/dev/null || true
  
  echo "Fallback save complete: $ck"
fi