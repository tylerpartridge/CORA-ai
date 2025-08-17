#!/usr/bin/env python3
"""
Safe Refactoring Tracker
Tracks what's been cleaned up and what's left to do
"""

import os
import re
from pathlib import Path
from datetime import datetime

def count_todos(directory="routes"):
    """Count TODO comments in Python files"""
    todo_count = 0
    files_with_todos = []
    
    for file_path in Path(directory).glob("*.py"):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            todos = re.findall(r'#.*TODO:', content)
            if todos:
                todo_count += len(todos)
                files_with_todos.append((file_path.name, len(todos)))
    
    return todo_count, sorted(files_with_todos, key=lambda x: x[1], reverse=True)

def count_commented_code(directory="routes"):
    """Count lines of commented-out code"""
    commented_lines = 0
    pattern = re.compile(r'^\s*#\s*(if |for |while |def |class |import |from |return |print|await |async )', re.MULTILINE)
    
    for file_path in Path(directory).glob("*.py"):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            matches = pattern.findall(content)
            commented_lines += len(matches)
    
    return commented_lines

def count_duplicate_files(directory="routes"):
    """Count potential duplicate files"""
    files = list(Path(directory).glob("*.py"))
    duplicates = []
    
    # Look for files with similar names
    for file in files:
        base_name = file.stem
        # Check for v2, v3, _old, _new, _optimized, _enhanced variations
        for other in files:
            if other != file:
                other_base = other.stem
                if (base_name in other_base or other_base in base_name) and \
                   any(suffix in other_base.lower() for suffix in ['v2', 'v3', 'old', 'new', 'optimized', 'enhanced', 'test', 'backup']):
                    if (base_name, other_base) not in duplicates and (other_base, base_name) not in duplicates:
                        duplicates.append((base_name, other_base))
    
    return duplicates

def generate_report():
    """Generate refactoring progress report"""
    report = f"""
# Refactoring Progress Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Routes Directory Analysis

### TODOs
"""
    
    todo_count, files_with_todos = count_todos()
    report += f"Total TODO comments: {todo_count}\n\n"
    if files_with_todos:
        report += "Files with TODOs:\n"
        for file, count in files_with_todos[:5]:
            report += f"  - {file}: {count} TODOs\n"
    
    report += f"\n### Commented Code\n"
    commented = count_commented_code()
    report += f"Lines of commented-out code: {commented}\n"
    
    report += f"\n### Potential Duplicates\n"
    duplicates = count_duplicate_files()
    if duplicates:
        report += f"Found {len(duplicates)} potential duplicate pairs:\n"
        for orig, dup in duplicates[:5]:
            report += f"  - {orig} <-> {dup}\n"
    else:
        report += "No obvious duplicates found\n"
    
    # Check deprecated folder
    deprecated_path = Path("routes/deprecated")
    if deprecated_path.exists():
        deprecated_files = list(deprecated_path.glob("*.py"))
        report += f"\n### Already Cleaned\n"
        report += f"Files moved to deprecated: {len(deprecated_files)}\n"
        for file in deprecated_files:
            report += f"  - {file.name}\n"
    
    return report

if __name__ == "__main__":
    print(generate_report())