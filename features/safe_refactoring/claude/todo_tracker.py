#!/usr/bin/env python3
"""
TODO Tracking System for CORA
Finds and categorizes all TODO comments in the codebase
Safe, read-only analysis tool
"""

import re
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class TodoTracker:
    def __init__(self):
        self.todos = []
        self.categories = defaultdict(list)
        
    def scan_file(self, filepath):
        """Scan a single file for TODOs"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                # Look for TODO, FIXME, XXX, HACK comments
                if re.search(r'#.*?(TODO|FIXME|XXX|HACK):?\s*(.*)', line):
                    match = re.search(r'#.*?(TODO|FIXME|XXX|HACK):?\s*(.*)', line)
                    if match:
                        todo_type = match.group(1)
                        todo_text = match.group(2).strip()
                        
                        # Categorize by priority
                        priority = self.determine_priority(todo_text, todo_type)
                        
                        todo_item = {
                            'file': str(filepath),
                            'line': line_num,
                            'type': todo_type,
                            'text': todo_text,
                            'priority': priority
                        }
                        
                        self.todos.append(todo_item)
                        self.categories[todo_type].append(todo_item)
                        
        except Exception as e:
            pass  # Skip files that can't be read
    
    def determine_priority(self, text, todo_type):
        """Determine priority based on keywords"""
        text_lower = text.lower()
        
        # High priority keywords
        if any(word in text_lower for word in ['critical', 'urgent', 'security', 'bug', 'broken', 'fix']):
            return 'HIGH'
        
        # FIXME and HACK are usually higher priority
        if todo_type in ['FIXME', 'HACK']:
            return 'MEDIUM'
        
        # Low priority keywords
        if any(word in text_lower for word in ['later', 'maybe', 'consider', 'enhance', 'refactor']):
            return 'LOW'
        
        return 'MEDIUM'
    
    def scan_directory(self, directory='.'):
        """Scan entire directory for TODOs"""
        for filepath in Path(directory).rglob('*.py'):
            # Skip test files and our own tracking tools
            if 'test' in str(filepath).lower() or 'safe_refactoring' in str(filepath):
                continue
            self.scan_file(filepath)
    
    def generate_report(self):
        """Generate a formatted TODO report"""
        if not self.todos:
            return "No TODOs found!"
        
        # Sort by priority
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        sorted_todos = sorted(self.todos, key=lambda x: priority_order[x['priority']])
        
        report = f"""# TODO Tracking Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Total TODOs: {len(self.todos)}

## Summary by Type:
"""
        for todo_type, items in self.categories.items():
            report += f"- {todo_type}: {len(items)} items\n"
        
        report += "\n## By Priority:\n"
        
        # Group by priority
        by_priority = defaultdict(list)
        for todo in sorted_todos:
            by_priority[todo['priority']].append(todo)
        
        for priority in ['HIGH', 'MEDIUM', 'LOW']:
            if priority in by_priority:
                report += f"\n### {priority} Priority ({len(by_priority[priority])} items)\n"
                for todo in by_priority[priority][:5]:  # Show top 5 per category
                    report += f"- **{Path(todo['file']).name}:{todo['line']}** - {todo['text'][:80]}\n"
        
        # Files with most TODOs
        file_counts = defaultdict(int)
        for todo in self.todos:
            file_counts[todo['file']] += 1
        
        report += "\n## Files with Most TODOs:\n"
        for filepath, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            report += f"- {Path(filepath).name}: {count} TODOs\n"
        
        return report
    
    def generate_actionable_list(self):
        """Generate list of actionable TODOs that can be fixed"""
        actionable = []
        
        for todo in self.todos:
            # Look for specific patterns that are fixable
            text = todo['text'].lower()
            
            if 'add' in text or 'implement' in text or 'create' in text:
                actionable.append({
                    **todo,
                    'action': 'IMPLEMENT'
                })
            elif 'fix' in text or 'broken' in text or 'bug' in text:
                actionable.append({
                    **todo,
                    'action': 'FIX'
                })
            elif 'remove' in text or 'delete' in text or 'clean' in text:
                actionable.append({
                    **todo,
                    'action': 'CLEANUP'
                })
        
        return actionable

if __name__ == "__main__":
    print("Scanning for TODOs in CORA codebase...\n")
    
    tracker = TodoTracker()
    tracker.scan_directory('.')
    
    # Generate and print report
    report = tracker.generate_report()
    print(report)
    
    # Save report to file
    with open('features/safe_refactoring/claude/TODO_REPORT.md', 'w') as f:
        f.write(report)
    
    print("\nReport saved to TODO_REPORT.md")
    
    # Generate actionable list
    actionable = tracker.generate_actionable_list()
    if actionable:
        print(f"\nFound {len(actionable)} actionable TODOs that could be addressed.")