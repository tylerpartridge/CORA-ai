#!/usr/bin/env python3
"""
Find potentially unused imports in Python files
Safe approach - only reports obvious cases
"""

import ast
from pathlib import Path

def find_unused_imports(filename):
    """Find imports that appear unused in a file"""
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Get all imports
        imports = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imports[name] = alias.name
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imports[name] = f"{node.module}.{alias.name}" if node.module else alias.name
        
        # Check which are used
        unused = []
        for import_name in imports:
            # Simple check - is the name referenced in the code?
            # Skip the import lines themselves
            lines = content.split('\n')
            found = False
            for line in lines:
                # Skip import lines
                if 'import ' in line and import_name in line:
                    continue
                # Check if used
                if import_name in line:
                    found = True
                    break
            
            if not found:
                unused.append(import_name)
        
        return unused
    except Exception as e:
        return []

def analyze_file(filepath):
    """Analyze a single file for unused imports"""
    unused = find_unused_imports(filepath)
    if unused:
        return {
            'file': filepath,
            'unused': unused,
            'count': len(unused)
        }
    return None

def scan_directory(directory="routes"):
    """Scan directory for unused imports"""
    results = []
    
    for filepath in Path(directory).glob("*.py"):
        result = analyze_file(filepath)
        if result:
            results.append(result)
    
    return sorted(results, key=lambda x: x['count'], reverse=True)

if __name__ == "__main__":
    print("Scanning for unused imports in routes/...\n")
    
    results = scan_directory("routes")
    
    if results:
        print(f"Found {len(results)} files with potentially unused imports:\n")
        
        # Show top 5
        for result in results[:5]:
            print(f"File: {result['file']}")
            print(f"   Unused ({result['count']}): {', '.join(result['unused'])}\n")
    else:
        print("No obvious unused imports found!")
    
    print("\n⚠️ Note: This is a simple check. Some imports may be used in ways not detected.")