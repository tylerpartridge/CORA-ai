# 🚀 SESSION BOOTUP PROMPTS

## For Claude (Full Context)

---

I'm starting a new work session on CORA. Please:

1. Read these files in this exact order:
   - NOW.md (current task)
   - STATUS.md (system health) 
   - .mind/today/session.md (recent work)
   - NEXT.md (upcoming tasks)

2. Check file sizes:
   - Windows: python tools/check_sizes.py
   - Linux/WSL: ./tools/check_sizes.sh
   - Flag any files over 70% full

3. Give me a brief summary:
   - **Last task:** (1 line)
   - **System status:** (1 line)
   - **Recommended next:** (1 line)

4. If it's a new day, remind me to run:
   - Windows: python tools/auto_archive.py --daily
   - Linux/WSL: ./tools/auto_archive.sh --daily

Then wait for my direction.

**Quick Commands:**
- "save" - Checkpoint progress
- "hydrate" - Refresh my context
- "status" - System health check
- "focus" - Current task reminder
(Full list in .mind/maps/commands.md)

**I'll remind you to:**
- "save" after major accomplishments
- "hydrate" during long sessions (30+ min)
- "check status" after system changes

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

Teaching mode: Use "TEACH: [topic]" for explanations
Key docs: .mind/maps/system_structure.md (folder purposes)
         .mind/maps/ai_architecture.md (conventions)

DEFAULT: Read documentation before answering. Never create without permission.

---