#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/restore_context.py
🎯 PURPOSE: Quickly restore AI context after token limit hit
🔗 IMPORTS: os, json, datetime
📤 EXPORTS: generate_context_prompt()
🔄 PATTERN: Context restoration
📝 TODOS: Add conversation history tracking

Use this when AI loses context or starting fresh session!
"""

import os
import json
import datetime

def read_ai_file(filename):
    """Safely read an AI memory file"""
    filepath = os.path.join('.ai', filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return f.read()
    return f"[Missing {filename}]"

def get_recent_changes():
    """Get recent file modifications"""
    recent = []
    now = datetime.datetime.now()
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.ai']
        
        for file in files:
            if file.endswith(('.py', '.md', '.html')):
                path = os.path.join(root, file)
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
                age = now - mtime
                
                if age.days < 1:  # Modified in last 24 hours
                    recent.append((path, mtime, age))
    
    return sorted(recent, key=lambda x: x[1], reverse=True)[:5]

def generate_context_prompt():
    """Generate a prompt to restore AI context"""
    prompt = ["# 🧠 CORA Context Restoration\n"]
    
    # ENTRY POINT FIRST (Cursor's suggestion)
    prompt.append("## 🚀 Main Entry Point")
    if os.path.exists('.entrypoint'):
        with open('.entrypoint', 'r') as f:
            prompt.append(f.read().strip())
    else:
        prompt.append("Main server: app.py")
    prompt.append("\n")
    
    # Recommended reading order
    prompt.append("## 📖 Recommended Reading Order")
    prompt.append("1. .entrypoint - Find main server")
    prompt.append("2. .ai/CURRENT_FOCUS.md - What we're doing")
    prompt.append("3. .ai/SYSTEM_MAP.md - Where files are")
    prompt.append("4. .ai/CONVENTIONS.md - How to code")
    prompt.append("5. app.py - Check navigation header")
    prompt.append("\n")
    
    # Current focus
    prompt.append("## Current Status")
    prompt.append(read_ai_file('CURRENT_FOCUS.md'))
    prompt.append("\n")
    
    # Key conventions
    prompt.append("## Key Rules")
    prompt.append("1. One file = one purpose")
    prompt.append("2. Keep files under 300 lines")
    prompt.append("3. No utils.py or helpers.py")
    prompt.append("4. Read navigation headers (🧭)")
    prompt.append("5. Update .ai/CHECKPOINT.md after changes")
    prompt.append("\n")
    
    # Recent activity
    prompt.append("## Recent Changes")
    recent = get_recent_changes()
    if recent:
        for path, mtime, age in recent:
            hours_ago = int(age.total_seconds() / 3600)
            prompt.append(f"- {path} (modified {hours_ago}h ago)")
    else:
        prompt.append("- No recent changes")
    prompt.append("\n")
    
    # Quick stats
    if os.path.exists('.ai/index.json'):
        with open('.ai/index.json', 'r') as f:
            index = json.load(f)
            stats = index.get('stats', {})
            prompt.append("## System Stats")
            prompt.append(f"- Total files: {stats.get('total_files', '?')}")
            prompt.append(f"- Total lines: {stats.get('total_lines', '?')}")
            prompt.append(f"- Documentation: {stats.get('documented_files', '?')}/{stats.get('total_files', '?')}")
    
    # Next steps
    prompt.append("\n## Next Steps")
    prompt.append("1. Read .ai/SYSTEM_MAP.md for file locations")
    prompt.append("2. Check app.py header for server info")
    prompt.append("3. Continue with deployment tasks")
    
    return "\n".join(prompt)

def save_context_snapshot():
    """Save current context for later restoration"""
    snapshot = {
        'timestamp': datetime.datetime.now().isoformat(),
        'focus': read_ai_file('CURRENT_FOCUS.md'),
        'recent_files': [f[0] for f in get_recent_changes()],
        'checkpoint': read_ai_file('CHECKPOINT.md')
    }
    
    snapshot_file = f".ai/snapshots/context_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs('.ai/snapshots', exist_ok=True)
    
    with open(snapshot_file, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    print(f"💾 Context saved to {snapshot_file}")

if __name__ == "__main__":
    print(generate_context_prompt())
    print("\n" + "="*50 + "\n")
    save_context_snapshot()
    print("\n✅ Context restoration prompt generated!")
    print("📋 Copy the above to restore AI context")