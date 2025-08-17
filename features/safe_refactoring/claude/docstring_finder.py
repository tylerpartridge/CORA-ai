#!/usr/bin/env python3
"""
Find functions without docstrings in Python files
"""

import ast
from pathlib import Path

def find_undocumented_functions(filepath):
    """Find functions without docstrings in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        tree = ast.parse(content)
        undocumented = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function has a docstring
                has_docstring = (
                    node.body and 
                    isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)
                )
                
                if not has_docstring and not node.name.startswith('_'):
                    undocumented.append({
                        'name': node.name,
                        'line': node.lineno
                    })
        
        return undocumented
    except:
        return []

def scan_routes():
    """Scan route files for undocumented functions"""
    results = {}
    
    for filepath in Path('routes').glob('*.py'):
        undocumented = find_undocumented_functions(filepath)
        if undocumented:
            results[str(filepath)] = undocumented
    
    return results

if __name__ == "__main__":
    print("Scanning for undocumented functions in routes/...\n")
    
    results = scan_routes()
    
    if results:
        # Sort by most undocumented
        sorted_files = sorted(results.items(), key=lambda x: len(x[1]), reverse=True)
        
        print(f"Found {len(results)} files with undocumented functions:\n")
        
        for filepath, funcs in sorted_files[:5]:
            print(f"File: {filepath} ({len(funcs)} undocumented)")
            for func in funcs[:3]:
                print(f"   - {func['name']} (line {func['line']})")
            if len(funcs) > 3:
                print(f"   ... and {len(funcs) - 3} more")
            print()
    else:
        print("All functions have docstrings!")