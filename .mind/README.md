# 🧠 The .mind Directory

This is our shared memory system - where human intuition meets AI precision.

## Structure
```
.mind/
├── today/          # Current session (auto-archives nightly)
│   ├── session.md  # Progress log
│   ├── decisions.md # Key choices made
│   └── context.md  # Additional context
│
├── archive/        # Historical data
│   └── YYYY-MM-DD/ # Daily snapshots
│
└── maps/           # Navigation helpers
    ├── codebase.md # File/import relationships
    └── patterns.md # Common patterns
```

## Rules
1. **today/** gets archived to **archive/YYYY-MM-DD/** at midnight
2. Files over 300 lines get split
3. Each file has ONE clear purpose
4. Always timestamp entries

## For Humans
- Check today/ to see what AI has been doing
- Browse archive/ to find past decisions
- Read maps/ to understand the system

## For AI
- Start with today/context.md for session state
- Use archive/ for historical lookups only
- Update maps/ when structure changes