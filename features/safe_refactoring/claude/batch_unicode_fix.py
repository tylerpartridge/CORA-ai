#!/usr/bin/env python3
"""
Batch fix Unicode issues in critical files
"""

import sys
from pathlib import Path

# List of files known to have Unicode issues
FILES_TO_FIX = [
    'tests/test_comprehensive_api.py',
    'tests/test_cora_sales.py',
    'tests/test_final_system.py',
    'tests/test_auth.py',
    'tests/test_expenses.py',
    'tests/test_endpoints.py',
    'tests/test_api.py',
    'tests/test_dashboard_data.py',
    'tests/test_job_profitability.py',
    'tests/test_onboarding.py',
    'tests/test_public_pages_status.py',
    'tests/test_quickbooks_integration.py',
    'tests/test_restoration.py',
    'tests/test_template_inheritance.py',
    'tests/test_user_journey.py',
    'tests/test_voice_activation.py',
    'tests/test_voice_parser.py',
]

# Simple replacements
REPLACEMENTS = {
    '✅': '[OK]',
    '❌': '[ERROR]',
    '⚠️': '[WARNING]',
    '🧪': '[TEST]',
    '🔍': '[SEARCH]',
    '📊': '[STATS]',
    '🚀': '[LAUNCH]',
    '💡': '[HINT]',
    '🎯': '[TARGET]',
    '🔧': '[FIX]',
    '📝': '[NOTE]',
    '🧭': '[LOCATION]',
    '📤': '[EXPORT]',
    '🔗': '[LINK]',
    '✨': '[NEW]',
    '🛡️': '[SECURITY]',
    '🏗️': '[BUILD]',
    '✓': '[CHECK]',
    '✗': '[X]',
    '→': '->',
    '•': '*',
}

def fix_file(filepath):
    """Fix Unicode in a single file"""
    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original = content
        
        # Apply replacements
        for old, new in REPLACEMENTS.items():
            content = content.replace(old, new)
        
        if content != original:
            # Write back
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[FIXED] {filepath}")
            return True
        else:
            print(f"[SKIP] {filepath} - no changes needed")
            return False
            
    except Exception as e:
        print(f"[ERROR] {filepath}: {e}")
        return False

def main():
    print("Batch Unicode Fix")
    print("=" * 60)
    
    fixed = 0
    errors = 0
    
    for filepath in FILES_TO_FIX:
        full_path = Path(filepath)
        if full_path.exists():
            if fix_file(full_path):
                fixed += 1
        else:
            print(f"[NOT FOUND] {filepath}")
            errors += 1
    
    print("\n" + "=" * 60)
    print(f"Fixed: {fixed} files")
    print(f"Errors: {errors} files")
    
    if fixed > 0:
        print("\n[SUCCESS] Unicode issues fixed!")

if __name__ == "__main__":
    main()