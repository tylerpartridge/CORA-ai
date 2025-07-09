# 🚀 SESSION BOOTUP PROMPTS

## For Claude (Full Context)

---

I'm starting a new work session on CORA. Please:

1. **Start with todos** - Use TodoWrite to capture session goals

2. Read these files in this exact order:
   - NOW.md (current task)
   - STATUS.md (system health) 
   - .mind/today/session.md (recent work)
   - NEXT.md (upcoming tasks)

3. Check file sizes (use Bash tool directly):
   - Windows: python tools/check_sizes.py
   - Linux/WSL: ./tools/check_sizes.sh
   - Flag any files over 70% full

4. Give me a brief summary:
   - **Last task:** (1 line)
   - **System status:** (1 line)
   - **Recommended next:** (1 line)

5. If it's a new day, remind me to run:
   - Windows: python tools/auto_archive.py --daily
   - Linux/WSL: ./tools/auto_archive.sh --daily

Then wait for my direction.

**Quick Commands:**
- "save" - Checkpoint progress
- "hydrate" - Refresh my context
- "status" - System health check
- "focus" - Current task reminder
- "meeting" - Decompression after milestones
(Full list in .mind/maps/commands.md)

**Workflow patterns:**
- Todo-first: Always start with TodoWrite
- Save-often: After each milestone/success
- Use tools: Bash for local commands (not manual terminal)
- Meet-and-improve: Quick decompression after big wins
- Read-extract-delete: For sensitive files

---

*This file: /CORA/BOOTUP.md*

## For Cursor (Code Assistance)

---

New CORA session. CRITICAL RULES:

1. NEVER create/modify files unless explicitly asked
2. ALWAYS read/search files to find accurate answers
3. When asked "where does X go?", check .mind/maps/system_structure.md first
4. Navigation headers MANDATORY for Python files
5. File limit: 300 lines, Function limit: 50 lines
6. One file = one purpose (no utils.py)

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