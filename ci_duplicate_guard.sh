#!/bin/bash
# CI Duplicate Guard: Check for awareness files outside docs/awareness/

set -e

echo "🔍 Checking awareness namespace compliance..."

# Define awareness state files that must only exist in docs/awareness/
AWARENESS_FILES=(
  "NOW.md"
  "NEXT.md"
  "STATUS.md" 
  "AI_WORK_LOG.md"
  "AI_DISCUSSION_SPACE.md"
  "REGISTRY.yml"
  "LOST_AND_FOUND.md"
)

violations=()
total_files=0

for file in "${AWARENESS_FILES[@]}"; do
  # Find any instance of the file outside docs/awareness/
  found=$(find . -maxdepth 3 -name "$file" -not -path "./docs/awareness/$file" -not -path "./.git/*" -not -path "./docs/ai-audits/*" 2>/dev/null || true)
  
  if [ -n "$found" ]; then
    while IFS= read -r path; do
      violations+=("$path")
      total_files=$((total_files + 1))
    done <<< "$found" 
  fi
done

if [ ${#violations[@]} -gt 0 ]; then
  echo "❌ CI CHECK FAILED: Awareness namespace violations detected"
  echo ""
  echo "Found $total_files awareness files outside docs/awareness/:"
  for violation in "${violations[@]}"; do
    echo "  - $violation"
  done
  echo ""
  echo "All awareness state files must be consolidated under: docs/awareness/"
  echo "Run the awareness namespace consolidation patch to fix this."
  echo ""
  exit 1
fi

echo "✅ Awareness namespace compliance: PASSED"
echo "📁 All awareness files properly located in docs/awareness/"