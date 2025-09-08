#!/usr/bin/env bash
set -euo pipefail
bad=$(git diff --cached --name-only | grep -E '^(routes/).*(\.bak|\.save|~|\.orig)$' || true)
if [ -n "$bad" ]; then
  echo "ERROR: Backup files staged (forbidden):"
  echo "$bad"
  exit 1
fi


