#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/ui_file_usage_analyzer.py
🎯 PURPOSE: Safe analysis of UI/UX file usage - READ ONLY
🔗 IMPORTS: pathlib, re, json
📤 EXPORTS: analyze_file_usage, find_orphaned_files
🔄 PATTERN: Safe analysis before any file operations
📝 STATUS: Production ready for safe analysis

💡 AI HINT: This is READ ONLY - no file modifications
⚠️ NEVER: Delete files without explicit permission
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def analyze_file_usage():
    """Analyze which UI/UX files are actually being used"""
    
    project_root = Path(__file__).parent.parent
    web_dir = project_root / "web"
    
    # Files to analyze
    css_files = list((web_dir / "static" / "css").glob("*.css"))
    js_files = list((web_dir / "static" / "js").glob("*.js"))
    template_files = list((web_dir / "templates").glob("*.html"))
    onboarding_templates = list((web_dir / "templates" / "onboarding").glob("*.html"))
    integration_templates = list((web_dir / "templates" / "integrations").glob("*.html"))
    
    all_templates = template_files + onboarding_templates + integration_templates
    
    # Track file usage
    file_usage = {
        'css': defaultdict(list),
        'js': defaultdict(list),
        'templates': defaultdict(list)
    }
    
    # Analyze template files for CSS/JS references
    for template in all_templates:
        try:
            content = template.read_text(encoding='utf-8')
            template_path = str(template.relative_to(project_root))
            
            # Find CSS references
            css_patterns = [
                r'href="([^"]*\.css)"',
                r'href=\'([^\']*\.css)\'',
                r'rel="stylesheet"[^>]*href="([^"]*)"',
                r'rel=\'stylesheet\'[^>]*href=\'([^\']*)\''
            ]
            
            for pattern in css_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    file_usage['css'][match].append(template_path)
            
            # Find JS references
            js_patterns = [
                r'src="([^"]*\.js)"',
                r'src=\'([^\']*\.js)\'',
                r'<script[^>]*src="([^"]*)"',
                r'<script[^>]*src=\'([^\']*)\''
            ]
            
            for pattern in js_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    file_usage['js'][match].append(template_path)
            
            # Track template usage (check if referenced in routes)
            file_usage['templates'][template_path] = []
            
        except Exception as e:
            print(f"⚠️  Error reading {template}: {e}")
    
    # Check route files for template references
    routes_dir = project_root / "routes"
    if routes_dir.exists():
        for route_file in routes_dir.glob("*.py"):
            try:
                content = route_file.read_text(encoding='utf-8')
                
                # Look for template references
                template_patterns = [
                    r'render_template\([\'"]([^\'"]*\.html)[\'"]',
                    r'template_name[\s]*=[\s]*[\'"]([^\'"]*\.html)[\'"]',
                    r'return[\s]+render_template\([\'"]([^\'"]*\.html)[\'"]'
                ]
                
                for pattern in template_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if match in file_usage['templates']:
                            file_usage['templates'][match].append(str(route_file.relative_to(project_root)))
                
            except Exception as e:
                print(f"⚠️  Error reading route file {route_file}: {e}")
    
    return file_usage

def find_orphaned_files(file_usage):
    """Find files that aren't being used"""
    
    project_root = Path(__file__).parent.parent
    web_dir = project_root / "web"
    
    # Get all UI/UX files
    all_css = {f.name: f for f in (web_dir / "static" / "css").glob("*.css")}
    all_js = {f.name: f for f in (web_dir / "static" / "js").glob("*.js")}
    
    # Find unused files
    orphaned = {
        'css': [],
        'js': [],
        'templates': []
    }
    
    # Check CSS files
    for css_file in all_css.values():
        css_name = css_file.name
        if css_name not in file_usage['css']:
            orphaned['css'].append(str(css_file.relative_to(project_root)))
    
    # Check JS files
    for js_file in all_js.values():
        js_name = js_file.name
        if js_name not in file_usage['js']:
            orphaned['js'].append(str(js_file.relative_to(project_root)))
    
    # Check templates (those not referenced in routes)
    for template_path, references in file_usage['templates'].items():
        if not references:
            orphaned['templates'].append(template_path)
    
    return orphaned

def print_analysis(file_usage, orphaned):
    """Print the analysis results"""
    
    print("🔍 UI/UX File Usage Analysis")
    print("=" * 60)
    
    print("\n📊 CSS Files Usage:")
    for css_file, templates in file_usage['css'].items():
        print(f"  ✅ {css_file}")
        for template in templates:
            print(f"    └─ Used by: {template}")
    
    print("\n📊 JS Files Usage:")
    for js_file, templates in file_usage['js'].items():
        print(f"  ✅ {js_file}")
        for template in templates:
            print(f"    └─ Used by: {template}")
    
    print("\n📊 Template Files Usage:")
    for template, routes in file_usage['templates'].items():
        if routes:
            print(f"  ✅ {template}")
            for route in routes:
                print(f"    └─ Referenced in: {route}")
        else:
            print(f"  ⚠️  {template} (no route references found)")
    
    print("\n🗑️  POTENTIALLY ORPHANED FILES:")
    print("=" * 60)
    
    if orphaned['css']:
        print("\n📁 Unused CSS Files:")
        for css in orphaned['css']:
            print(f"  ❌ {css}")
    
    if orphaned['js']:
        print("\n📁 Unused JS Files:")
        for js in orphaned['js']:
            print(f"  ❌ {js}")
    
    if orphaned['templates']:
        print("\n📁 Unused Template Files:")
        for template in orphaned['templates']:
            print(f"  ❌ {template}")
    
    if not any(orphaned.values()):
        print("  ✅ No orphaned files found!")
    
    print(f"\n📈 Summary:")
    print(f"  Total CSS files: {len(file_usage['css'])}")
    print(f"  Total JS files: {len(file_usage['js'])}")
    print(f"  Total templates: {len(file_usage['templates'])}")
    print(f"  Potentially orphaned: {sum(len(files) for files in orphaned.values())}")

if __name__ == "__main__":
    print("🔍 Starting safe UI/UX file usage analysis...")
    file_usage = analyze_file_usage()
    orphaned = find_orphaned_files(file_usage)
    print_analysis(file_usage, orphaned)
    
    print("\n🛡️  SAFETY NOTE: This is READ-ONLY analysis.")
    print("   No files have been modified or deleted.")
    print("   Review results carefully before any file operations.") 