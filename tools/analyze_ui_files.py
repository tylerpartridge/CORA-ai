#!/usr/bin/env python3
"""
Quick analysis of UI/UX files to identify what's actually used vs legacy
"""

import json
from collections import defaultdict

def analyze_ui_files():
    """Analyze UI/UX files to identify active vs legacy"""
    
    # Load the registry
    with open('reports/ui_ux_registry_20250717_172720.json', 'r') as f:
        data = json.load(f)
    
    # Group by enhancement level
    by_level = defaultdict(list)
    by_type = defaultdict(list)
    
    for path, info in data['files'].items():
        level = info.get('enhancement_level', 'unknown')
        by_level[level].append(path)
        
        # Categorize by file type
        if path.endswith('.css'):
            by_type['css'].append(path)
        elif path.endswith('.js'):
            by_type['js'].append(path)
        elif path.endswith('.html'):
            by_type['html'].append(path)
        elif path.endswith('.py'):
            by_type['middleware'].append(path)
    
    print("🎨 UI/UX File Analysis")
    print("=" * 50)
    
    print("\n📊 By Enhancement Level:")
    for level in ['a_plus', 'complete', 'enhanced', 'basic', 'none']:
        if level in by_level:
            files = by_level[level]
            print(f"  {level.upper()}: {len(files)} files")
            for file in files[:3]:  # Show first 3
                print(f"    - {file}")
            if len(files) > 3:
                print(f"    ... and {len(files) - 3} more")
    
    print("\n📁 By File Type:")
    for file_type, files in by_type.items():
        print(f"  {file_type.upper()}: {len(files)} files")
        for file in files[:3]:
            print(f"    - {file}")
        if len(files) > 3:
            print(f"    ... and {len(files) - 3} more")
    
    print("\n🎯 Active Files (Enhanced or Better):")
    active_files = []
    for level in ['a_plus', 'complete', 'enhanced']:
        active_files.extend(by_level.get(level, []))
    
    for file in sorted(active_files):
        print(f"  ✅ {file}")
    
    print(f"\n📈 Summary:")
    print(f"  Total Files: {len(data['files'])}")
    print(f"  Active Files: {len(active_files)}")
    print(f"  Legacy Files: {len(data['files']) - len(active_files)}")
    
    return active_files, by_level

if __name__ == "__main__":
    analyze_ui_files() 