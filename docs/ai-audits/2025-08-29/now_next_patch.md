# 📋 AWARENESS NAMESPACE CONSOLIDATION PATCH PLAN

**Date:** 2025-08-29  
**Goal:** Consolidate all awareness state files under `docs/awareness/` as single source of truth  
**Status:** Ready for execution

## 🎯 SUMMARY

All awareness state files will be moved to `docs/awareness/` namespace. Root pointer files will be removed. Writer references will be updated to new paths.

## 📁 FILE MOVES

### 1. Move Canonical Files to Target Namespace

```bash
# Create target directory
mkdir -p docs/awareness

# Move canonical files from docs/ai-awareness/ to docs/awareness/
git mv docs/ai-awareness/NOW.md docs/awareness/NOW.md
git mv docs/ai-awareness/NEXT.md docs/awareness/NEXT.md  
git mv docs/ai-awareness/STATUS.md docs/awareness/STATUS.md
git mv docs/ai-awareness/AI_WORK_LOG.md docs/awareness/AI_WORK_LOG.md
git mv docs/ai-awareness/AI_DISCUSSION_SPACE.md docs/awareness/AI_DISCUSSION_SPACE.md
git mv docs/ai-awareness/REGISTRY.yml docs/awareness/REGISTRY.yml
git mv docs/ai-awareness/LOST_AND_FOUND.md docs/awareness/LOST_AND_FOUND.md
```

### 2. Remove Duplicate/Pointer Files

```bash
# Remove root-level pointer files
git rm NOW.md
git rm NEXT.md
git rm STATUS.md

# Remove outdated root AI_WORK_LOG.md (rotated archive)
git rm AI_WORK_LOG.md
```

## ✏️ FILE EDITS

### 1. Update Writer Reference in AI_WORK_LOG.md

**File:** `AI_WORK_LOG.md` (will be deleted, but preserving for reference)  
**Line:** 143

```diff
- | tee -a docs/ai-awareness/AI_WORK_LOG.md >/dev/null
+ | tee -a docs/awareness/AI_WORK_LOG.md >/dev/null
```

### 2. Update Writer References in Tools Scripts

**File:** `tools/save_oneshot.sh`  
**Line:** 3

```diff
-printf "Saved checkpoint: %s at %s UTC\n" "$ck" "$(date -u -Is)" | tee -a /var/www/cora/docs/ai-awareness/AI_WORK_LOG.md >/dev/null
+printf "Saved checkpoint: %s at %s UTC\n" "$ck" "$(date -u -Is)" | tee -a /var/www/cora/docs/awareness/AI_WORK_LOG.md >/dev/null
```

**File:** `tools/save_fallback.sh`  
**Line:** 36

```diff
-  | tee -a "${repo}/docs/ai-awareness/AI_WORK_LOG.md" >/dev/null
+  | tee -a "${repo}/docs/awareness/AI_WORK_LOG.md" >/dev/null
```

**File:** `tools/save.sh`  
**Lines:** 21-22

```diff
-if [ -n "${last_bundle:-}" ] && ! grep -Fq "$last_bundle" docs/ai-awareness/AI_WORK_LOG.md 2>/dev/null; then
-  echo "Saved checkpoint: $last_bundle at $(date -u -Is) UTC" >> docs/ai-awareness/AI_WORK_LOG.md
+if [ -n "${last_bundle:-}" ] && ! grep -Fq "$last_bundle" docs/awareness/AI_WORK_LOG.md 2>/dev/null; then
+  echo "Saved checkpoint: $last_bundle at $(date -u -Is) UTC" >> docs/awareness/AI_WORK_LOG.md
```

## 📝 BOOTUP.md PATH CORRECTIONS

**File:** `BOOTUP.md`

### Update Optional Block References

```diff
 <bootup-config>

-- /docs/ai-awareness/SPARKS.md  # present
-- /docs/ai-awareness/DECISIONS.md  # optional
-- /docs/ai-awareness/THRESHOLDS.md  # optional
-- /docs/ai-awareness/METRICS_SNAPSHOT.md  # optional
-- /docs/ai-awareness/AIM.md  # optional
+- /docs/ai-awareness/SPARKS.md  # present - Optional Meta
+- /docs/ai-awareness/DECISIONS.md  # optional - Optional Meta  
+- /docs/ai-awareness/THRESHOLDS.md  # optional - Optional Meta
+- /docs/ai-awareness/METRICS_SNAPSHOT.md  # optional - Optional Meta
+- /docs/ai-awareness/AIM.md  # optional - Optional Meta
```

### Update State File References

```diff
 ### 1. Read Active State Files
-- **MVP_REQUIREMENTS.md** - 🗿 THE ONLY THING THAT MATTERS (65 items to launch)
-- **NOW.md** - Current work in progress
-- **STATUS.md** - System health status
-- **NEXT.md** - Task queue and priorities
-- **HANDOVER_ACTIVE.md** - Claude ↔ Cursor collaboration status
+- **docs/ai-awareness/MVP_REQUIREMENTS.md** - 🗿 THE ONLY THING THAT MATTERS (65 items to launch) 
+- **docs/awareness/NOW.md** - Current work in progress
+- **docs/awareness/STATUS.md** - System health status
+- **docs/awareness/NEXT.md** - Task queue and priorities
+- **docs/HANDOVER_ACTIVE.md** - Claude ↔ Cursor collaboration status
```

### Update Quick Start Instructions

```diff
 3. Read state files: NOW.md, STATUS.md, NEXT.md, docs/HANDOVER_ACTIVE.md
+3. Read state files: docs/awareness/NOW.md, docs/awareness/STATUS.md, docs/awareness/NEXT.md, docs/HANDOVER_ACTIVE.md
```

## 🛡️ ENFORCEMENT ARTIFACTS

### 1. Pre-commit Hook

**File:** `.githooks/pre-commit`

```bash
#!/bin/bash
# Pre-commit hook: Prevent awareness state files outside docs/awareness/

set -e

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

# Check for awareness files outside docs/awareness/
violations=()

for file in "${AWARENESS_FILES[@]}"; do
  # Find any instance of the file outside docs/awareness/
  found=$(find . -name "$file" -not -path "./docs/awareness/$file" -not -path "./.git/*" 2>/dev/null || true)
  
  if [ -n "$found" ]; then
    while IFS= read -r path; do
      violations+=("$path")
    done <<< "$found"
  fi
done

if [ ${#violations[@]} -gt 0 ]; then
  echo "❌ COMMIT BLOCKED: Awareness state files found outside docs/awareness/"
  echo ""
  echo "The following files violate the awareness namespace policy:"
  for violation in "${violations[@]}"; do
    echo "  - $violation"
  done
  echo ""
  echo "Awareness state files must only exist in: docs/awareness/"
  echo ""
  echo "To fix this:"
  echo "  1. Move files to docs/awareness/ using: git mv <file> docs/awareness/<file>"  
  echo "  2. Or remove duplicates using: git rm <file>"
  echo ""
  exit 1
fi

echo "✅ Awareness namespace policy: PASSED"
```

### 2. CI Duplicate Guard Script

**File:** `ci_duplicate_guard.sh`

```bash
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
  found=$(find . -name "$file" -not -path "./docs/awareness/$file" -not -path "./.git/*" 2>/dev/null || true)
  
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
```

## 🚀 EXECUTION ORDER

1. **Create enforcement artifacts**
   ```bash
   # Create pre-commit hook
   mkdir -p .githooks
   # Copy pre-commit content above to .githooks/pre-commit
   chmod +x .githooks/pre-commit
   
   # Create CI guard script  
   # Copy ci_duplicate_guard.sh content above
   chmod +x ci_duplicate_guard.sh
   ```

2. **Execute file moves**
   ```bash
   # Run the git mv commands from File Moves section
   mkdir -p docs/awareness
   git mv docs/ai-awareness/NOW.md docs/awareness/NOW.md
   # ... (all other moves)
   ```

3. **Remove duplicates**
   ```bash 
   # Run the git rm commands for pointer files
   git rm NOW.md NEXT.md STATUS.md AI_WORK_LOG.md
   ```

4. **Update writer references**
   ```bash
   # Apply the diffs to tools/*.sh files
   # Update BOOTUP.md with path corrections
   ```

5. **Test enforcement**
   ```bash
   # Run the duplicate guard to verify compliance
   ./ci_duplicate_guard.sh
   ```

## ✅ ACCEPTANCE CRITERIA

- [ ] All awareness state files exist only in `docs/awareness/`
- [ ] No duplicate awareness files in root or other locations
- [ ] All writer references updated to new paths
- [ ] BOOTUP.md references correct paths
- [ ] Pre-commit hook prevents future violations
- [ ] CI guard script passes compliance check
- [ ] All files maintain their content integrity

## 📊 IMPACT ASSESSMENT

- **Files moved:** 7 awareness state files
- **Files removed:** 4 root pointer/duplicate files  
- **Scripts updated:** 4 tools scripts with writer references
- **Documentation updated:** BOOTUP.md path corrections
- **Enforcement added:** Pre-commit hook + CI guard script

**Result:** Clean, single source of truth for awareness state under `docs/awareness/` with automated enforcement.