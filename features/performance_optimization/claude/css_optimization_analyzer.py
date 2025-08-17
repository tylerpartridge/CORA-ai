#!/usr/bin/env python3
"""
🎨 CSS OPTIMIZATION ANALYZER
📁 LOCATION: /CORA/features/performance_optimization/claude/css_optimization_analyzer.py
⚠️ PURPOSE: Analyze CSS files for optimization opportunities
"""

import os
import re
from collections import defaultdict
from pathlib import Path

def analyze_css_files():
    """Analyze CSS files for optimization opportunities"""
    static_dir = "/mnt/host/c/CORA/web/static"
    templates_dir = "/mnt/host/c/CORA/web/templates"
    
    css_files = []
    template_files = []
    
    print("CSS OPTIMIZATION ANALYSIS")
    print("=" * 40)
    
    # Find all CSS files
    for root, dirs, files in os.walk(static_dir):
        for file in files:
            if file.endswith('.css'):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                css_files.append({
                    'name': file,
                    'path': file_path,
                    'rel_path': file_path.replace(static_dir, ''),
                    'size': file_size,
                    'size_kb': file_size // 1024
                })
    
    # Find all template files
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                template_files.append(os.path.join(root, file))
    
    # Sort CSS files by size
    css_files.sort(key=lambda x: x['size'], reverse=True)
    
    print("\\n1. CSS FILES BY SIZE:")
    print("-" * 25)
    for css_file in css_files:
        print(f"{css_file['size_kb']:3}KB - {css_file['name']}")
    
    # Analyze CSS usage in templates
    print("\\n2. CSS USAGE ANALYSIS:")
    print("-" * 25)
    
    css_usage = defaultdict(list)
    
    for template_path in template_files:
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            template_name = Path(template_path).name
            
            for css_file in css_files:
                css_name = css_file['name']
                if css_name in content:
                    css_usage[css_name].append(template_name)
        except:
            continue
    
    # Show usage
    unused_css = []
    for css_file in css_files:
        css_name = css_file['name']
        used_in = css_usage.get(css_name, [])
        
        if used_in:
            print(f"{css_name} ({css_file['size_kb']}KB):")
            for template in used_in:
                print(f"  - {template}")
        else:
            unused_css.append(css_file)
            print(f"{css_name} ({css_file['size_kb']}KB): NOT USED")
        print()
    
    # Consolidation opportunities
    print("3. OPTIMIZATION OPPORTUNITIES:")
    print("-" * 30)
    
    large_files = [f for f in css_files if f['size_kb'] > 10]
    if large_files:
        print("Large files that could be minified:")
        for css_file in large_files:
            print(f"  {css_file['name']} ({css_file['size_kb']}KB)")
            # Estimate minification savings
            try:
                with open(css_file['path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Simple minification estimate
                minified = re.sub(r'/\\*.*?\\*/', '', content, flags=re.DOTALL)  # Remove comments
                minified = re.sub(r'\\s+', ' ', minified)  # Collapse whitespace
                minified = re.sub(r'\\s*([{}:;,>+~])\\s*', r'\\1', minified)  # Remove extra spaces
                
                minified_size = len(minified)
                original_size = len(content)
                savings = original_size - minified_size
                savings_percent = (savings / original_size) * 100
                
                if savings_percent > 10:
                    print(f"    Potential savings: {savings//1024}KB ({savings_percent:.1f}%)")
            except:
                print(f"    Could not analyze for minification")
        print()
    
    if unused_css:
        total_unused_kb = sum(f['size_kb'] for f in unused_css)
        print(f"Unused CSS files ({total_unused_kb}KB total):")
        for css_file in unused_css:
            print(f"  {css_file['name']} ({css_file['size_kb']}KB)")
        print()
    
    # Check for duplicate/similar CSS
    print("4. DUPLICATE/SIMILAR CSS CHECK:")
    print("-" * 30)
    
    similar_names = defaultdict(list)
    for css_file in css_files:
        base_name = css_file['name'].replace('-consolidated', '').replace('-theme', '').replace('.css', '')
        similar_names[base_name].append(css_file)
    
    for base_name, files in similar_names.items():
        if len(files) > 1:
            print(f"Similar CSS files ('{base_name}' theme):")
            for css_file in files:
                print(f"  {css_file['name']} ({css_file['size_kb']}KB)")
            print()
    
    # Recommendations
    print("5. RECOMMENDATIONS:")
    print("-" * 18)
    
    total_css_size = sum(f['size_kb'] for f in css_files)
    print(f"Total CSS size: {total_css_size}KB")
    
    if large_files:
        potential_savings = sum(f['size_kb'] * 0.3 for f in large_files)  # Estimate 30% savings
        print(f"Potential minification savings: ~{potential_savings:.0f}KB")
    
    if unused_css:
        unused_savings = sum(f['size_kb'] for f in unused_css)
        print(f"Potential removal savings: {unused_savings}KB")
    
    print("\\nSafe optimizations to implement:")
    print("1. Minify large CSS files (>10KB)")
    print("2. Remove unused CSS files (if confirmed unused)")
    print("3. Combine similar themed CSS files")
    print("4. Use critical CSS loading for above-the-fold content")

if __name__ == "__main__":
    analyze_css_files()