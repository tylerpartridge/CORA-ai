# 💾 CHECKPOINT SYSTEM - Awareness Synchronization Ritual

## 🎯 Purpose

The checkpoint system is a mandatory ritual that guarantees CORA awareness files are always synchronized, never stale, and never lost. It enforces state consistency across all AI sessions and prevents context degradation.

## 🕐 When to Checkpoint

### Mandatory Checkpoints:
- **Major milestones** - Feature completions, bug fixes, system changes
- **Risky operations** - Database migrations, production deployments, architecture changes  
- **End-of-day** - Before stopping work or switching contexts
- **Before handoff** - Claude ↔ Cursor transitions, session transfers
- **Pre-merge** - Before any PR/commit operations
- **Multi-agent tasks** - Before deploying parallel agents

### Quick Rule:
> If you're about to do something important or stop working → **CHECKPOINT FIRST**

## 📋 What Must Be Updated

### Core Files (All Required):
1. **STATE.md** - Current system status and health
2. **NEXT.md** - Task queue and priorities  
3. **AI_WORK_LOG.md** - Session activities and decisions
4. **HANDOFF.md** - Collaboration status and context
5. **AIM.md** - Strategic objectives and focus

### Checkpoint Capsule Format:
Each file must include a 5-10 line snapshot at the top:

```markdown
## 💾 CHECKPOINT: [YYYY-MM-DD HH:MM]
**Status:** [Current state in 1 line]
**Last Action:** [What was just completed]
**Next Priority:** [What comes next]
**Blockers:** [Any issues or dependencies]
**Context:** [Key details for next session]
```

## 🛡️ Guard Rules

### Pre-Merge Protection:
- ❌ **NO PR merges** without valid checkpoint
- ❌ **NO commits** without awareness files updated
- ❌ **NO production deployments** without checkpoint verification

### Enforcement Pattern:
```bash
# Before any major operation:
1. Update all 5 core awareness files
2. Add checkpoint capsule to each
3. Verify synchronization
4. THEN proceed with operation
```

## 🗂️ Compaction & Archiving Integration

### AI_WORK_LOG Management:
- **Target:** ≤ 300 lines maximum
- **Action:** When exceeded, archive older entries to `/docs/archive/work-logs/`
- **Retention:** Keep last 2 weeks in active file
- **Format:** Archive files named `AI_WORK_LOG_YYYY-MM-DD.md`

### SPARKS Pruning:
- **Schedule:** Every Friday
- **Action:** Move completed sparks to archive
- **Retention:** Keep active sparks only
- **Archive:** `/docs/archive/sparks/`

### NEXT Pruning:
- **Schedule:** At sprint close (weekly/bi-weekly)
- **Action:** Archive completed tasks and old priorities
- **Retention:** Keep current sprint + next sprint only
- **Archive:** `/docs/archive/next/`

## 🔄 Checkpoint Execution Pattern

### Step 1: Status Assessment
```markdown
# Check current state
- What was accomplished this session?
- What's the current system status?
- Are there any blockers or issues?
```

### Step 2: File Updates
```markdown
# Update each file with checkpoint capsule
1. STATE.md - System health and status
2. NEXT.md - Updated priorities and queue
3. AI_WORK_LOG.md - Session summary and decisions
4. HANDOFF.md - Collaboration context
5. AIM.md - Strategic alignment check
```

### Step 3: Verification
```markdown
# Ensure synchronization
- All files have current timestamp
- Capsules are consistent across files
- No conflicting information
- Context is preserved for next session
```

## 📖 Example Checkpoint Capsule

```markdown
## 💾 CHECKPOINT: 2025-08-29 14:30
**Status:** Beta launch ready - all core features operational
**Last Action:** Completed checkpoint system documentation
**Next Priority:** Begin beta user acquisition program
**Blockers:** None - system fully operational
**Context:** 53/65 MVP items complete, production routes fixed
```

## 🚨 Checkpoint Discipline Enforcement

### For AI Sessions:
- **Before major file operations** → Run checkpoint
- **Before ending session** → Run checkpoint  
- **Before handoff to another AI** → Run checkpoint
- **After major completions** → Run checkpoint

### For Development Teams:
- **Before merging PRs** → Verify checkpoint exists
- **Before production deploys** → Verify checkpoint exists
- **Before major refactors** → Run checkpoint
- **Before context switches** → Run checkpoint

## 🎯 Success Metrics

### Checkpoint Quality:
- ✅ All 5 files updated with consistent information
- ✅ Capsules contain actionable next steps
- ✅ No stale or contradictory information
- ✅ Context preserved across sessions

### System Health:
- ✅ Zero context loss incidents
- ✅ Smooth AI handoffs
- ✅ Consistent awareness across sessions
- ✅ Reduced context confusion

---

**Remember:** Checkpoints are not optional - they're the foundation of CORA's awareness system. When in doubt, checkpoint. Better to over-checkpoint than lose critical context.