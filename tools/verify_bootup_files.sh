#!/bin/bash
# Verification script for bootup files canonicalization
# Ensures all required bootup files exist at their canonical locations

req=(
  "BOOTUP.md"
  "docs/awareness/MISSION.md"
  "docs/ai-awareness/MVP_REQUIREMENTS.md"
  "docs/awareness/NOW.md"
  "docs/awareness/NEXT.md"
  "docs/awareness/STATUS.md"
  "docs/awareness/AI_WORK_LOG.md"
  "docs/awareness/AI_DISCUSSION_SPACE.md"
  "GPT5_handoff.md"
)

echo "Checking bootup files..."
missing=0

for f in "${req[@]}"; do
  if [ -f "$f" ]; then
    echo "[OK] $f"
  else
    echo "[MISSING] $f"
    missing=$((missing + 1))
  fi
done

if [ $missing -eq 0 ]; then
  echo ""
  echo "OK: all bootup files present"
  exit 0
else
  echo ""
  echo "ERROR: $missing files missing"
  exit 1
fi