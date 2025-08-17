#!/usr/bin/env python3
"""
TODO Tracker for CORA's own code only
Excludes dependencies and third-party libraries
"""

import re
from pathlib import Path
from datetime import datetime

def find_cora_todos():
    """Find TODOs only in CORA's own code"""
    todos = []
    
    # Directories to scan (CORA's code only)
    cora_dirs = ['routes', 'services', 'models', 'utils', 'middleware', 'dependencies']
    
    for dir_name in cora_dirs:
        if not Path(dir_name).exists():
            continue
            
        for filepath in Path(dir_name).glob('*.py'):
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    if 'TODO:' in line or '# TODO' in line:
                        # Extract TODO text
                        match = re.search(r'#\s*TODO:?\s*(.*)', line)
                        if match:
                            todo_text = match.group(1).strip()
                            todos.append({
                                'file': f"{dir_name}/{filepath.name}",
                                'line': line_num,
                                'text': todo_text
                            })
            except:
                pass
    
    # Also check app.py
    if Path('app.py').exists():
        try:
            with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                if 'TODO:' in line or '# TODO' in line:
                    match = re.search(r'#\s*TODO:?\s*(.*)', line)
                    if match:
                        todo_text = match.group(1).strip()
                        todos.append({
                            'file': 'app.py',
                            'line': line_num,
                            'text': todo_text
                        })
        except:
            pass
    
    return todos

def generate_cora_report(todos):
    """Generate report for CORA TODOs only"""
    report = f"""# CORA TODO Report (Core Code Only)
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Total TODOs in CORA code: {len(todos)}

## TODOs by File:
"""
    
    # Group by file
    by_file = {}
    for todo in todos:
        file = todo['file']
        if file not in by_file:
            by_file[file] = []
        by_file[file].append(todo)
    
    # Sort by most TODOs
    sorted_files = sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)
    
    for file, file_todos in sorted_files:
        report += f"\n### {file} ({len(file_todos)} TODOs)\n"
        for todo in file_todos[:3]:  # Show first 3 per file
            report += f"- Line {todo['line']}: {todo['text'][:100]}\n"
        if len(file_todos) > 3:
            report += f"- ... and {len(file_todos) - 3} more\n"
    
    # Categorize by content
    report += "\n## Categories:\n"
    
    payment_todos = [t for t in todos if 'payment' in t['text'].lower() or 'stripe' in t['text'].lower()]
    integration_todos = [t for t in todos if 'integration' in t['text'].lower() or 'api' in t['text'].lower()]
    security_todos = [t for t in todos if 'security' in t['text'].lower() or 'auth' in t['text'].lower()]
    
    if payment_todos:
        report += f"\n### Payment-related ({len(payment_todos)} TODOs)\n"
        for todo in payment_todos[:3]:
            report += f"- {todo['file']}:{todo['line']} - {todo['text'][:80]}\n"
    
    if integration_todos:
        report += f"\n### Integration-related ({len(integration_todos)} TODOs)\n"
        for todo in integration_todos[:3]:
            report += f"- {todo['file']}:{todo['line']} - {todo['text'][:80]}\n"
    
    if security_todos:
        report += f"\n### Security-related ({len(security_todos)} TODOs)\n"
        for todo in security_todos[:3]:
            report += f"- {todo['file']}:{todo['line']} - {todo['text'][:80]}\n"
    
    return report

if __name__ == "__main__":
    print("Scanning CORA's own code for TODOs...\n")
    
    todos = find_cora_todos()
    report = generate_cora_report(todos)
    
    print(report)
    
    # Save report
    with open('features/safe_refactoring/claude/CORA_TODO_REPORT.md', 'w') as f:
        f.write(report)
    
    print(f"\nReport saved. Found {len(todos)} TODOs in CORA's code.")