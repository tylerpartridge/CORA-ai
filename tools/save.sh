#!/usr/bin/env bash
set -euo pipefail
cd /var/www/cora

# Run engine (do NOT use exec so footer can run)
if ! /usr/bin/env python3 tools/save_engine.py --repo /var/www/cora; then
  echo "WARN: save_engine.py failed; creating bare snapshot anyway" >&2
fi

## repo.tgz snapshot (full repo without heavy dirs)
last_bundle="$(ls -1d /var/backups/cora/progress/*/*/*/ckpt-* 2>/dev/null | tail -n 1 || true)"
if [ -n "${last_bundle:-}" ] && [ ! -f "$last_bundle/repo.tgz" ]; then
  tar -czf "$last_bundle/repo.tgz" \
    --warning=no-file-changed \
    --exclude='.git' --exclude='node_modules' --exclude='venv' \
    --exclude='__pycache__' --exclude='*.db' --exclude='*.db-*' \
    --exclude='logs/*.log*' -C /var/www/cora .
fi

# Awareness log line (guard against dupes)
if [ -n "${last_bundle:-}" ] && ! grep -Fq "$last_bundle" docs/awareness/CHECKPOINT_LOG.md 2>/dev/null; then
  mkdir -p docs/awareness
  echo "Saved checkpoint: $last_bundle at $(date -u -Is) UTC" >> docs/awareness/CHECKPOINT_LOG.md
fi
