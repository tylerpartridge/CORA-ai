# ⚡ SYSTEM RULES - CHECK BEFORE EVERY ACTION

## 🚨 MANDATORY: Use PREFLIGHT_CHECKLIST.md before ANY file operation!

## 📋 FILE CREATION GUIDELINES
- **Root dir:** Target 10 files (currently at limit!)
- **New files:** NEVER in root - ask WHERE first
- **Python/JS:** Target 300 lines (guideline, not rule)
- **Edit vs Create:** DEFAULT TO EDIT - Creation requires STRONG justification
  - **First question:** "Can this go in an existing file?"
  - **Answer is YES if:** Any existing file handles related functionality
  - **Creation allowed ONLY when:** No related file exists AT ALL
  - **When uncertain:** EDIT the closest match

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