#!/usr/bin/env bash
set -euo pipefail
echo "🔍 Checking awareness namespace compliance..."

# Awareness state files must live ONLY under docs/awareness/
files=("NOW.md" "NEXT.md" "STATUS.md" "AI_WORK_LOG.md" "AI_DISCUSSION_SPACE.md" "REGISTRY.yml" "LOST_AND_FOUND.md")
violations=()

# Use git index to list tracked files, then filter by name
while IFS= read -r path; do
  for f in "${files[@]}"; do
    if [[ "$path" =~ (^|/)${f}$ ]]; then
      if [[ "$path" != docs/awareness/* ]]; then
        violations+=("$path")
      fi
    fi
  done
done < <(git ls-files)

if [ "${#violations[@]}" -gt 0 ]; then
  echo "❌ Awareness namespace violation(s) detected:"
  printf '  %s\n' "${violations[@]}"
  exit 1
fi

echo "✅ Awareness namespace compliance: PASSED"