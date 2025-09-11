# ⚡ SYSTEM RULES - CHECK BEFORE EVERY ACTION

**Collaboration Policy (2025-09-04):** Cursor is primary executor (code/git/deploy); Sonnet limited to audits/intel/codebase search; Opus removed. Prompts label target and call out Tyler-required steps.

SSOT: This file is the single source of truth for rules and guardrails. Other docs (PREFLIGHT_CHECKLIST.md, FILE_OPERATION_WORKFLOW.md, BOOTUP.md) reference this file and should not duplicate rules.
TodoWrite: Use `canmore.update_textdoc` for any multi‑step documentation edits (alias: "TodoWrite").

## TL;DR — Non‑negotiables
- **PRs‑only**: No direct commits to `main` unless RED; always PR → squash merge
- **Edit > Create**: Default to editing existing files; creation needs strong justification
- **Batch deploy windows**: 12:30 and 17:30 UTC only, unless RED
- **Prompt labeling**: Use SONNET / OPUS / CURSOR / TYLER blocks
- **Run `PREFLIGHT_CHECKLIST.md`** before any file operation

## 🚨 MANDATORY: Use PREFLIGHT_CHECKLIST.md before ANY file operation!

## Quick Commands (merge + sync + smokes)
```powershell
# Merge PR (admin), sync main
cd C:\CORA; gh pr merge <#> --squash --delete-branch --admin; git checkout main; git pull --prune

# Run PROD smokes (on server)
ssh -o BatchMode=yes root@159.203.183.48 "cd /var/www/cora && ./tools/smoke.sh --base-url http://127.0.0.1:8000 --retries 3 --timeout 5 && python3 tools/smoke.py --base-url http://127.0.0.1:8000 --retries 3 --timeout 5 --json"
```

## Verify PRs/Branches (post-automation sanity)
```bash
git fetch --all --prune
git branch -r | grep -E "(feature|fix|chore)/2025-09-08" || true
gh pr list -L 10 -s open
git log -1 --oneline
```

## Canonical Smokes (must pass)
- `/health` → 200
- `/api/status` → 200
- `/api/feature-flags` (unauth) → 401
- Scripts: `tools/smoke.sh` and `tools/smoke.py` (see `docs/runbooks/SMOKES.md`)

## Targets
- **PROD SSH**: `root@159.203.183.48` (alt: `root@coraai.tech`)
- **App path**: `/var/www/cora`
- **Postgres DSN file**: `/root/CORA_PROD_PG_DSN.env` (not in repo)

## 📋 FILE CREATION GUIDELINES
- **Root dir:** Target 10 files (currently at limit!)
- **New files:** NEVER in root - ask WHERE first
- **Python/JS:** Target 300 lines (guideline, not rule)
- **Edit vs Create:** DEFAULT TO EDIT - Creation requires STRONG justification
  - **First question:** "Can this go in an existing file?"
  - **Answer is YES if:** Any existing file handles related functionality
  - **Creation allowed ONLY when:** No related file exists AT ALL
  - **When uncertain:** EDIT the closest match

### Root Policy (explicit exceptions)
Allowed at repo root:
- app.py
- README.md
- GPT5_handoff.md
- OPERATIONS.md
- docs/ (directory)
- data/ (directory)
All other files should live under an appropriate subdirectory. Ask before adding new root items.

## ❌ THESE ARE NOT VALID REASONS TO CREATE FILES
- "Better separation of concerns" ❌ - ADD TO EXISTING FILE
- "Service layer pattern" ❌ - ADD TO EXISTING FILE  
- "Keep routes/controllers thin" ❌ - ADD TO EXISTING FILE
- "Single responsibility principle" ❌ - ADD TO EXISTING FILE
- "It would be cleaner" ❌ - ADD TO EXISTING FILE
- "Standard architecture" ❌ - ADD TO EXISTING FILE
- "Utils/helpers pattern" ❌ - ADD TO EXISTING FILE

**CORA Philosophy:** Simplicity > Separation. One file with 200 lines is better than 4 files with 50 lines each.

## 📁 WHERE FILES GO
- `/routes/` - API endpoints only
- `/models/` - Database models only
- `/services/` - Business logic only
- `/tools/` - Utility scripts
- `/docs/` - Documentation
- `/tests/` - Test files
- **NEVER:** Random files in root

## 📝 FILE REQUIREMENTS  
- **Python files:** MUST have navigation header
- **Headers format:** 🧭 LOCATION, 🎯 PURPOSE, 🔗 IMPORTS, 📤 EXPORTS
- **One file = One purpose** (no utils.py, no helpers.py)
- **Names:** Descriptive, not generic
- **Size guideline:** Target 300 lines BUT functionality > arbitrary splits
  - NEVER break working code just to hit line count
  - NEVER split if it breaks imports/dependencies
  - NEVER create coupling issues for size sake
  - DO split when natural boundaries exist
  - DO refactor when it improves architecture
  - **Functionality First:** Working code > line count guidelines

## 🔧 BEFORE YOU CODE
- Check: Will this exceed 300 lines? → Consider splitting IF logical boundary exists
- Check: Does similar file exist? → Edit it
- Check: Right directory? → Verify path
- Check: Has header? → Add it
- Check: Would splitting break functionality? → Keep together (functionality first)

## 🤝 COLLABORATION
- Check HANDOVER_ACTIVE.md before editing
- Never edit same file as partner
- Update status every 5-10 mins
- All GPT5_handoff.md session capsules must use UTC ISO-8601 timestamps (YYYY-MM-DDTHH:MMZ).

## ❌ NEVER DO THIS
- Create "test.py" or "temp.py" 
- Add files to root directory
- Break working code just to hit line count guidelines
- Create utils/helpers/common files
- Skip headers "to save time"

## 🚨 DURABLE WORKFLOW RULES (2025-09-03)

### Production Debugging & CI Guards
1. **CI guard for orphaned router imports** - CI should fail if `app.include_router(<name>)` is called without a corresponding import or defined symbol. This prevents production startup failures from missing routers.

2. **Stub-first rescue pattern** - In production incidents where a router is missing, create a minimal stub in `/routes/<name>.py` exporting both `router` and `<name>_router`, rather than patching `app.py` directly. This maintains clean separation and allows proper implementation later.

3. **Always journalctl before health probes** - On production debugging, check logs with `journalctl -u cora.service -n 80` before running curl probes. This avoids chasing misleading 000/timeout results when the real issue is visible in logs.

---
**CHECK THIS BEFORE EVERY: File creation, Edit, Move, or Delete**

Durable rules — last updated: 2025-09-03. Keep Part A stable; session-specific guidance belongs in `GPT5_handoff.md` Part B and `docs/awareness/NOW.md`/`NEXT.md`.
