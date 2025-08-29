# 📋 PR: Awareness Namespace Consolidation

## 🎯 Summary
Consolidates all awareness state files under `docs/awareness/` as the single source of truth, removing duplicates and updating all writer references.

## 📊 Changes Made

### File Moves (7 files)
- ✅ `docs/ai-awareness/NOW.md` → `docs/awareness/NOW.md`
- ✅ `docs/ai-awareness/NEXT.md` → `docs/awareness/NEXT.md`
- ✅ `docs/ai-awareness/STATUS.md` → `docs/awareness/STATUS.md`
- ✅ `docs/ai-awareness/AI_WORK_LOG.md` → `docs/awareness/AI_WORK_LOG.md`
- ✅ `docs/ai-awareness/AI_DISCUSSION_SPACE.md` → `docs/awareness/AI_DISCUSSION_SPACE.md`
- ✅ `docs/ai-awareness/REGISTRY.yml` → `docs/awareness/REGISTRY.yml`
- ✅ `docs/ai-awareness/LOST_AND_FOUND.md` → `docs/awareness/LOST_AND_FOUND.md`

### Files Removed (4 root duplicates)
- ✅ Removed `NOW.md` (pointer file)
- ✅ Removed `NEXT.md` (pointer file)
- ✅ Removed `STATUS.md` (pointer file)
- ✅ Removed `AI_WORK_LOG.md` (rotated archive)

### Writer References Updated (4 files)
- ✅ `tools/save_oneshot.sh` - Updated AI_WORK_LOG.md path
- ✅ `tools/save_fallback.sh` - Updated AI_WORK_LOG.md path
- ✅ `tools/save.sh` - Updated 2 AI_WORK_LOG.md references
- ✅ `BOOTUP.md` - Updated all state file paths

### Enforcement Added
- ✅ `.githooks/pre-commit` - Prevents future awareness file duplication
- ✅ `ci_duplicate_guard.sh` - CI check for awareness namespace compliance
- ✅ `.github/workflows/ci.yml` - Added awareness-guard job

## ✅ Acceptance Tests

### 1. No stale writer paths remain
```bash
$ grep -R "docs/ai-awareness/AI_WORK_LOG.md" . --exclude-dir=.git --exclude-dir=docs/ai-audits || echo "OK: no old writer paths found"
OK: no old writer paths found
```

### 2. No root duplicates of awareness files
```bash
$ ls -la | grep -E '^.*(NOW|NEXT|STATUS|AI_WORK_LOG|AI_DISCUSSION_SPACE)\.md' || echo "GOOD: No root duplicates"
GOOD: No root duplicates
```

### 3. Exactly one canonical copy under docs/awareness/
```bash
$ for f in NOW.md NEXT.md STATUS.md AI_WORK_LOG.md AI_DISCUSSION_SPACE.md REGISTRY.yml LOST_AND_FOUND.md; do
    echo "== $f =="; find . -name "$f" -not -path "./.git/*" -not -path "./docs/ai-audits/*"
  done

== NOW.md ==
./docs/awareness/NOW.md
== NEXT.md ==
./docs/awareness/NEXT.md
== STATUS.md ==
./docs/awareness/STATUS.md
== AI_WORK_LOG.md ==
./docs/awareness/AI_WORK_LOG.md
== AI_DISCUSSION_SPACE.md ==
./docs/awareness/AI_DISCUSSION_SPACE.md
== REGISTRY.yml ==
./docs/awareness/REGISTRY.yml
== LOST_AND_FOUND.md ==
./docs/awareness/LOST_AND_FOUND.md
```

### 4. Pre-commit guard blocks reintroductions
```bash
$ cp docs/awareness/NOW.md NOW.md && bash .githooks/pre-commit
❌ COMMIT BLOCKED: Awareness state files found outside docs/awareness/
The following files violate the awareness namespace policy:
  - ./NOW.md
```

### 5. CI duplicate guard passes
```bash
$ ./ci_duplicate_guard.sh
🔍 Checking awareness namespace compliance...
✅ Awareness namespace compliance: PASSED
📁 All awareness files properly located in docs/awareness/
```

## 📝 Notes

- All awareness state files now have a single canonical location: `docs/awareness/`
- The `docs/ai-awareness/` directory remains for Optional Meta files (SPARKS, DECISIONS, etc.)
- All writer scripts have been updated to write to the new location
- Automated enforcement prevents future regressions

## 🚀 Impact

This consolidation ensures:
1. **Single Source of Truth**: No more confusion about which file is canonical
2. **Clean Namespace**: Clear separation between state files and optional meta
3. **Automated Enforcement**: Pre-commit hooks and CI checks prevent duplicates
4. **Consistent Writers**: All scripts write to the same location

---

**Ready for merge after CI passes.**