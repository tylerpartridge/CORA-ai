# 🤔 Decisions Log - 2025-01-08

## Architecture Decisions

### File Size Limits
**Decision:** 300-line maximum for all state files
**Reason:** Prevents overwhelming both human and AI
**Impact:** Forces regular archiving and clean structure

### Directory Structure  
**Decision:** Use .mind/ instead of .ai/
**Reason:** Clearer metaphor - this is our shared mind/memory
**Impact:** Better mental model for collaboration

### Root Directory
**Decision:** Only dashboard files in root (NOW, NEXT, STATUS)
**Reason:** Root = command center, not storage
**Impact:** Always clean, always navigable

### Save Strategy
**Decision:** Multiple small files vs one large state
**Reason:** Faster retrieval, targeted updates
**Impact:** More granular but more organized

### Save Command System
**Decision:** Single "save" command for checkpointing
**Reason:** Simple for human, intelligent evaluation by AI
**Impact:** Prevents both over-saving and missed milestones

### BOOTUP.md Ownership
**Decision:** Claude maintains both sections of BOOTUP.md
**Reason:** Claude has full system view, Cursor focuses on code
**Impact:** Single source of truth, consistent updates

### Folder Documentation Location
**Decision:** Document folder purposes in .mind/maps/system_structure.md
**Reason:** Avoids adding files to root, keeps system knowledge centralized
**Impact:** Clear folder purposes without violating 4-file root rule

### Transition Document Handling
**Decision:** Migration summaries and transition docs go to archive/
**Reason:** They document past events, not current state
**Impact:** Keeps .mind/ focused on active work only

### Save Timing Decision
**Decision:** Proactively suggest "save" after significant changes
**Reason:** Prevents work loss, maintains session continuity
**When to save:**
- After completing a major task
- After system structure changes
- After running tests/validations
- After resolving issues or inconsistencies
**Impact:** Better work preservation and clearer progress tracking

### CORA Positioning Decision
**Decision:** CORA is a comprehensive AI business brain, not just bookkeeper
**Reason:** Bookkeeping is the wedge, but vision is total business intelligence
**Scope:** Business planning, finance, tax, legal, bookkeeping, integrations
**Key differentiator:** AI-to-AI native - built for AI assistant economy
**Impact:** All features/messaging should reinforce comprehensive capability

### Workflow Optimization Decision
**Decision:** Adopt todo-first, save-often workflow pattern
**Reason:** Today's deployment proved this combination prevents dropped tasks
**Key patterns:**
- Start every session with TodoWrite
- Save after each milestone/success
- Create reference docs during teaching
- Read-extract-delete for sensitive files
**Impact:** Smoother human-AI collaboration, nothing forgotten

### AI Tool Usage Decision  
**Decision:** Use ALL tools actively, not just favorites
**Reason:** TodoWrite transformed session effectiveness when finally adopted
**Priority order:**
1. TodoWrite - First thing in any session
2. Save commands - After every milestone
3. Read/Edit tools - For all file operations
4. Task tool - For complex searches
**Impact:** Maximum leverage of the .mind/ system

### Continuous Improvement Meeting Decision
**Decision:** Hold "decompression meetings" after achievements
**Reason:** Today's reflection session yielded valuable workflow improvements
**Types:**
- Quick strategic (2-3 min during work)
- Milestone meetings (15-20 min after big wins)
- End-of-session debriefs
**Principle:** Less complicated, more data-dense
**Impact:** Continuous workflow optimization through reflection

### Terminal Execution Decision
**Decision:** Use Cursor's Bash tool for all local commands
**Reason:** Keeps human in one interface, reduces context switching
**Rule:** If Cursor can do it, Cursor should do it
**Exceptions:** SSH sessions (must be manual)
**Bad pattern:** "Open PowerShell and run X"
**Good pattern:** Execute directly with Bash tool
**Impact:** Smoother workflow, leverage Cursor's full capabilities

### Insight Capture Decision
**Decision:** Strategically capture insights from casual conversation
**Reason:** Valuable patterns emerge in natural discussion
**High-value triggers:** "I wish...", "What if...", "Next time..."
**Compression rule:** Verbose chat → Dense insight → Right file
**File routing:** Actionable→decisions, Vision→vision files, Process→workflow
**Impact:** Continuous improvement without documentation bloat