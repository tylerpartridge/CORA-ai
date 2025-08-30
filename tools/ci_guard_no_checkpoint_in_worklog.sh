#!/bin/bash
set -e

# Guard to prevent checkpoint logging from writing to AI work log
# Check save scripts for problematic patterns
if grep -l "AI_WORK_LOG.md" tools/save.sh tools/save_fallback.sh tools/save_oneshot.sh 2>/dev/null | while read file; do
  grep -q "Saved checkpoint.*AI_WORK_LOG.md" "$file" && echo "$file"
done | grep -q .; then
  echo "ERROR: Checkpoint logging must not write to AI work log"
  exit 1
fi

echo "OK: checkpoint logging not targeting AI work log"