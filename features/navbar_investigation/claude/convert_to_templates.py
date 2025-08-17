#!/usr/bin/env python3
"""
Template Conversion Script - Converts pages to use template inheritance
Author: Claude
Date: 2025-08-09
Purpose: Convert standalone HTML pages to use Jinja2 template inheritance
"""

import os
from pathlib import Path
from datetime import datetime

# Configuration
TEMPLATES_DIR = Path("web/templates")
BACKUP_DIR = Path("backups/template_conversion_" + datetime.now().strftime("%Y%m%d_%H%M%S"))

# Pages to convert with their template type
CONVERSIONS = {
    # High priority pages
    "pricing.html": "base_public.html",
    "features.html": "base_public.html", 
    "how-it-works.html": "base_public.html",
    "contact.html": "base_public.html",
    "reviews.html": "base_public.html",
    
    # Auth pages
    "login.html": "base_minimal.html",
    "signup.html": "base_minimal.html",
}

def create_backup(file_path):
    """Create backup of file before modification"""
    if not file_path.exists():
        return False
    
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / file_path.name
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[OK] Backed up {file_path.name} to {backup_path}")
    return True

def extract_page_content(html_content):
    """Extract the main content between nav and footer"""
    # Find content between </nav> and <footer
    nav_end = html_content.find('</nav>')
    footer_start = html_content.find('<footer')
    
    if nav_end == -1 or footer_start == -1:
        # Fallback: find body content
        body_start = html_content.find('<body')
        body_start = html_content.find('>', body_start) + 1 if body_start != -1 else 0
        body_end = html_content.find('</body>')
        
        if body_start != -1 and body_end != -1:
            return html_content[body_start:body_end].strip()
    
    # Skip past </nav> 
    content_start = nav_end + len('</nav>')
    content = html_content[content_start:footer_start].strip()
    
    return content

def extract_title(html_content):
    """Extract page title"""
    title_start = html_content.find('<title>')
    title_end = html_content.find('</title>')
    
    if title_start != -1 and title_end != -1:
        return html_content[title_start + 7:title_end].strip()
    
    return "CORA - Construction Financial Intelligence"

def extract_description(html_content):
    """Extract meta description"""
    desc_start = html_content.find('name="description"')
    if desc_start != -1:
        content_start = html_content.find('content="', desc_start)
        if content_start != -1:
            content_start += 9
            content_end = html_content.find('"', content_start)
            if content_end != -1:
                return html_content[content_start:content_end].strip()
    
    return "CORA helps contractors track jobs, control costs, and boost profits."

def convert_to_template(file_path, base_template):
    """Convert HTML file to use template inheritance"""
    print(f"\n[CONVERTING] {file_path.name} to use {base_template}...")
    
    # Read original content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract components
    title = extract_title(content)
    description = extract_description(content)
    main_content = extract_page_content(content)
    
    # Build new template
    template = f"""{{% extends "{base_template}" %}}

{{% block page_title %}}{title}{{% endblock %}}

{{% block page_description %}}{description}{{% endblock %}}

{{% block content %}}
{main_content}
{{% endblock %}}"""
    
    return template

def main():
    print("=" * 60)
    print("TEMPLATE CONVERSION SCRIPT")
    print("Converting standalone HTML to template inheritance")
    print("=" * 60)
    
    # Create backup directory
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n[BACKUP DIR] {BACKUP_DIR}")
    
    # Process each file
    converted = []
    failed = []
    
    for filename, base_template in CONVERSIONS.items():
        file_path = TEMPLATES_DIR / filename
        
        if not file_path.exists():
            print(f"[ERROR] {filename} not found, skipping...")
            failed.append(filename)
            continue
        
        # Create backup
        if not create_backup(file_path):
            print(f"[ERROR] Failed to backup {filename}, skipping...")
            failed.append(filename)
            continue
        
        try:
            # Convert to template
            new_content = convert_to_template(file_path, base_template)
            
            # Write converted file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"[SUCCESS] Converted {filename}")
            converted.append(filename)
            
        except Exception as e:
            print(f"[ERROR] Converting {filename}: {e}")
            failed.append(filename)
    
    # Summary
    print("\n" + "=" * 60)
    print("CONVERSION SUMMARY")
    print("=" * 60)
    print(f"[SUCCESS] Converted: {len(converted)} files")
    for f in converted:
        print(f"   - {f}")
    
    if failed:
        print(f"\n[FAILED] {len(failed)} files")
        for f in failed:
            print(f"   - {f}")
    
    print(f"\n[BACKUPS] Saved to: {BACKUP_DIR}")
    print("\n[IMPORTANT] Test all converted pages in the browser!")
    print("If any issues, restore from backups.")

if __name__ == "__main__":
    # DRY RUN MODE - Set to False to actually convert
    DRY_RUN = True
    
    if DRY_RUN:
        print("\n[DRY RUN MODE] - No files will be modified")
        print("Set DRY_RUN = False to actually convert files")
        print("\nFiles that would be converted:")
        for filename, base_template in CONVERSIONS.items():
            file_path = TEMPLATES_DIR / filename
            if file_path.exists():
                size = file_path.stat().st_size / 1024
                print(f"  - {filename} ({size:.1f} KB) -> {base_template}")
    else:
        response = input("\n[WARNING] This will modify files. Continue? (yes/no): ")
        if response.lower() == 'yes':
            main()
        else:
            print("Cancelled.")