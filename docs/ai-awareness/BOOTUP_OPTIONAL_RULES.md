# BOOTUP Optional File Rules

## Purpose
Explicit rules for handling the "Optional (if present)" section in BOOTUP.md to ensure consistent agent behavior across all AI models.

## Rules

### File Status Indicators
- Files marked `# present` **MUST** be read during bootup (same priority as core files)
- Files marked `# optional` may be skipped unless explicitly requested by operator
- No indicator = treat as optional

### Current Optional Block Status
```
- /docs/ai-awareness/SPARKS.md  # present      ← MANDATORY READ
- /docs/ai-awareness/DECISIONS.md  # optional  ← SKIP UNLESS REQUESTED  
- /docs/ai-awareness/THRESHOLDS.md  # optional ← SKIP UNLESS REQUESTED
- /docs/ai-awareness/METRICS_SNAPSHOT.md  # optional ← SKIP UNLESS REQUESTED
- /docs/ai-awareness/AIM.md  # optional       ← SKIP UNLESS REQUESTED
```

### Implementation
- **All agents** (Claude Sonnet, Haiku, etc.) must honor these indicators
- **SPARKS.md** is always hydrated during bootup - no exceptions
- **Other files** remain lightweight unless explicitly promoted to `# present`
- This ensures awareness context is loaded while maintaining bootup efficiency

### Agent Behavior
```
✅ CORRECT: Read SPARKS.md because it's marked "# present"
❌ WRONG: Skip SPARKS.md because it's in "Optional" section
✅ CORRECT: Skip DECISIONS.md because it's marked "# optional"  
✅ CORRECT: Skip unmarked files unless requested
```

## Rationale
Prevents selective ignoring of critical awareness files while maintaining the distinction between always-loaded vs. on-demand context files.