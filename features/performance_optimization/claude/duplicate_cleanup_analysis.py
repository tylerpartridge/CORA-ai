#!/usr/bin/env python3
"""
🔍 PURPOSE: Analyze duplicate static files for safe cleanup
📁 LOCATION: /CORA/features/performance_optimization/claude/duplicate_cleanup_analysis.py
⚠️ SAFETY: Analysis only - no files modified without explicit approval
"""

import os
import hashlib
from collections import defaultdict
from pathlib import Path

def get_file_hash(filepath):
    """Get MD5 hash of file content"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def analyze_duplicates():
    """Analyze duplicate files in web/static directory"""
    static_dir = "/mnt/host/c/CORA/web/static"
    
    # Find all JS and CSS files
    files_by_name = defaultdict(list)
    files_by_content = defaultdict(list)
    
    print("Analyzing static files for duplicates...")
    
    if not os.path.exists(static_dir):
        print(f"❌ Static directory not found: {static_dir}")
        return
    
    for root, dirs, files in os.walk(static_dir):
        for file in files:
            if file.endswith(('.js', '.css')):
                file_path = os.path.join(root, file)
                rel_path = file_path.replace(static_dir, '')
                file_size = os.path.getsize(file_path)
                file_hash = get_file_hash(file_path)
                
                files_by_name[file].append({
                    'path': rel_path,
                    'full_path': file_path,
                    'size': file_size,
                    'hash': file_hash
                })
                
                if file_hash:
                    files_by_content[file_hash].append({
                        'name': file,
                        'path': rel_path,
                        'full_path': file_path,
                        'size': file_size
                    })
    
    print("\\n📊 DUPLICATE ANALYSIS RESULTS")
    print("=" * 50)
    
    # Analyze by filename
    print("\\n1. DUPLICATE FILENAMES:")
    name_duplicates = {name: files for name, files in files_by_name.items() if len(files) > 1}
    
    total_wasted_space = 0
    cleanup_recommendations = []
    
    for filename, files in name_duplicates.items():
        print(f"\\n📄 {filename} ({len(files)} copies):")
        files.sort(key=lambda x: x['size'], reverse=True)
        
        for i, file_info in enumerate(files):
            size_kb = file_info['size'] // 1024
            status = "LARGEST" if i == 0 else f"smaller (-{((files[0]['size'] - file_info['size']) // 1024)}KB)"
            print(f"  {file_info['path']} ({size_kb}KB) [{status}]")
        
        # Check if smaller versions are redundant
        if len(files) > 1:
            largest = files[0]
            for smaller in files[1:]:
                if '/bundles/' in smaller['path'] and '/bundles/' not in largest['path']:
                    # Bundle version is smaller - might be minified, keep both
                    print(f"  ✅ Bundle version detected - likely minified, keep both")
                elif '/bundles/' in largest['path'] and '/bundles/' not in smaller['path']:
                    # Bundle is larger - original might be unminified
                    space_saved = smaller['size']
                    total_wasted_space += space_saved
                    cleanup_recommendations.append({
                        'action': 'remove_redundant',
                        'file': smaller['full_path'],
                        'reason': 'Unbundled version exists, bundle is newer',
                        'space_saved': space_saved
                    })
                    print(f"  🗑️  Could remove: {smaller['path']} (saves {space_saved//1024}KB)")
    
    # Analyze by content
    print("\\n2. IDENTICAL CONTENT:")
    content_duplicates = {hash_val: files for hash_val, files in files_by_content.items() if len(files) > 1}
    
    for hash_val, files in content_duplicates.items():
        if len(files) > 1:
            print(f"\\n🔄 Identical files ({files[0]['size']//1024}KB each):")
            for file_info in files:
                print(f"  {file_info['path']}")
            
            # Recommend keeping the one in the most logical location
            keep_file = min(files, key=lambda x: len(x['path']))  # Keep shortest path
            for file_info in files:
                if file_info != keep_file:
                    space_saved = file_info['size']
                    total_wasted_space += space_saved
                    cleanup_recommendations.append({
                        'action': 'remove_duplicate',
                        'file': file_info['full_path'],
                        'reason': f'Identical to {keep_file["path"]}',
                        'space_saved': space_saved
                    })
    
    print("\\n📈 CLEANUP SUMMARY")
    print("=" * 30)
    print(f"Total wasted space: {total_wasted_space//1024}KB")
    print(f"Files that could be removed: {len(cleanup_recommendations)}")
    
    if cleanup_recommendations:
        print("\\n🗑️ SAFE CLEANUP RECOMMENDATIONS:")
        for rec in cleanup_recommendations:
            rel_path = rec['file'].replace('/mnt/host/c/CORA/web/static', '')
            print(f"  Remove: {rel_path}")
            print(f"    Reason: {rec['reason']}")
            print(f"    Saves: {rec['space_saved']//1024}KB")
            print()
    
    return cleanup_recommendations

def create_cleanup_script(recommendations):
    """Create a safe cleanup script"""
    if not recommendations:
        print("✅ No cleanup needed!")
        return
    
    script_path = "/mnt/host/c/CORA/features/performance_optimization/claude/safe_cleanup.py"
    
    script_content = f'''#!/usr/bin/env python3
"""
SAFE STATIC FILE CLEANUP SCRIPT
Generated: {os.path.basename(__file__)}
Total files to clean: {len(recommendations)}
Total space to save: {sum(r["space_saved"] for r in recommendations)//1024}KB
"""

import os
import shutil
from datetime import datetime

# Set to True to actually execute cleanup
DRY_RUN = True

def backup_file(filepath):
    """Create backup before removal"""
    backup_path = f"{{filepath}}.backup_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}"
    shutil.copy2(filepath, backup_path)
    return backup_path

def main():
    if DRY_RUN:
        print("🔬 DRY RUN MODE - No files will be removed")
        print("Set DRY_RUN = False to execute cleanup")
    
    files_to_remove = ['''
    
    for rec in recommendations:
        script_content += f'''
        {{
            "file": "{rec['file']}",
            "reason": "{rec['reason']}",
            "space_saved": {rec['space_saved']}
        }},'''
    
    script_content += '''
    ]
    
    total_space_saved = 0
    
    for file_info in files_to_remove:
        filepath = file_info["file"]
        
        if os.path.exists(filepath):
            rel_path = filepath.replace("/mnt/host/c/CORA/web/static", "")
            size_kb = os.path.getsize(filepath) // 1024
            
            print(f"\\n📄 {rel_path} ({size_kb}KB)")
            print(f"   Reason: {file_info['reason']}")
            
            if not DRY_RUN:
                backup_path = backup_file(filepath)
                os.remove(filepath)
                print(f"   ✅ Removed (backup: {os.path.basename(backup_path)})")
                total_space_saved += file_info["space_saved"]
            else:
                print(f"   🔬 Would remove (saves {size_kb}KB)")
    
    if not DRY_RUN:
        print(f"\\n🎉 Cleanup complete! Saved {total_space_saved//1024}KB")
    else:
        estimated_savings = sum(f["space_saved"] for f in files_to_remove) // 1024
        print(f"\\n📊 Estimated savings: {estimated_savings}KB")

if __name__ == "__main__":
    main()
'''
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    os.chmod(script_path, 0o755)
    print(f"\\n📝 Created cleanup script: {script_path}")
    print("   Run with: python safe_cleanup.py")

if __name__ == "__main__":
    recommendations = analyze_duplicates()
    create_cleanup_script(recommendations)