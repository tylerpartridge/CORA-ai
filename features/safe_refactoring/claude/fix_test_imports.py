#!/usr/bin/env python3
"""
Fix import issues in all test files
Adds proper sys.path setup to each test
"""

import os
import sys
from pathlib import Path

# Import fix to add at the beginning of each test file
IMPORT_FIX = '''import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
'''

def needs_import_fix(content):
    """Check if file already has the import fix"""
    return "sys.path.insert(0" not in content

def fix_test_file(filepath):
    """Add import fix to a test file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not needs_import_fix(content):
            print(f"[SKIP] {filepath.name} - already fixed")
            return False
        
        # Find where to insert the fix
        lines = content.split('\n')
        
        # Find the first import or after docstring
        insert_index = 0
        in_docstring = False
        docstring_count = 0
        
        for i, line in enumerate(lines):
            # Track docstrings
            if '"""' in line or "'''" in line:
                if in_docstring:
                    in_docstring = False
                    docstring_count += 1
                    if docstring_count == 1:  # After first docstring
                        insert_index = i + 1
                        break
                else:
                    in_docstring = True
            
            # If we find an import and haven't found docstring
            if not in_docstring and line.strip().startswith('import') and insert_index == 0:
                insert_index = i
                break
        
        # Insert the fix
        if insert_index > 0:
            # Add import fix before first import
            lines.insert(insert_index, '')
            lines.insert(insert_index, '# Fix import paths')
            for line in reversed(IMPORT_FIX.strip().split('\n')):
                lines.insert(insert_index, line)
            lines.insert(insert_index, '')
        else:
            # Add after shebang/encoding
            start_index = 0
            if lines[0].startswith('#!'):
                start_index = 1
            if start_index < len(lines) and lines[start_index].startswith('# -*- coding'):
                start_index += 1
            
            lines.insert(start_index, '')
            for line in IMPORT_FIX.strip().split('\n'):
                start_index += 1
                lines.insert(start_index, line)
            lines.insert(start_index + 1, '')
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"[FIXED] {filepath.name}")
        return True
        
    except Exception as e:
        print(f"[ERROR] {filepath.name}: {e}")
        return False

def main():
    print("Test Import Fixer")
    print("=" * 60)
    
    # Find all test files
    test_dir = Path("tests")
    test_files = list(test_dir.glob("test_*.py"))
    
    # Also check for test files in root
    root_tests = list(Path(".").glob("test_*.py"))
    test_files.extend(root_tests)
    
    print(f"Found {len(test_files)} test files\n")
    
    fixed = 0
    skipped = 0
    errors = 0
    
    for filepath in test_files:
        result = fix_test_file(filepath)
        if result:
            fixed += 1
        elif result is False:
            skipped += 1
        else:
            errors += 1
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Fixed: {fixed} files")
    print(f"Skipped: {skipped} files (already fixed)")
    print(f"Errors: {errors} files")
    
    if fixed > 0:
        print("\n[SUCCESS] Test imports fixed!")
        print("Now try running: python -m pytest tests/")

if __name__ == "__main__":
    main()