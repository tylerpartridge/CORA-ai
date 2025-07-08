# 🤖 CORA AI Architecture & Collaboration System

## 🎯 Core Philosophy
1. **Self-Documenting**: Every file knows where it is and what it does
2. **Self-Indexing**: System can map itself automatically  
3. **Context Preserving**: AI never loses track of the project
4. **Sprawl Preventing**: Hard limits and clear boundaries

## 🧭 Navigation Headers (MANDATORY)
Every Python file MUST start with:
```python
"""
🧭 LOCATION: /CORA/[path]
🎯 PURPOSE: [One line description]
🔗 IMPORTS: [What this file imports]
📤 EXPORTS: [Main functions/classes]
🔄 PATTERN: [Design pattern if applicable]
📝 TODOS: [Next steps for this file]
"""
```

## 📏 Hard Limits (NO EXCEPTIONS)
- **Files**: Max 300 lines (split before this!)
- **Functions**: Max 50 lines
- **Classes**: Max 150 lines
- **Total Files**: Stay under 50 for v4
- **Root Files**: Exactly 4 (app.py, NOW.md, NEXT.md, STATUS.md)

When approaching limits, add:
`# 🚨 APPROACHING LIMIT: Split into [new_file.py] next`

## 📐 Naming Conventions
- **Files**: `feature_action.py` (e.g., `payment_process.py`)
- **Functions**: `verb_noun()` (e.g., `capture_email()`)
- **Classes**: `NounVerber` (e.g., `EmailCapture`)
- **NO**: utils.py, helpers.py, common.py

## 🚫 FORBIDDEN (Do NOT Build)
### Phase 1 - Not Yet:
- Payment processing (Stripe)
- User authentication
- Database models
- AI categorization
- Dashboard beyond landing
- API endpoints (beyond email capture)

### Architecture - Never:
- Abstract base classes
- Dependency injection
- Complex folder nesting
- Files over 300 lines
- Premature abstractions

**Core Rule**: "We need paying customers before we need infrastructure"

## 🎓 Micro-Learning System
Transform downtime into mastery:

### Learning Moments:
- **During installs (2-5 min)**: Read conventions
- **During deployment (5-10 min)**: Read guides section by section
- **During tests (1-3 min)**: Read current focus
- **During DNS wait (5-60 min)**: Read full vision docs
- **During startup (30 sec)**: Quick reference

### TEACH Protocol:
When you say "TEACH: [topic]", AI will:
1. Explain in 2-3 sentences max
2. Show concrete CORA example
3. Point to relevant file/line
4. Suggest next reading

### Daily Ritual:
- **Morning (2 min)**: Check NOW.md
- **Before coding (1 min)**: "TEACH: What convention applies?"
- **During breaks**: Pick a learning moment
- **End of day (3 min)**: Update .mind/today/session.md

## 🔄 Three-Way Collaboration
### The Three Intelligences:
1. **Human**: Vision, decisions, business sense
2. **Claude**: Architecture, strategy, system design
3. **Cursor**: Execution, teaching, immediate help

### Sync Commands:
- **To Cursor**: "TEACH: [what Claude explained]"
- **To Claude**: "Why does [Cursor's teaching] matter?"
- **Both**: "What should I read while waiting?"

### Learning Multipliers:
- **Echo**: Claude explains → Cursor shows → Human does → Document
- **Challenge**: Human asks → Claude creates path → Cursor exercises
- **Review**: Weekly review → Strategic + Tactical insights

## 🧠 The .mind/ System
Our shared memory structure:
```
.mind/
├── today/          # Current work (auto-archives)
├── archive/        # Historical by date
└── maps/           # System knowledge (this file!)
```

### Save Triggers:
- Task change → Update NOW.md
- Decision made → Append to decisions.md
- Progress made → Append to session.md
- File >300 lines → Auto-split and archive

## 🚀 Essential Commands
```bash
# Check file sizes
./tools/check_sizes.sh

# Archive if needed
./tools/auto_archive.sh

# For daily archive
./tools/auto_archive.sh --daily
```

## 💡 Key Success Factors
1. **One file = One purpose** (no sprawl)
2. **Breadcrumbs everywhere** (navigation headers)
3. **Size limits enforced** (auto-split)
4. **Daily archiving** (fresh starts)
5. **Three-way sync** (use all available intelligence)

## 🔮 Growth Path
As CORA grows:
- Phase 2: Payment (5-10 files)
- Phase 3: AI categorization (5-10 files)  
- Phase 4: API layer (10-15 files)
Target: <50 files total

---
Remember: Every file must earn its existence by bringing in customers!