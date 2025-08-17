#!/usr/bin/env python3
"""
Remove or comment out console.log statements from production JavaScript files
"""
import os
import re
from pathlib import Path

def process_js_file(filepath):
    """Process a single JS file to handle console.log statements"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern to match console.log statements (including multiline)
    # This preserves the logic but wraps in a debug check
    pattern = r'(console\.(log|error|warn|info|debug))'
    
    # Replace with conditional that checks for debug mode
    # Only replace if not already wrapped in a condition
    def replace_console(match):
        full_match = match.group(0)
        # Check if already wrapped in a debug check
        lines_before = content[:match.start()].split('\n')
        if lines_before and 'DEBUG' in lines_before[-1]:
            return full_match
        # For production, comment out instead of wrapping
        # This is safer and cleaner
        return f'// {full_match}'
    
    # Apply replacements
    content = re.sub(pattern, replace_console, content)
    
    # Count changes
    changes = len(re.findall(pattern, original_content))
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return changes
    return 0

def main():
    """Process all JavaScript files in web/static/js"""
    
    js_dirs = [
        'web/static/js',
        'web/static/js/bundles',
        'web/components'
    ]
    
    total_changes = 0
    files_modified = 0
    
    for dir_path in js_dirs:
        if not os.path.exists(dir_path):
            continue
            
        for js_file in Path(dir_path).glob('*.js'):
            # Skip already minified files and vendor files
            if '.min.js' in str(js_file) or 'vendor' in str(js_file):
                continue
                
            changes = process_js_file(js_file)
            if changes > 0:
                print(f"Modified {js_file}: {changes} console statements commented")
                total_changes += changes
                files_modified += 1
    
    print(f"\n✅ Summary:")
    print(f"  Files modified: {files_modified}")
    print(f"  Console statements commented: {total_changes}")
    
    # Also update deployment package
    deploy_js = Path('deployment_package/web/static/js')
    if deploy_js.exists():
        print("\n📦 Updating deployment package...")
        for js_file in deploy_js.glob('*.js'):
            if '.min.js' not in str(js_file):
                changes = process_js_file(js_file)
                if changes > 0:
                    print(f"  Modified {js_file.name}: {changes} statements")

if __name__ == "__main__":
    main()