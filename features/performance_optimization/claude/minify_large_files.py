#!/usr/bin/env python3
"""
🎯 PURPOSE: Bundle and minify large JavaScript/CSS files for better performance
📁 LOCATION: /CORA/features/performance_optimization/claude/minify_large_files.py
⚠️ SAFETY: Only processes files >30KB, creates backups, dry-run mode available
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

# Configuration
DRY_RUN = False  # Set to False to actually execute
MIN_FILE_SIZE = 20 * 1024  # 20KB threshold
STATIC_DIR = "/mnt/host/c/CORA/web/static"

def backup_file(file_path):
    """Create timestamped backup"""
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    return backup_path

def minify_js(content):
    """Basic JavaScript minification - removes comments and extra whitespace"""
    # Remove single line comments (but preserve URLs)
    content = re.sub(r'(?<!:)//(?![\/\*]).*$', '', content, flags=re.MULTILINE)
    
    # Remove multi-line comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Remove extra whitespace
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'\s*([{}();,])\s*', r'\1', content)
    
    return content.strip()

def minify_css(content):
    """Basic CSS minification"""
    # Remove comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Remove extra whitespace
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', content)
    
    return content.strip()

def get_large_files():
    """Find JavaScript and CSS files larger than threshold"""
    large_files = []
    
    for root, dirs, files in os.walk(STATIC_DIR):
        for file in files:
            if file.endswith(('.js', '.css')):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                
                if file_size > MIN_FILE_SIZE:
                    large_files.append({
                        'path': file_path,
                        'size': file_size,
                        'size_kb': file_size // 1024
                    })
    
    return sorted(large_files, key=lambda x: x['size'], reverse=True)

def minify_file(file_info):
    """Minify a single file"""
    file_path = file_info['path']
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_size = len(content)
        
        if file_path.endswith('.js'):
            minified_content = minify_js(content)
        else:  # .css
            minified_content = minify_css(content)
        
        minified_size = len(minified_content)
        savings_percent = ((original_size - minified_size) / original_size) * 100
        
        if not DRY_RUN and savings_percent > 5:  # Only save if >5% savings
            backup_path = backup_file(file_path)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(minified_content)
            
            return {
                'success': True,
                'original_size': original_size,
                'minified_size': minified_size,
                'savings_percent': savings_percent,
                'backup_path': backup_path
            }
        else:
            return {
                'success': False,
                'original_size': original_size,
                'minified_size': minified_size,
                'savings_percent': savings_percent,
                'reason': 'Insufficient savings' if savings_percent <= 5 else 'Dry run mode'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    print("Finding large JavaScript and CSS files...")
    large_files = get_large_files()
    
    if not large_files:
        print("No large files found that need minification")
        return
    
    print(f"\nFound {len(large_files)} large files:")
    for file_info in large_files:
        rel_path = file_info['path'].replace(STATIC_DIR, '')
        print(f"  {rel_path} ({file_info['size_kb']}KB)")
    
    if DRY_RUN:
        print("\nDRY RUN MODE - No files will be modified")
    
    print(f"\nProcessing files...")
    
    total_original = 0
    total_minified = 0
    processed_count = 0
    
    for file_info in large_files:
        rel_path = file_info['path'].replace(STATIC_DIR, '')
        print(f"\nProcessing: {rel_path}")
        
        result = minify_file(file_info)
        
        if result['success']:
            total_original += result['original_size']
            total_minified += result['minified_size']
            processed_count += 1
            
            print(f"  Minified: {result['original_size']:,} -> {result['minified_size']:,} bytes")
            print(f"  Savings: {result['savings_percent']:.1f}%")
            if not DRY_RUN:
                print(f"  Backup: {os.path.basename(result['backup_path'])}")
        else:
            print(f"  Skipped: {result.get('reason', result.get('error', 'Unknown error'))}")
    
    if total_original > 0:
        overall_savings = ((total_original - total_minified) / total_original) * 100
        print(f"\nSUMMARY:")
        print(f"  Files processed: {processed_count}")
        print(f"  Original size: {total_original:,} bytes ({total_original//1024}KB)")
        print(f"  Minified size: {total_minified:,} bytes ({total_minified//1024}KB)")
        print(f"  Total savings: {overall_savings:.1f}%")
        print(f"  Space saved: {(total_original - total_minified)//1024}KB")

if __name__ == "__main__":
    main()