# 🎮 CORA Command Keywords

## Core Commands

### 💾 "save"  
**What:** Checkpoint significant progress to .mind/today/session.md
**When:** After completing something meaningful

### 📍 "hydrate"
**What:** Refresh my context by re-reading key files
**When:** During long sessions when context feels lost

### 📊 "status"
**What:** Quick health check of the system
**When:** Want to know if everything's okay

## Tool Commands

### 📏 "check sizes"
**What:** Run file size analysis
**Tool:** `python tools/check_sizes.py`

### 🗄️ "archive"
**What:** Archive today's work and split large files
**Tool:** `python tools/auto_archive.py --daily`

### 🚀 "start"
**What:** Start the development server
**Tool:** `python tools/start_cora.py`

### 🔄 "commit"
**What:** Smart git commit with context
**Tool:** `python tools/git_smart.py "message"`

### 🏥 "health"
**What:** Full system health analysis  
**Tool:** `python tools/health_check.py`

### 🗺️ "index"
**What:** Rebuild system maps
**Tool:** `python tools/index_cora.py`

## Usage
Just say the keyword. I'll recognize it and run the full action sequence.

## Examples
- "Let's hydrate" → Full context refresh
- "Save" → Checkpoint progress
- "Status check" → System health
- "Focus?" → Current task reminder