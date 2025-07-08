# 🏗️ CORA Organization Plan - Self-Organizing Structure

## The Vision
Root directory = Visual dashboard. One glance tells the whole story.

## New Structure (After Move)
```
C:\CORA\
├── app.py                 # ⚡ Main server
├── start.py               # 🚀 Always run this first
├── requirements.txt       # 📦 Dependencies
├── .env.example          # 🔧 Config template
├── .cursorrules          # 🤖 AI instructions
├── .entrypoint           # 📍 Quick navigation
├── .ai/                  # 🧠 AI memory system
├── tools/                # 🔨 Utilities (4 files)
├── docs/                 # 📚 Human guides (3 files)
├── templates/            # 🎨 HTML/UI
└── static/               # 🖼️ Images/CSS/JS
```

## Self-Organizing Rules

### Rule 1: Entry Justification
Every file/folder must answer: "Why are you in root?"
- Direct entry points → Root
- Supporting tools → tools/
- Documentation → docs/
- Code → modules/ (when needed)

### Rule 2: Visual Hierarchy
Root shows WHAT you can do:
- `app.py` - Run the server
- `start.py` - Start development
- `tools/` - Use utilities
- `docs/` - Learn the system

### Rule 3: Growth Protection
When adding files:
1. Does it belong in root? (Probably not)
2. Does a folder exist? (Use it)
3. Need new folder? (Justify it)
4. Update .ai/SYSTEM_MAP.md

## Implementation After Move

1. **Reorganize files**:
```bash
mkdir tools docs
move health_check.py tools/
move index_cora.py tools/
move restore_context.py tools/
move git_smart.py tools/
move DEPLOY_GUIDE.md docs/
move HUMAN_TRAINING.md docs/
move README_AI_SYSTEM.md docs/
```

2. **Update tool imports**:
All tools need: `sys.path.append('..')` to find app.py

3. **Simplify names**:
- `start_cora.py` → `start.py`
- `index_cora.py` → `index.py`

## The Result

Opening C:\CORA shows instantly:
- What to run (app.py, start.py)
- Where to find things (tools/, docs/)
- How to configure (.env.example)
- What the rules are (.cursorrules)

Clean. Intuitive. Self-organizing.