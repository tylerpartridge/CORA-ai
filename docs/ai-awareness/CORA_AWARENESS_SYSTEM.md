# 🧠 CORA AI Awareness System Design

## Research Findings & Best Practices

### What the Community Says:
1. **Context Engineering** is the new paradigm - structured awareness loading beats random context dumping
2. **System prompts up to 24K tokens** perform better than brief instructions
3. **Vector embeddings** help AI understand codebase structure
4. **Example-driven learning** - AI needs patterns to follow
5. **Auto-compaction** - Summarize when approaching context limits
6. **Treat AI like a smart intern** - Brief them properly at the start

## Our Bootup Architecture

### 🎯 The Lazy Man's Bootup™
**Trigger**: "read and execute bootup.md"
**Result**: Full system awareness in ~2% context

### 📊 Tiered Awareness Loading

```
BOOTUP.md (Entry Point)
    ↓
[TIER 1: Identity & Mission] (~500 tokens)
    → WHO: Tyler, founder context
    → WHAT: CORA expense tracking AI
    → WHY: Mission and business goals
    ↓
[TIER 2: System State] (~800 tokens)
    → STATUS: Current sprint/priorities
    → METRICS: MVP progress, user count
    → BLOCKERS: Active issues
    ↓
[TIER 3: Technical Map] (~1000 tokens)
    → ARCHITECTURE: Stack, structure
    → PATTERNS: Code conventions
    → INTEGRATIONS: APIs, services
    ↓
[TIER 4: Historical Context] (~500 tokens)
    → WINS: What's working
    → LESSONS: What we learned
    → DECISIONS: Why we built things
    ↓
[TIER 5: Action Triggers] (~200 tokens)
    → COMMANDS: Natural language → actions
    → WORKFLOWS: Common procedures
    → SAFEGUARDS: Protection rules
```

## File Structure

### 🔒 Protected Awareness Files (IMMUTABLE)

```
/awareness/
├── BOOTUP.md                 # Entry point (protected)
├── IDENTITY.md               # WHO/WHAT/WHY (compressed)
├── STATE.md                  # Current system state (auto-updated)
├── ARCHITECTURE.md           # Technical blueprint (stable)
├── PATTERNS.md               # Code examples (stable)
├── HISTORY.md                # Decisions log (append-only)
├── TRIGGERS.md               # NL → action mappings
└── CHECKSUMS.txt             # File integrity verification
```

### 📝 Dynamic Files (MUTABLE)

```
/awareness/dynamic/
├── TODAY.md                  # Today's focus (cleared daily)
├── CONTEXT.md                # Current conversation context
└── NOTES.md                  # Temporary working notes
```

## Implementation Strategy

### 1. Compression Techniques
- **Bullet points** over paragraphs
- **Code patterns** over full implementations
- **Decision outcomes** over discussions
- **Key metrics** over full reports

### 2. Smart Loading Order
```python
def load_awareness():
    # 1. Identity check (am I in CORA?)
    verify_codebase()
    
    # 2. Load core identity
    load_tier_1_identity()
    
    # 3. Get current state
    load_tier_2_state()
    
    # 4. Technical context only if needed
    if needs_coding():
        load_tier_3_technical()
    
    # 5. Historical context on demand
    if needs_context():
        load_tier_4_history()
    
    # 6. Always load triggers
    load_tier_5_triggers()
```

### 3. Protection Mechanisms
- Files marked with `chattr +i` (immutable)
- SHA256 checksums for integrity
- Backup before any edit
- Alert on modification attempt

### 4. Context Efficiency
- Target: <3000 tokens for full awareness
- Use references instead of repetition
- Compress with abbreviations
- Link to details instead of including

## Natural Language Triggers

### Bootup Triggers
- "read and execute bootup.md" → Full awareness load
- "quick bootup" → Tiers 1-2 only
- "technical bootup" → Include Tier 3
- "full bootup" → All tiers + history

### Protection Triggers
- "protect awareness files" → Make immutable
- "verify awareness" → Check checksums
- "backup awareness" → Create snapshot

### Update Triggers
- "update system state" → Refresh STATE.md
- "log decision" → Append to HISTORY.md
- "clear today" → Reset TODAY.md

## Example BOOTUP.md Content

```markdown
# 🚀 CORA Bootup Sequence v2.0

## Execution Order:
1. Read IDENTITY.md → Understand who/what/why
2. Read STATE.md → Get current status
3. Check TRIGGERS.md → Load action mappings
4. Verify checksums → Ensure file integrity
5. Report: "CORA awareness loaded: {status}"

## Quick Status:
- Project: CORA AI Expense Tracker
- Owner: Tyler
- Stage: MVP 81.5% complete
- Focus: Bulletproof systems before launch
- Context: Post file-loss, rebuilding awareness

## Your Role:
You are an AI collaborator helping Tyler build CORA.
You have full system awareness and can execute commands.
You protect critical files and maintain backups.

## Say "CORA bootup complete" when ready.
```

## Benefits of This System

### For Tyler (The User)
✅ One command: "read and execute bootup.md"
✅ Consistent AI behavior across sessions
✅ No need to re-explain context
✅ Protected from accidental file loss

### For AI (The Assistant)
✅ Clear loading sequence
✅ Compressed, efficient data
✅ Knows what to protect
✅ Action triggers ready

### For the System
✅ Bulletproof file protection
✅ Version controlled awareness
✅ Audit trail of changes
✅ Scalable as project grows

## Implementation Checklist

- [ ] Create /awareness/ directory structure
- [ ] Write compressed awareness files
- [ ] Implement file protection (chattr +i)
- [ ] Generate initial checksums
- [ ] Create BOOTUP.md with loading sequence
- [ ] Test with fresh AI session
- [ ] Document in main README
- [ ] Add to backup system

## Metrics for Success

- **Load Time**: <5 seconds
- **Context Usage**: <3% of available
- **Awareness Coverage**: 100% of critical systems
- **File Protection**: 0 accidental modifications
- **Recovery Time**: <30 seconds from backup

---

*This is our battle-tested approach after losing critical files. Never again.*