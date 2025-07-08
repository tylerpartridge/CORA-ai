#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/index_cora.py
🎯 PURPOSE: Generate fresh system index for AI navigation
🔗 IMPORTS: os, json, datetime, ast
📤 EXPORTS: scan_codebase(), update_indexes()
🔄 PATTERN: Self-documenting codebase
📝 TODOS: Add import graph visualization

Run this before each AI session to give perfect context!
"""

import os
import json
import datetime
import ast
import re

def extract_navigation_header(content):
    """Extract the navigation header from a Python file"""
    nav_pattern = r'"""[\s\S]*?🧭 LOCATION: (.*?)\n.*?🎯 PURPOSE: (.*?)\n.*?🔗 IMPORTS: (.*?)\n.*?📤 EXPORTS: (.*?)\n'
    match = re.search(nav_pattern, content)
    
    if match:
        return {
            'location': match.group(1).strip(),
            'purpose': match.group(2).strip(),
            'imports': match.group(3).strip(),
            'exports': match.group(4).strip()
        }
    return None

def scan_codebase():
    """Scan all Python files and extract navigation info"""
    index = {}
    stats = {'total_files': 0, 'total_lines': 0, 'documented_files': 0}
    
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.ai']
        
        for file in files:
            if file.endswith('.py'):
                stats['total_files'] += 1
                path = os.path.join(root, file)
                
                with open(path, 'r') as f:
                    content = f.read()
                    stats['total_lines'] += len(content.splitlines())
                    
                    nav_info = extract_navigation_header(content)
                    if nav_info:
                        stats['documented_files'] += 1
                        index[path] = nav_info
    
    return index, stats

def update_indexes():
    """Update all AI navigation files"""
    print("🔍 Scanning CORA codebase...")
    index, stats = scan_codebase()
    
    # Update SYSTEM_MAP.md
    with open('.ai/SYSTEM_MAP.md', 'w') as f:
        f.write(f"# 🗺️ CORA SYSTEM MAP - Auto-Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"## Statistics\n")
        f.write(f"- Total Python Files: {stats['total_files']}\n")
        f.write(f"- Total Lines: {stats['total_lines']}\n")
        f.write(f"- Files with Navigation: {stats['documented_files']}\n")
        f.write(f"- Documentation Coverage: {stats['documented_files']/max(stats['total_files'],1)*100:.1f}%\n\n")
        
        f.write("## File Directory\n\n")
        for path, info in sorted(index.items()):
            f.write(f"### `{path}`\n")
            f.write(f"- **Purpose**: {info['purpose']}\n")
            f.write(f"- **Imports**: {info['imports']}\n")
            f.write(f"- **Exports**: {info['exports']}\n\n")
    
    # Update JSON index for programmatic access
    with open('.ai/index.json', 'w') as f:
        json.dump({
            'generated': datetime.datetime.now().isoformat(),
            'stats': stats,
            'files': index
        }, f, indent=2)
    
    # Create a quick reference file
    with open('.ai/QUICK_NAV.md', 'w') as f:
        f.write("# 🚀 QUICK NAVIGATION\n\n")
        f.write("Jump to any file by purpose:\n\n")
        for path, info in sorted(index.items(), key=lambda x: x[1]['purpose']):
            f.write(f"- **{info['purpose']}** → `{path}`\n")
    
    # Update checkpoint
    with open('.ai/CHECKPOINT.md', 'a') as f:
        f.write(f"\n\n## Index Update - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"- Files indexed: {stats['total_files']}\n")
        f.write(f"- Navigation headers: {stats['documented_files']}\n")
    
    print(f"✅ Indexed {stats['total_files']} files")
    print(f"📊 Documentation coverage: {stats['documented_files']/max(stats['total_files'],1)*100:.1f}%")
    print(f"📁 Check .ai/SYSTEM_MAP.md for details")

if __name__ == "__main__":
    update_indexes()