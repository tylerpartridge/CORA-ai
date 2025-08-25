#!/usr/bin/env bash
set -euo pipefail
repo="/var/www/cora"
snap="${repo}/docs/awareness/SNAPSHOT.md"
mkdir -p "$(dirname "$snap")"

{
  echo "# Awareness Snapshot"
  echo "_Generated: $(date -u -Is)_"
  echo
  if git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Branch: $(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null || echo n/a)"
    echo
    echo "Recent commits:"
    git -C "$repo" log --oneline -n 5 2>/dev/null | sed 's/^/- /' || true
    echo
  fi
  echo "Top-level files:"
  ls -1 "$repo" | head -n 50 | sed 's/^/- /'
} > "$snap"
echo "✅ snapshot written: $snap"
