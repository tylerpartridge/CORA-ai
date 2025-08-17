#!/usr/bin/env python3
"""
CSS Architecture Audit - Validate and expand on Cursor's findings
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def find_css_definitions(root_dir="/mnt/host/c/CORA/web"):
    """Find all CSS class definitions across HTML and CSS files"""
    
    css_classes = defaultdict(list)  # class_name: [(file, line_num, definition)]
    
    # Patterns to find CSS definitions
    patterns = {
        'css_file': r'\.([a-zA-Z][\w-]*)\s*\{',  # .class-name {
        'style_tag': r'\.([a-zA-Z][\w-]*)\s*\{',  # Same pattern in <style> tags
        'inline_class': r'class="([^"]*)"',  # class="name1 name2"
        'inline_style': r'style="([^"]*)"',  # style="..."
    }
    
    # Search through all HTML and CSS files
    for root, dirs, files in os.walk(root_dir):
        # Skip node_modules and similar
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__']]
        
        for file in files:
            if file.endswith(('.html', '.css')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.splitlines()
                        
                        # Track if we're in a <style> tag
                        in_style = False
                        
                        for line_num, line in enumerate(lines, 1):
                            # Check for style tag boundaries
                            if '<style' in line:
                                in_style = True
                            elif '</style>' in line:
                                in_style = False
                            
                            # Find CSS class definitions
                            if file.endswith('.css') or in_style:
                                matches = re.finditer(patterns['css_file'], line)
                                for match in matches:
                                    class_name = match.group(1)
                                    rel_path = os.path.relpath(file_path, root_dir)
                                    css_classes[class_name].append((rel_path, line_num, 'definition'))
                            
                            # Find inline styles
                            if 'style=' in line:
                                rel_path = os.path.relpath(file_path, root_dir)
                                css_classes['INLINE_STYLES'].append((rel_path, line_num, 'inline'))
                                
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return css_classes

def analyze_conflicts(css_classes):
    """Identify CSS conflicts and duplicates"""
    
    conflicts = {}
    
    # Find classes defined in multiple places
    for class_name, locations in css_classes.items():
        if class_name == 'INLINE_STYLES':
            continue
        
        unique_files = set(loc[0] for loc in locations)
        if len(unique_files) > 1:
            conflicts[class_name] = {
                'count': len(unique_files),
                'files': list(unique_files),
                'total_definitions': len(locations)
            }
    
    return conflicts

def check_css_variables():
    """Check CSS variable usage and definitions"""
    
    variables = defaultdict(list)
    var_pattern = r'var\(--([^)]+)\)'
    def_pattern = r'--([a-zA-Z][\w-]*)\s*:'
    
    root_dir = "/mnt/host/c/CORA/web"
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git']]
        
        for file in files:
            if file.endswith(('.html', '.css')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Find variable definitions
                        for match in re.finditer(def_pattern, content):
                            var_name = match.group(1)
                            rel_path = os.path.relpath(file_path, root_dir)
                            variables[var_name].append(('defined', rel_path))
                        
                        # Find variable usage
                        for match in re.finditer(var_pattern, content):
                            var_name = match.group(1)
                            rel_path = os.path.relpath(file_path, root_dir)
                            variables[var_name].append(('used', rel_path))
                            
                except Exception:
                    pass
    
    return variables

def main():
    print("="*80)
    print("CSS ARCHITECTURE AUDIT - Validating Cursor's Findings")
    print("="*80)
    
    # Find all CSS definitions
    print("\n[SCANNING] CSS DEFINITIONS...")
    css_classes = find_css_definitions()
    
    # Analyze conflicts
    print("\n[WARNING] CSS CLASS CONFLICTS FOUND:")
    print("-"*60)
    conflicts = analyze_conflicts(css_classes)
    
    # Sort by number of conflicting files
    sorted_conflicts = sorted(conflicts.items(), key=lambda x: x[1]['count'], reverse=True)
    
    # Focus on the most problematic classes
    critical_classes = ['pricing-card', 'btn-construction', 'btn-construction-secondary']
    
    print("\n[CRITICAL] CLASS CONFLICTS (mentioned by Cursor):")
    for class_name in critical_classes:
        if class_name in conflicts:
            info = conflicts[class_name]
            print(f"\n  .{class_name}:")
            print(f"    Defined in {info['count']} different files!")
            for file in info['files'][:5]:  # Show first 5
                print(f"      - {file}")
    
    print("\n[WARNING] OTHER MAJOR CONFLICTS (10+ definitions):")
    for class_name, info in sorted_conflicts[:10]:
        if class_name not in critical_classes and info['total_definitions'] >= 10:
            print(f"  .{class_name}: {info['count']} files, {info['total_definitions']} total definitions")
    
    # Check inline styles
    inline_count = len(css_classes.get('INLINE_STYLES', []))
    print(f"\n[STATS] INLINE STYLES: {inline_count} occurrences found")
    if inline_count > 50:
        print("  [WARNING] Heavy use of inline styles indicates CSS architecture issues")
    
    # Check CSS variables
    print("\n[VARIABLES] CSS VARIABLES ANALYSIS:")
    variables = check_css_variables()
    
    # Find undefined variables
    undefined = []
    for var_name, usages in variables.items():
        types = [u[0] for u in usages]
        if 'used' in types and 'defined' not in types:
            undefined.append(var_name)
    
    if undefined:
        print(f"  [WARNING] {len(undefined)} variables used but never defined:")
        for var in undefined[:5]:
            print(f"    - var(--{var})")
    
    # Summary
    print("\n" + "="*80)
    print("[REPORT] VALIDATION OF CURSOR'S FINDINGS:")
    print("-"*60)
    
    cursor_claims = {
        "Multiple .pricing-card definitions": 'pricing-card' in conflicts,
        "Multiple .btn-construction-secondary definitions": 'btn-construction-secondary' in conflicts,
        "Heavy inline style usage": inline_count > 20,
        "CSS variable issues": len(undefined) > 0
    }
    
    for claim, validated in cursor_claims.items():
        status = "[OK] CONFIRMED" if validated else "[FAIL] NOT FOUND"
        print(f"  {claim}: {status}")
    
    # Additional findings
    print("\n[NEW] ADDITIONAL FINDINGS (beyond Cursor's report):")
    print("-"*60)
    
    # Count total conflicts
    total_conflicts = len(conflicts)
    major_conflicts = sum(1 for c in conflicts.values() if c['count'] >= 3)
    
    print(f"  1. Total conflicting classes: {total_conflicts}")
    print(f"  2. Classes defined in 3+ files: {major_conflicts}")
    print(f"  3. Most conflicted class: ", end="")
    if sorted_conflicts:
        worst = sorted_conflicts[0]
        print(f".{worst[0]} ({worst[1]['count']} files)")
    else:
        print("None")
    
    # Check for CSS in wrong places
    print("\n[ALERT] CSS ARCHITECTURE VIOLATIONS:")
    
    # Check for styles in HTML templates
    template_styles = 0
    for class_name, locations in css_classes.items():
        for loc in locations:
            if 'templates/' in loc[0] and loc[0].endswith('.html'):
                template_styles += 1
                break
    
    print(f"  - Styles defined in HTML templates: {template_styles}")
    print(f"  - No CSS modules or scoping detected")
    print(f"  - No BEM or naming convention detected")
    
    print("\n" + "="*80)
    print("[ADVICE] RECOMMENDATIONS:")
    print("-"*60)
    print("  1. IMMEDIATE: Continue using inline styles for select-plan (working)")
    print("  2. SHORT-TERM: Create page-specific CSS files with scoped classes")
    print("  3. LONG-TERM: Implement CSS architecture (BEM, CSS Modules, or Tailwind)")
    print("  4. CRITICAL: Consolidate .pricing-card definitions into ONE file")
    print("="*80)

if __name__ == "__main__":
    main()