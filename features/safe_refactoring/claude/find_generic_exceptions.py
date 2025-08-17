#!/usr/bin/env python3
"""
Find all generic exception handlers that might be hiding real problems
"""

import ast
import os
from pathlib import Path

class GenericExceptionFinder(ast.NodeVisitor):
    def __init__(self, filepath):
        self.filepath = filepath
        self.generic_handlers = []
        
    def visit_ExceptHandler(self, node):
        # Check for bare except or except Exception
        if node.type is None:  # bare except:
            self.generic_handlers.append({
                'line': node.lineno,
                'type': 'bare_except',
                'file': self.filepath
            })
        elif isinstance(node.type, ast.Name):
            if node.type.id in ['Exception', 'BaseException']:
                # Check if it just passes or has minimal handling
                if len(node.body) == 1:
                    stmt = node.body[0]
                    if isinstance(stmt, ast.Pass):
                        self.generic_handlers.append({
                            'line': node.lineno,
                            'type': 'exception_pass',
                            'file': self.filepath
                        })
                    elif isinstance(stmt, ast.Expr):
                        # Check for print or logger without re-raising
                        self.generic_handlers.append({
                            'line': node.lineno,
                            'type': 'exception_minimal',
                            'file': self.filepath
                        })
        self.generic_visit(node)

def find_generic_exceptions(filepath):
    """Find generic exception handlers in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        finder = GenericExceptionFinder(filepath)
        finder.visit(tree)
        return finder.generic_handlers
    except Exception:
        return []

def main():
    print("Generic Exception Handler Finder")
    print("=" * 60)
    
    # Directories to check
    dirs_to_check = ['routes', 'services', 'models', 'utils', 'middleware']
    
    all_handlers = []
    files_checked = 0
    
    for dir_name in dirs_to_check:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            continue
            
        for py_file in dir_path.glob('*.py'):
            files_checked += 1
            handlers = find_generic_exceptions(py_file)
            all_handlers.extend(handlers)
    
    # Also check root py files
    for py_file in Path('.').glob('*.py'):
        if py_file.name not in ['setup.py', 'conftest.py']:
            files_checked += 1
            handlers = find_generic_exceptions(py_file)
            all_handlers.extend(handlers)
    
    print(f"Checked {files_checked} files")
    print(f"Found {len(all_handlers)} generic exception handlers\n")
    
    # Group by file
    by_file = {}
    for handler in all_handlers:
        filepath = handler['file']
        if filepath not in by_file:
            by_file[filepath] = []
        by_file[filepath].append(handler)
    
    # Sort by most problematic files
    sorted_files = sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)
    
    print("Top Offenders:")
    print("-" * 40)
    
    for filepath, handlers in sorted_files[:10]:
        print(f"\n{filepath}: {len(handlers)} generic handlers")
        
        # Show first few line numbers
        lines = [str(h['line']) for h in handlers[:5]]
        if len(handlers) > 5:
            lines.append(f"... +{len(handlers)-5} more")
        print(f"  Lines: {', '.join(lines)}")
        
        # Count types
        types = {}
        for h in handlers:
            types[h['type']] = types.get(h['type'], 0) + 1
        print(f"  Types: {types}")
    
    # Priority files to fix (routes that handle frontend)
    print("\n" + "=" * 60)
    print("PRIORITY FILES (Frontend-facing routes):")
    print("-" * 40)
    
    priority_files = [
        'routes/pages.py',
        'routes/auth_coordinator.py', 
        'routes/dashboard_routes.py',
        'routes/expenses.py',
        'routes/api_status.py',
        'app.py'
    ]
    
    for pf in priority_files:
        pf_path = Path(pf)
        if pf_path in by_file:
            handlers = by_file[pf_path]
            print(f"\n{pf}: {len(handlers)} handlers")
            for h in handlers[:3]:
                print(f"  Line {h['line']}: {h['type']}")
    
    return all_handlers

if __name__ == "__main__":
    handlers = main()
    
    # Create a fix script
    if handlers:
        print("\n" + "=" * 60)
        print("Creating fix script...")
        
        script_path = Path('features/safe_refactoring/claude/fix_exceptions.py')
        with open(script_path, 'w') as f:
            f.write('#!/usr/bin/env python3\n')
            f.write('"""Fix generic exception handlers"""\n\n')
            f.write('# Files to fix with line numbers:\n')
            f.write('FILES_TO_FIX = [\n')
            
            by_file = {}
            for h in handlers:
                if h['file'] not in by_file:
                    by_file[h['file']] = []
                by_file[h['file']].append(h['line'])
            
            for filepath, lines in by_file.items():
                f.write(f'    ("{filepath}", {sorted(lines)}),\n')
            
            f.write(']\n\n')
            f.write('print("Files that need exception handler fixes:")\n')
            f.write('for filepath, lines in FILES_TO_FIX:\n')
            f.write('    print(f"{filepath}: lines {lines}")\n')
        
        print(f"Fix script created: {script_path}")