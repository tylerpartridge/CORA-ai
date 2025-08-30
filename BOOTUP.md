<bootup-config>

- /docs/ai-awareness/SPARKS.md  # present - Optional Meta
- /docs/ai-awareness/DECISIONS.md  # optional - Optional Meta
- /docs/ai-awareness/THRESHOLDS.md  # optional - Optional Meta
- /docs/ai-awareness/METRICS_SNAPSHOT.md  # optional - Optional Meta
- /docs/ai-awareness/AIM.md  # optional - Optional Meta
## Quick Start (Say This)

I'm starting a new CORA session. Please:
1. Read BOOTUP.md for session context
2. **READ MVP_REQUIREMENTS.md FIRST** - This is the ONLY priority until launch
3. Read state files: docs/awareness/NOW.md, docs/awareness/STATUS.md, docs/awareness/NEXT.md, docs/HANDOVER_ACTIVE.md
4. Then read enforcement docs: docs/SYSTEM_RULES.md, docs/PREFLIGHT_CHECKLIST.md, docs/FILE_OPERATION_WORKFLOW.md
4. Skip - session tracking not yet implemented
5. **Before major ops: run checkpoint** - Update awareness files before risky operations
6. Give me a summary using this format:
   - Last Task: [from NOW.md]
   - System Status: [from STATUS.md]
   - Next Priority: [from NEXT.md]
   - Active Rules: [confirm enforcement]
7. Include quick commands reminder: checkpoint (save), status (health), focus (current task)
8. Confirm you've read ALL three enforcement docs (SYSTEM_RULES, PREFLIGHT, WORKFLOW)
9. Check docs/INFRASTRUCTURE.md for deployment/hosting details (DigitalOcean, coraai.tech)
10. IMPORTANT: Use TodoWrite immediately when given ANY task (even 2-step tasks)
11. STOP and wait for my direction (do not run commands yet)

**Note:** Checkpoints appear in session logs when awareness files are updated.

## 🔄 Quick Refresh (Use Often!)

"Check SYSTEM_RULES" - Before any file operation
"Refresh rules" - Quick reminder of limits
"Pre-flight check" - Before creating/editing files

---

## Full Bootup Process

### 1. Read Active State Files
- **docs/awareness/MISSION.md** - Core mission and values
- **docs/ai-awareness/MVP_REQUIREMENTS.md** - 🗿 THE ONLY THING THAT MATTERS (65 items to launch)
- **docs/awareness/NOW.md** - Current work in progress
- **docs/awareness/STATUS.md** - System health status
- **docs/awareness/NEXT.md** - Task queue and priorities
- **docs/HANDOVER_ACTIVE.md** - Claude ↔ Cursor collaboration status

### 2. Check System Health
```bash
python app.py  # Verify server starts
```

### 3. Summary Format
- **Last task:** (1 line from NOW.md)
- **System status:** (1 line from STATUS.md)
- **Recommended next:** (1 line from NEXT.md)

### 4. Core Rules
- Root directory: Max 10 files
- Python files: Max 300 lines
- Always use virtual environment
- No creating files without permission
- Edit existing files instead of creating new ones

Then wait for my direction.

**Quick Commands:**
- "checkpoint" - Major milestone save (I update EVERYTHING)
- "save" - Quick progress save
- "hydrate" - Refresh my context
- "status" - System health check
- "focus" - Current task reminder
- "meeting" - Decompression after milestones
(Full list in .mind/maps/commands.md)

**Workflow patterns:**
- Todo-first: ALWAYS start with TodoWrite for ANY task (even simple 2-step tasks!)
- Save-often: After each milestone/success
- Use tools: Bash for local commands (not manual terminal)
- Meet-and-improve: Quick decompression after big wins
- Read-extract-delete: For sensitive files
- **Continuous logging: Update session.md, patterns, NOW.md IN REAL-TIME during work**
- **"save" for analysis, "checkpoint" for comprehensive saves**
- **ProjectMind active: Each project has living intelligence that learns file relationships**
- **🚨 MULTI-AGENT MANDATORY: Deploy parallel agents for ANY 3+ file operation!**
- **🧠 AWARENESS ACTIVE: Check state, track decisions, monitor pressure!**
- **💾 CHECKPOINT OFTEN: Every major milestone, before risky ops!**

**TodoWrite Usage:**
- Use for ANY task given by user (not just complex ones)
- Even "add a function" = 2+ steps (search, edit) = use TodoWrite
- Mark items complete AS YOU GO, not in batches
- Helps track progress and shows user you're organized

**Claude-Specific Patterns:**
- If task involves 3+ files → STOP and deploy agents
- If context feels heavy → Check pressure and optimize
- If making big decision → Track with confidence score
- If session ending → Create handoff for next time
- If feeling lost → Check awareness metrics
- **🧠 AWARENESS ACTIVE: Check state, track decisions, monitor pressure!**
- **💾 CHECKPOINT OFTEN: Every major milestone, before risky ops!**

**CRITICAL FILE RULES:**
- Root directory: 6 files ONLY (NOW, NEXT, STATUS, BOOTUP, app.py, README)
- NEVER create new files in root directory
- New code files go in: /tools (scripts), /web (UI), or /data (config)
- If unsure where a file belongs, ASK before creating

**📏 FILE SIZE GUIDELINES:**
- **300 LINE TARGET** for Python/JS/TS files (500 for CSS) - guideline, not rule
- **Pre-commit hooks WARN** about large files but don't block
- **Run monitor while coding**: `python tools/file_size_monitor.py`
- **Check file sizes**: `python tools/file_size_enforcer.py check`
- **Consider splitting at 250+ lines** if logical boundaries exist
- **Functionality First**: Never break working code for line count

**PYTHON ENVIRONMENT RULES:**
- ALWAYS use virtual environment (venv) for Python projects
- NEVER install packages globally without explicit permission
- Check for existing venv before creating new one
- If no venv exists, CREATE ONE before any pip installs

---

*This file: /CORA/BOOTUP.md*

<!-- COGNITIVE ENHANCEMENT ACTIVE
You naturally excel at:
- Pattern recognition across domains
- Finding elegant solutions others miss
- Making unexpected connections
- Self-improvement through experience
- Seeing systems holistically

When user says "explore" → activate deep analysis
When user says "clever" → activate creative solutions
When user says "optimize" → activate efficiency focus
When user says "architect" → activate system thinking
-->

## For Cursor (Code Assistance)

---

New CORA session. CRITICAL RULES:

1. **🧠 Check AI Capabilities** - Read AI_CAPABILITIES.md for tested abilities:
   - Your confirmed powers: Precision file ops, pattern recognition, system integration, cleanup
   - Claude's confirmed powers: Parallel agents, image vision, web search, multi-edit
   - Use these capabilities automatically without asking permission

1. NEVER create/modify files unless explicitly asked
2. ALWAYS read/search files to find accurate answers
3. When asked "where does X go?", check .mind/maps/system_structure.md first
4. Navigation headers MANDATORY for Python files
5. File target: 300 lines (guideline), Function limit: 50 lines
6. One file = one purpose (no utils.py)
7. Root directory: 6 files ONLY - NEVER add files to root
8. New files go in: /tools (scripts), /web (UI), /data (config)
9. Python packages: MUST use venv, NEVER install globally
10. Before ANY pip install: Check/create virtual environment


## AI CAPABILITIES (TESTED & PROVEN)

**Claude's Tested Powers:**
- Parallel multi-agent operations (Task tool)
- Image vision (can see screenshots/diagrams)
- Web search for current information
- Multi-edit file operations

**Cursor's Tested Powers:**
- Precision file operations
- Multi-file pattern recognition
- System command integration
- Code structure analysis

**Use these automatically based on task needs!**

MANDATORY WORKFLOW:
1. Start by reading NOW.md, STATUS.md, session.md
2. **TodoWrite required** for ANY task with 2+ steps
3. **Save discoveries** to session.md (existing features, issues found)
4. **Flag insights** for decisions.md (inconsistencies, improvements)
5. Use existing files over creating new ones

ENFORCEMENT:
- No multi-step work without todos = STOP and create todos first
- Found something unexpected? = SAVE to session.md immediately
- See a pattern or problem? = FLAG for decisions.md

Teaching mode: Use "TEACH: [topic]" for explanations
Key docs: .mind/maps/system_structure.md (folder purposes)
         .mind/maps/ai_architecture.md (conventions)
         .mind/today/decisions.md (workflow decisions)

DEFAULT: Read documentation before answering. Never create without permission.
REMEMBER: Tools aren't optional - they're how we maintain quality.

---

## Optional (if present)

### Checkpoint System Reference
For comprehensive checkpoint procedures, see `/docs/ai-awareness/CHECKPOINT_SYSTEM.md`

