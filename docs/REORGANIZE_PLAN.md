# 🔄 CORA Reorganization Plan

## Current Problem
- Root has 24 files (should have 4)
- No clear separation of concerns
- Violates our "root as mental index" principle

## Target Structure
```
CORA/
├── 🚀 app.py          # Entry point
├── 📋 NOW.md          # Current task
├── 🎯 NEXT.md         # Task queue
├── 📊 STATUS.md       # System health
│
├── 📚 docs/           # All documentation
├── 🌐 web/            # Templates + static files
├── 🔧 tools/          # Scripts and utilities
├── 💾 data/           # Configs and user data
├── 📦 core/           # Business logic (when needed)
└── 🧠 .mind/          # AI memory system
```

## Migration Commands
```bash
# 1. Create directories
mkdir -p docs web data

# 2. Move documentation
mv CORA_V4_PLAN.md DEPLOY_GUIDE.md HUMAN_TRAINING.md docs/
mv ORGANIZE_AFTER_MOVE.md QUICK_REFERENCE.md README_AI_SYSTEM.md docs/
mv SAVE_SYSTEM.md my_learning_log.md docs/

# 3. Move web files
mv static templates web/

# 4. Move tools (already have tools/)
mv *.py tools/
mv MOVE_CORA.bat tools/

# 5. Move config
mv requirements.txt data/

# 6. Handle assets (design files)
mv assets docs/  # These are reference materials
```

## Benefits
- Root stays clean (4 files only)
- Clear mental model
- Easy navigation
- No sprawl

Execute? (This will clean up our organization immediately)