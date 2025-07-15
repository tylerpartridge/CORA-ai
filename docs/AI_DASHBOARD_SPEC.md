# 🎯 AI_DASHBOARD.md Specification

## Goal: 30-Second Absolute Awareness

### Design Principles
1. **Information Hierarchy**: Most critical info first
2. **Scannable**: Use visual markers, short lines
3. **Actionable**: Every section leads to action
4. **Fresh**: Auto-generated, never stale
5. **Complete**: Everything needed, nothing more

## Dashboard Structure

```markdown
# 🤖 AI Assistant Dashboard
Generated: 2025-01-12 14:30:00 | Session: #42 | Health: 🟢

## 🎯 FOCUS NOW
> Building user authentication flow in /routes/auth.py

## 🚨 BLOCKERS (Fix First!)
1. ❌ ImportError in auth_routes.py:45 - missing 'validate_token'
2. ⚠️  File size violation: dashboard_analytics.py (318/300 lines)

## 📊 SYSTEM PULSE
- Health: 🟢 Good (2 minor issues)
- Files: 737 total, 2 violations
- Tests: 45/48 passing
- Git: 50 uncommitted changes
- Last Success: 2 hours ago

## 🗺️ INSTANT NAVIGATION
| Need To... | Go To... | Command |
|------------|----------|---------|
| See current work | NOW.md | `cat NOW.md` |
| Check priorities | NEXT.md | `cat NEXT.md` |
| Find user routes | /routes/ | `ls routes/` |
| Run tests | | `python -m pytest` |
| Check sizes | | `python tools/css_health.py` |

## 📍 CONTEXT (You Are Here)
**Previous**: Fixed 26,712 file sprawl (99.99% reduction)
**Current**: Implementing AI awareness system
**Next**: User authentication improvements
**Vision**: Self-aware AI-friendly codebase

## 🧠 QUICK DECISIONS
- Architecture pattern: MVC with service layer
- Testing approach: Pytest with mocks
- File size limit: 300 lines strict
- Git strategy: Feature branches

## 🔄 RECENT ACTIVITY (Last 24h)
- ✅ Removed backup sprawl system
- ✅ Implemented NO_TOOL_BACKUPS policy
- 🔄 Started AI awareness project
- 📝 Created collaboration protocol

## 💡 AI COMMANDS
`python tools/ai_awareness.py`        # Full context load
`python tools/ai_handoff.py`          # See previous AI's work  
`python tools/ai_navigate.py [query]` # Find anything fast
`./refresh_dashboard.sh`              # Update this dashboard

## ⚡ QUICK START
1. Read this dashboard (✓ you are here)
2. Check blockers above
3. Continue current focus
4. Update NOW.md when switching tasks
```

## Generation Requirements

The dashboard generator (`tools/ai_dashboard_generator.py`) should:

### 1. Data Collection (Parallel)
- Read NOW.md for current focus
- Run health check for system status
- Check git status for changes
- Scan for file size violations
- Look for failing tests
- Extract recent git commits

### 2. Intelligence Features
- **Blocker Detection**: Scan for errors, broken imports, failing tests
- **Smart Navigation**: Most-used directories based on recent activity
- **Context Building**: Read session logs for previous/next
- **Decision Memory**: Extract patterns from codebase

### 3. Performance Targets
- Generate in <2 seconds
- Read maximum 10 files
- Output <100 lines
- Cache stable data (refresh every hour)

### 4. Auto-Generation Triggers
- On session start (bootup)
- On major git operations
- On request (manual refresh)
- After error detection

## Implementation Checklist for Cursor

```python
# tools/ai_dashboard_generator.py

class AIDashboardGenerator:
    def __init__(self):
        self.cache = {}
        
    def generate(self):
        # Parallel data collection
        data = self.collect_all_data()
        
        # Build dashboard sections
        dashboard = self.build_dashboard(data)
        
        # Write to AI_DASHBOARD.md
        self.write_dashboard(dashboard)
        
    def collect_all_data(self):
        """Collect in parallel for speed"""
        return {
            'focus': self.get_current_focus(),
            'blockers': self.detect_blockers(),
            'health': self.get_system_health(),
            'navigation': self.build_nav_map(),
            'context': self.get_context(),
            'activity': self.get_recent_activity()
        }
```

## Success Metrics
1. **Time to awareness**: <30 seconds (from 10 minutes)
2. **Files to read**: 1 (from 10-15)
3. **Accuracy**: 100% current state
4. **Actionability**: Every section has clear next step

---

Ready for implementation, Cursor! This should give us absolute awareness in one glance.