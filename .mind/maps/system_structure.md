# 🗺️ CORA System Structure Map

## Root Directory (5 files only!)
- `app.py` - FastAPI server entry point
- `NOW.md` - Current task tracking
- `NEXT.md` - Task queue
- `STATUS.md` - System health
- `BOOTUP.md` - AI startup prompt

## Folder Purposes

### /docs/ - Cold Storage Documentation
- **Purpose**: Reference materials, guides, old decisions
- **Examples**: DEPLOY_GUIDE.md, CORA_V4_PLAN.md, assets/
- **When used**: Rarely - only when you need historical info
- **Rule**: If you're opening it daily, it belongs elsewhere

### /.mind/ - Active AI Memory  
- **Purpose**: Current context, session tracking, system knowledge
- **Structure**: 
  - `today/` - Current session work
  - `archive/` - Historical sessions by date
  - `maps/` - System knowledge (like this file)
- **When used**: Every AI session, auto-archived daily
- **Rule**: 300 line limit per file

### /tools/ - Scripts & Utilities
- **Purpose**: Helper programs, automation, dev tools
- **Examples**: check_sizes.py, auto_archive.py, git_smart.py
- **When used**: During development for specific tasks
- **Rule**: One tool = one purpose

### /data/ - Config & Storage
- **Purpose**: Configuration, dependencies, future user data
- **Current**: requirements.txt
- **Future**: .env, captured_emails.json, user_preferences.json
- **When used**: Deployment, persistent storage needs
- **Rule**: No business logic, only data/config

### /web/ - Frontend Assets
- **Purpose**: Everything users see
- **Structure**: 
  - `templates/` - HTML files
  - `static/` - CSS, JS, images
- **When used**: UI changes only
- **Rule**: Frontend only, no backend logic

### /.claude/ - Tool Settings
- **Purpose**: Claude Code permission cache
- **When used**: Automatically by Claude Code CLI
- **Rule**: Don't modify, let tool manage it

## Quick Navigation
- **Server changes**: Start at app.py
- **What am I doing?**: Read NOW.md
- **System design?**: Check .mind/maps/
- **Run a tool?**: Look in tools/
- **Old docs?**: Browse docs/

## File Limits
- Root: 5 files (strict!)
- Per file: 300 lines max
- Per function: 50 lines max
- Total project: <50 files target