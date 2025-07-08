# 💾 How AI Saves & Retrieves Data

## What Gets Saved & Where

### 1. NOW.md (Current Focus)
```markdown
# 🎯 Current Task: Implementing save system
Started: 2025-01-08 14:30
Working on: SAVE_SYSTEM.md design
Next: Create auto-save script
```

### 2. .mind/today/session.md (Detailed Progress)
```markdown
## Session: 2025-01-08 14:30
- Created SAVE_SYSTEM.md
- Updated NOW.md with current task
- Discovered Python not in WSL PATH
- Decision: Use bash scripts instead
```

### 3. .mind/today/decisions.md (Key Choices)
```markdown
## 2025-01-08
- DECISION: Use bash for scripts (Python not available)
- DECISION: 300 line limit for state files
- DECISION: Archive daily at midnight
```

## When I Save (Triggers)

### Automatic Saves (I'll use Edit/Write tools):
1. **Task Change** → Update NOW.md
2. **Major Decision** → Append to decisions.md  
3. **Completed Step** → Append to session.md
4. **Error/Learning** → Append to learnings.md

### Manual Save Commands You Can Give:
- "Save progress" → I'll update all relevant files
- "Checkpoint" → Full state dump to .mind/today/
- "Archive now" → Move today's files to archive/

## How I Save (The Actual Process)

```python
# When you say "I finished the login feature":

1. I use Edit tool:
   Edit("/mnt/host/c/CORA/NOW.md", 
        old="Working on: Login form",
        new="Working on: Login testing")

2. I use Write tool (append-style):
   current = Read(".mind/today/session.md")
   Write(".mind/today/session.md",
         current + "\n- Completed: Login feature")

3. If file > 300 lines:
   → Move overflow to .mind/archive/2025-01-08/
   → Start fresh file
```

## How I Retrieve What I Need

### On Session Start:
```bash
1. Read NOW.md        # Where we are
2. Read NEXT.md       # What's planned
3. Check .mind/today/ # Recent context
```

### When You Ask "What were we doing?":
```bash
1. Read NOW.md first
2. If need more detail → .mind/today/session.md
3. If need history → .mind/archive/*/
```

### Smart Retrieval (I won't read everything):
- **Recent work**: .mind/today/* (small files)
- **Yesterday**: .mind/archive/2025-01-07/summary.md
- **Specific search**: grep through archive/

## Example Workflow

**You**: "Let's add user authentication"

**Me** (internally):
1. Edit NOW.md → "Current Task: User authentication"
2. Write to session.md → "14:45 - Starting auth system"
3. Read existing auth files if any

**You**: "Actually, let's do payments first"

**Me** (internally):
1. Append to session.md → "14:50 - Switched to payments (auth postponed)"
2. Edit NOW.md → "Current Task: Payment integration"  
3. Append to NEXT.md → "- Resume auth system"

**You**: "Save checkpoint"

**Me**: 
1. Write full context to .mind/today/checkpoint-1450.md
2. Update STATUS.md with checkpoint timestamp
3. Confirm: "✓ Checkpoint saved"

## The Beauty:
- **No huge files** to parse
- **Clear triggers** for saves
- **Fast retrieval** with targeted reads
- **You see it all** in the filesystem

Want me to implement this system now?