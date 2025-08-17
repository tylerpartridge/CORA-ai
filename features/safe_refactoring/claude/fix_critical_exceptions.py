#!/usr/bin/env python3
"""
Fix critical exception handlers in frontend routes
These could be hiding real problems
"""

from pathlib import Path
import re

def fix_pages_routes():
    """Fix exception handlers in pages.py"""
    filepath = Path('routes/pages.py')
    
    if not filepath.exists():
        print(f"[ERROR] {filepath} not found")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix pattern 1: bare except that redirects to login
    # Replace with specific exception handling
    pattern1 = r'(\s+)except:\s*\n\s*#.*auth fails.*\n\s*return RedirectResponse'
    replacement1 = r'\1except (HTTPException, AttributeError) as e:\n\1    # Log the actual error for debugging\n\1    import logging\n\1    logging.error(f"Dashboard access error: {e}")\n\1    return RedirectResponse'
    
    content = re.sub(pattern1, replacement1, content)
    
    # Fix pattern 2: generic Exception without logging
    pattern2 = r'except Exception as e:\s*\n(\s+)return'
    replacement2 = r'except Exception as e:\n\1import logging\n\1logging.error(f"Unexpected error: {e}")\n\1return'
    
    content = re.sub(pattern2, replacement2, content)
    
    if content != original:
        # Backup original
        backup = filepath.with_suffix('.py.exception_backup')
        with open(backup, 'w', encoding='utf-8') as f:
            f.write(original)
        
        # Write fixed version
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[FIXED] {filepath}")
        print(f"  Backup: {backup}")
        return True
    else:
        print(f"[SKIP] {filepath} - no changes needed")
        return False

def fix_auth_routes():
    """Fix exception handlers in auth_coordinator.py"""
    filepath = Path('routes/auth_coordinator.py')
    
    if not filepath.exists():
        print(f"[ERROR] {filepath} not found")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Known problem lines from our scan
    problem_lines = [268, 467]
    
    modified = False
    for line_num in problem_lines:
        if line_num < len(lines):
            line = lines[line_num - 1]
            
            # If it's a generic exception handler
            if 'except Exception as e:' in line:
                # Check next line for minimal handling
                if line_num < len(lines):
                    next_line = lines[line_num]
                    if 'print(' in next_line or 'pass' in next_line:
                        # Add proper logging
                        indent = len(line) - len(line.lstrip())
                        lines[line_num] = ' ' * indent + '    logger.error(f"Auth error at line {}: {e}", exc_info=True)\n'.format(line_num) + next_line
                        modified = True
                        print(f"  Fixed line {line_num}: Added proper logging")
    
    if modified:
        # Backup
        backup = filepath.with_suffix('.py.exception_backup')
        with open(backup, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # Write fixed
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"[FIXED] {filepath}")
        return True
    else:
        print(f"[SKIP] {filepath} - manual review needed")
        return False

def fix_expenses_routes():
    """Fix exception handlers in expenses.py"""
    filepath = Path('routes/expenses.py')
    
    if not filepath.exists():
        print(f"[ERROR] {filepath} not found")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Add logging import if not present
    if 'import logging' not in content:
        # Add after other imports
        content = content.replace('from typing import', 'import logging\nfrom typing import')
    
    # Fix generic exception handlers
    # Replace simple returns with logged returns
    pattern = r'except Exception as e:\s*\n(\s+)return JSONResponse\(status_code=500'
    replacement = r'except Exception as e:\n\1logging.error(f"Expense route error: {e}", exc_info=True)\n\1return JSONResponse(status_code=500'
    
    content = re.sub(pattern, replacement, content)
    
    if content != original:
        # Backup
        backup = filepath.with_suffix('.py.exception_backup')
        with open(backup, 'w', encoding='utf-8') as f:
            f.write(original)
        
        # Write fixed
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[FIXED] {filepath}")
        return True
    else:
        print(f"[SKIP] {filepath}")
        return False

def main():
    print("Critical Exception Handler Fixes")
    print("=" * 60)
    print("Fixing frontend-facing routes that might be hiding errors...\n")
    
    fixed = 0
    
    # Fix the most critical routes
    print("1. Fixing routes/pages.py...")
    if fix_pages_routes():
        fixed += 1
    
    print("\n2. Fixing routes/auth_coordinator.py...")
    if fix_auth_routes():
        fixed += 1
    
    print("\n3. Fixing routes/expenses.py...")
    if fix_expenses_routes():
        fixed += 1
    
    print("\n" + "=" * 60)
    print(f"Fixed {fixed} files")
    
    if fixed > 0:
        print("\n[IMPORTANT] Exception handlers now log errors properly")
        print("Check logs to see what errors were being hidden!")
        print("\nTo see errors in real-time:")
        print("  tail -f cora.log")
        print("  # or check console output when running server")

if __name__ == "__main__":
    main()