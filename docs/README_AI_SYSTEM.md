# 🤖 CORA's AI-Friendly Architecture

This is CORA v4 - rebuilt from scratch with AI collaboration in mind. Here's how it works:

## 🎯 Core Philosophy

1. **Self-Documenting**: Every file knows where it is and what it does
2. **Self-Indexing**: System can map itself automatically  
3. **Context Preserving**: AI never loses track of the project
4. **Sprawl Preventing**: Hard limits and clear boundaries

## 🗂️ The .ai/ Folder System

The `.ai/` folder is the AI's memory:

```
.ai/
├── CURRENT_FOCUS.md      # What we're working on RIGHT NOW
├── SYSTEM_MAP.md         # Where everything lives (auto-generated)
├── FORBIDDEN.md          # What NOT to build (prevents scope creep)
├── CONVENTIONS.md        # How to write code
├── CHECKPOINT.md         # Progress tracking
├── NEXT_FEATURES.md      # Future plans (don't build yet!)
├── QUICK_NAV.md          # Jump to any file by purpose
├── ACTIVE_FILES.md       # NEW! Complete file manifest
└── snapshots/            # Context snapshots for restoration
```

## 🚀 NEW: Entry Point Discovery

Based on AI feedback, we now have:
- `.entrypoint` file at root - instantly find main server
- Updated `.cursorrules` - check entrypoint first
- Enhanced `restore_context.py` - better restoration flow

## 🚀 Essential Commands

```bash
# Start development (ALWAYS use this)
python start_cora.py

# Update all indexes
python index_cora.py

# Check system health
python health_check.py

# Restore AI context
python restore_context.py

# Smart git commit
python git_smart.py "Your message"

# Prepare for deployment
python git_smart.py deploy
```

## 🧭 Navigation Headers

Every Python file starts with:

```python
"""
🧭 LOCATION: /CORA/[path]
🎯 PURPOSE: [What this file does]
🔗 IMPORTS: [What it needs]
📤 EXPORTS: [What it provides]
🔄 PATTERN: [Design pattern if any]
📝 TODOS: [What's next]
"""
```

This allows AI to understand the codebase instantly.

## 📏 Hard Limits

- **Files**: Max 300 lines (split before this!)
- **Functions**: Max 50 lines
- **Classes**: Max 150 lines
- **Total Files**: Stay under 50 for v4

## 🔄 Workflow for AI Sessions

1. **Start Fresh**:
   ```bash
   python start_cora.py  # Updates indexes, checks health
   ```

2. **Lost Context?**:
   ```bash
   python restore_context.py  # Generates restoration prompt
   ```

3. **Before Committing**:
   ```bash
   python git_smart.py "What you did"  # Smart commit with context
   ```

## 🚫 What Makes This Different

Unlike Ghost's 400+ files:
- **No utils.py** - Each file has ONE job
- **No deep nesting** - Find files instantly
- **No manual indexes** - System self-documents
- **No context loss** - Everything is connected

## 💡 Key Insights

1. **Breadcrumbs Everywhere**: Every file points to related files
2. **AI Hints in Code**: Strategic comments guide AI behavior
3. **Automatic Indexing**: No manual documentation maintenance
4. **Progressive Disclosure**: Build only what's needed NOW

## 🎓 For Humans

This system is designed for solo developers working with AI assistants. It assumes:
- You value simplicity over "proper" architecture
- You want to ship, not engineer
- You're building a business, not a codebase

## 🔮 Future Vision

As CORA grows:
- Phase 2: Add payment processing (5-10 files)
- Phase 3: Add AI categorization (5-10 files)  
- Phase 4: Add API layer (10-15 files)

Total target: <50 files for a complete product

---

Remember: Every file must earn its existence by bringing in customers!