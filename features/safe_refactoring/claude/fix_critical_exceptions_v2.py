#!/usr/bin/env python3
"""
Fix critical exception handlers in frontend routes - Version 2
Adds proper logging to see what errors were being hidden
"""

from pathlib import Path
import re

def fix_auth_coordinator():
    """Fix exception handlers in auth_coordinator.py"""
    filepath = Path('routes/auth_coordinator.py')
    
    if not filepath.exists():
        print(f"[ERROR] {filepath} not found")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = []
    
    # Fix line 268: Email sending exception
    old_pattern1 = r'except Exception as e:\s*\n\s*# Log email failure but don\'t fail registration\s*\n\s*print\(f"Failed to send welcome email'
    new_pattern1 = '''except Exception as e:
            # Log email failure but don't fail registration
            import logging
            logging.error(f"Welcome email failed for {user.email}: {e}", exc_info=True)
            print(f"Failed to send welcome email'''
    
    if old_pattern1 in content:
        content = content.replace(
            "except Exception as e:\n            # Log email failure but don't fail registration\n            print(f\"Failed to send welcome email",
            new_pattern1
        )
        changes.append("Line 268: Added proper logging for welcome email failures")
    
    # Fix line 467: Password reset email exception
    old_pattern2 = 'print(f"Failed to send password reset email to {request.email}: {str(e)}")'
    new_pattern2 = '''import logging
                logging.error(f"Password reset email failed for {request.email}: {e}", exc_info=True)
                print(f"Failed to send password reset email to {request.email}: {str(e)}")'''
    
    if old_pattern2 in content:
        content = content.replace(
            '            except Exception as e:\n                print(f"Failed to send password reset email',
            '            except Exception as e:\n                import logging\n                logging.error(f"Password reset email failed for {request.email}: {e}", exc_info=True)\n                print(f"Failed to send password reset email'
        )
        changes.append("Line 467: Added proper logging for password reset email failures")
    
    if content != original:
        # Backup original
        backup = filepath.with_suffix('.py.exception_backup_v2')
        with open(backup, 'w', encoding='utf-8') as f:
            f.write(original)
        
        # Write fixed version
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[FIXED] {filepath}")
        for change in changes:
            print(f"  - {change}")
        print(f"  Backup: {backup}")
        return True
    else:
        print(f"[SKIP] {filepath} - no changes needed")
        return False

def fix_expenses():
    """Fix exception handlers in expenses.py"""
    filepath = Path('routes/expenses.py')
    
    if not filepath.exists():
        print(f"[ERROR] {filepath} not found")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = []
    
    # Add logging import if not present
    if 'import logging' not in content:
        # Add after other imports
        content = content.replace('import json', 'import json\nimport logging')
        changes.append("Added logging import")
    
    # Fix cache get error (line 179)
    old_cache_get = 'except Exception as e:\n        print(f"Cache get error: {e}")'
    new_cache_get = '''except Exception as e:
        logging.warning(f"Cache get error for key {cache_key}: {e}")
        print(f"Cache get error: {e}")'''
    
    if old_cache_get in content:
        content = content.replace(old_cache_get, new_cache_get)
        changes.append("Line 179: Added logging for cache get errors")
    
    # Fix cache set error (line 188)
    old_cache_set = 'except Exception as e:\n        print(f"Cache set error: {e}")'
    new_cache_set = '''except Exception as e:
        logging.warning(f"Cache set error for key {cache_key}: {e}")
        print(f"Cache set error: {e}")'''
    
    if old_cache_set in content:
        content = content.replace(old_cache_set, new_cache_set)
        changes.append("Line 188: Added logging for cache set errors")
    
    # Fix cache invalidation error (line 197)
    old_cache_inv = 'except Exception as e:\n        print(f"Cache invalidation error: {e}")'
    new_cache_inv = '''except Exception as e:
        logging.warning(f"Cache invalidation error for user {user_email}: {e}")
        print(f"Cache invalidation error: {e}")'''
    
    if old_cache_inv in content:
        content = content.replace(old_cache_inv, new_cache_inv)
        changes.append("Line 197: Added logging for cache invalidation errors")
    
    if content != original:
        # Backup
        backup = filepath.with_suffix('.py.exception_backup_v2')
        with open(backup, 'w', encoding='utf-8') as f:
            f.write(original)
        
        # Write fixed
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[FIXED] {filepath}")
        for change in changes:
            print(f"  - {change}")
        print(f"  Backup: {backup}")
        return True
    else:
        print(f"[SKIP] {filepath} - no changes needed")
        return False

def fix_voice_commands():
    """Fix bare except handlers in voice_commands.py"""
    filepath = Path('routes/voice_commands.py')
    
    if not filepath.exists():
        print(f"[ERROR] {filepath} not found")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Lines with bare except: 95, 128, 161
    problem_lines = [95, 128, 161]
    changes = []
    
    for line_num in problem_lines:
        if line_num <= len(lines):
            idx = line_num - 1
            if 'except:' in lines[idx]:
                # Replace bare except with specific exception
                indent = len(lines[idx]) - len(lines[idx].lstrip())
                lines[idx] = ' ' * indent + 'except Exception as e:\n'
                
                # Add logging on next line
                if idx + 1 < len(lines):
                    next_indent = indent + 4
                    log_line = ' ' * next_indent + 'import logging\n'
                    log_line += ' ' * next_indent + f'logging.error(f"Voice command error at line {line_num}: {{e}}", exc_info=True)\n'
                    lines.insert(idx + 1, log_line)
                    changes.append(f"Line {line_num}: Replaced bare except with logged exception")
    
    if changes:
        # Backup
        backup = filepath.with_suffix('.py.exception_backup_v2')
        with open(backup, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # Write fixed
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"[FIXED] {filepath}")
        for change in changes:
            print(f"  - {change}")
        print(f"  Backup: {backup}")
        return True
    else:
        print(f"[SKIP] {filepath} - no changes needed")
        return False

def main():
    print("Critical Exception Handler Fixes - Version 2")
    print("=" * 60)
    print("Adding proper logging to see hidden errors...\n")
    
    fixed = 0
    
    # Fix the most critical routes
    print("1. Fixing routes/auth_coordinator.py...")
    if fix_auth_coordinator():
        fixed += 1
    
    print("\n2. Fixing routes/expenses.py...")
    if fix_expenses():
        fixed += 1
    
    print("\n3. Fixing routes/voice_commands.py...")
    if fix_voice_commands():
        fixed += 1
    
    print("\n" + "=" * 60)
    print(f"Fixed {fixed} files")
    
    if fixed > 0:
        print("\n[IMPORTANT] Exception handlers now log errors properly")
        print("You can now see what errors were being hidden!")
        print("\nTo monitor errors in real-time:")
        print("  # Python logging output")
        print("  tail -f cora.log")
        print("\n  # Or watch console when running server")
        print("  python app.py 2>&1 | grep -E '(ERROR|WARNING)'")
        
        print("\n[NEXT STEPS]")
        print("1. Restart the server to see new error logs")
        print("2. Check logs to identify hidden issues")
        print("3. Fix root causes of exceptions")
        print("4. Gradually upgrade remaining 90+ exception handlers")

if __name__ == "__main__":
    main()