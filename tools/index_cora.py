#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/index_cora.py
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
import sys

# Fix Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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
        # Skip hidden directories and venv
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'venv']
        
        # Skip if we're inside venv
        if 'venv' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                stats['total_files'] += 1
                path = os.path.join(root, file)
                
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        stats['total_lines'] += len(content.splitlines())
                        
                        nav_info = extract_navigation_header(content)
                        if nav_info:
                            stats['documented_files'] += 1
                            index[path] = nav_info
                except (UnicodeDecodeError, PermissionError):
                    # Skip files with encoding issues or permission errors
                    continue
    
    return index, stats

def update_indexes():
    """Update all AI navigation files"""
    print("🔍 Scanning CORA codebase...")
    index, stats = scan_codebase()
    
    # Ensure .mind/maps exists
    os.makedirs('.mind/maps', exist_ok=True)
    
    # Update master_file_registry.md - COMPACT VERSION
    with open('.mind/maps/master_file_registry.md', 'w', encoding='utf-8') as f:
        f.write("🧭 LOCATION: /CORA/.mind/maps/master_file_registry.md\n")
        f.write("🎯 PURPOSE: Compact file registry - See file_index.json for full details\n")
        f.write("🔗 RELATED: system_structure.md, ai_architecture.md\n")
        f.write("📝 TODOS: Run regularly to keep updated\n\n")
        f.write(f"# 🗺️ CORA File Registry - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"## Statistics\n")
        f.write(f"- Total Python Files: {stats['total_files']}\n")
        f.write(f"- Total Lines: {stats['total_lines']}\n")
        f.write(f"- Documentation Coverage: {stats['documented_files']/max(stats['total_files'],1)*100:.1f}%\n\n")
        
        f.write("## Key Files by Category\n\n")
        
        # Group files by category based on directory
        categories = {}
        for path, info in index.items():
            if not info:
                continue
            
            # Determine category based on path
            if path.startswith('.\\routes\\') or path.startswith('./routes/'):
                category = 'Routes'
            elif path.startswith('.\\models\\') or path.startswith('./models/'):
                category = 'Models'
            elif path.startswith('.\\tools\\') or path.startswith('./tools/'):
                category = 'Tools'
            elif path.startswith('.\\tests\\') or path.startswith('./tests/'):
                category = 'Tests'
            elif path.startswith('.\\migrations\\') or path.startswith('./migrations/'):
                category = 'Migrations'
            elif path == '.\\app.py' or path == './app.py':
                category = 'Core'
            else:
                category = 'Other'
            
            if category not in categories:
                categories[category] = []
            categories[category].append((path, info))
        
        line_count = 12  # Header lines
        
        # Write categories in priority order
        priority_order = ['Core', 'Routes', 'Models', 'Tools', 'Tests', 'Migrations', 'Other']
        for category in priority_order:
            if category not in categories:
                continue
                
            f.write(f"### {category}\n")
            line_count += 1
            
            # Sort files within category
            for path, info in sorted(categories[category]):
                if line_count < 300:  # Keep under 320 lines
                    purpose = info['purpose'][:60] + '...' if len(info['purpose']) > 60 else info['purpose']
                    f.write(f"- `{path}`: {purpose}\n")
                    line_count += 1
            
            f.write("\n")
            line_count += 1
            
            if line_count >= 300:
                f.write("*[Truncated - see file_index.json for complete listing]*\n")
                break
    
    # Update JSON index for programmatic access
    with open('.mind/maps/file_index.json', 'w', encoding='utf-8') as f:
        json.dump({
            'generated': datetime.datetime.now().isoformat(),
            'stats': stats,
            'files': index
        }, f, indent=2)
    
    # Add note about full index
    with open('.mind/maps/master_file_registry.md', 'a', encoding='utf-8') as f:
        f.write("\n## 📚 Full Index\n\n")
        f.write("For complete file details including imports/exports, see:\n")
        f.write("- JSON: `.mind/maps/file_index.json`\n")
        f.write("- Run `python tools/index_cora.py` to regenerate\n")
    
    print(f"✅ Indexed {stats['total_files']} files")
    print(f"📊 Documentation coverage: {stats['documented_files']/max(stats['total_files'],1)*100:.1f}%")
    print(f"📁 Updated .mind/maps/master_file_registry.md")
    print(f"💾 JSON index at .mind/maps/file_index.json")

if __name__ == "__main__":
    update_indexes()