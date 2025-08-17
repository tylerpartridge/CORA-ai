#!/usr/bin/env python3
"""
Fix Unicode issues in Python files
Replaces emojis and special characters that cause encoding errors
"""

import os
import re
from pathlib import Path

# Mapping of emojis to text replacements
EMOJI_REPLACEMENTS = {
    '🧭': '[LOCATION]',
    '🎯': '[PURPOSE]',
    '🔗': '[IMPORTS]',
    '📤': '[EXPORTS]',
    '🔄': '[PATTERN]',
    '📝': '[STATUS]',
    '💡': '[HINT]',
    '⚠️': '[WARNING]',
    '✅': '[OK]',
    '❌': '[ERROR]',
    '🚀': '[LAUNCH]',
    '🔧': '[FIX]',
    '🏗️': '[BUILD]',
    '🧪': '[TEST]',
    '✨': '[NEW]',
    '🛡️': '[SECURITY]',
    '🔍': '[SEARCH]',
    '📊': '[STATS]',
    '🎉': '[SUCCESS]',
    '📁': '[FOLDER]',
    '📂': '[FOLDER]',
    '🗂️': '[FILES]',
    '💾': '[SAVE]',
    '🔒': '[LOCKED]',
    '🔓': '[UNLOCKED]',
    '🌟': '[STAR]',
    '⭐': '[STAR]',
    '🔥': '[HOT]',
    '💰': '[MONEY]',
    '💳': '[PAYMENT]',
    '📈': '[GROWTH]',
    '📉': '[DECLINE]',
    '⏰': '[TIME]',
    '🕐': '[TIME]',
    '📅': '[DATE]',
    '🔔': '[ALERT]',
    '📢': '[ANNOUNCE]',
    '💬': '[CHAT]',
    '💭': '[THINK]',
    '🤖': '[AI]',
    '👤': '[USER]',
    '👥': '[USERS]',
    '🏠': '[HOME]',
    '🏢': '[OFFICE]',
    '🌍': '[GLOBAL]',
    '🌎': '[GLOBAL]',
    '🌏': '[GLOBAL]',
    '📧': '[EMAIL]',
    '📱': '[PHONE]',
    '💻': '[COMPUTER]',
    '🖥️': '[DESKTOP]',
    '⚡': '[FAST]',
    '🔋': '[BATTERY]',
    '🔌': '[PLUGIN]',
    '🎨': '[DESIGN]',
    '🖼️': '[IMAGE]',
    '📷': '[PHOTO]',
    '🎥': '[VIDEO]',
    '🎵': '[MUSIC]',
    '🔊': '[SOUND]',
    '🔇': '[MUTE]',
    '📚': '[DOCS]',
    '📖': '[BOOK]',
    '📃': '[PAGE]',
    '📄': '[FILE]',
    '📋': '[CLIPBOARD]',
    '📌': '[PIN]',
    '📍': '[LOCATION]',
    '🏆': '[TROPHY]',
    '🥇': '[FIRST]',
    '🥈': '[SECOND]',
    '🥉': '[THIRD]',
    '🎁': '[GIFT]',
    '🎈': '[CELEBRATE]',
    '🎊': '[PARTY]',
    '✔️': '[CHECK]',
    '✓': '[CHECK]',
    '✗': '[X]',
    '❗': '[!]',
    '❓': '[?]',
    '💯': '[100%]',
    '🆕': '[NEW]',
    '🆗': '[OK]',
    '🆙': '[UP]',
    '⬆️': '[UP]',
    '⬇️': '[DOWN]',
    '➡️': '[RIGHT]',
    '⬅️': '[LEFT]',
    '↩️': '[RETURN]',
    '⏪': '[BACK]',
    '⏩': '[FORWARD]',
    '▶️': '[PLAY]',
    '⏸️': '[PAUSE]',
    '⏹️': '[STOP]',
    '🔴': '[RED]',
    '🟢': '[GREEN]',
    '🟡': '[YELLOW]',
    '🔵': '[BLUE]',
    '⚫': '[BLACK]',
    '⚪': '[WHITE]',
    '🟠': '[ORANGE]',
    '🟣': '[PURPLE]',
}

def fix_unicode_in_file(filepath: Path, dry_run: bool = False) -> bool:
    """Fix Unicode issues in a single file"""
    try:
        # Read file with UTF-8
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace all emojis
        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            if emoji in content:
                content = content.replace(emoji, replacement)
                if not dry_run:
                    print(f"  Replaced '{emoji}' with '{replacement}'")
        
        # Check if changes were made
        if content != original_content:
            if not dry_run:
                # Create backup
                backup_path = filepath.with_suffix(filepath.suffix + '.unicode_backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                # Write fixed content
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"[FIXED] {filepath}")
                return True
            else:
                print(f"[WOULD FIX] {filepath}")
                return True
        
        return False
        
    except Exception as e:
        print(f"[ERROR] {filepath}: {e}")
        return False

def find_files_with_unicode():
    """Find all Python files with Unicode issues"""
    files = []
    
    # Search patterns for various Unicode ranges
    patterns = [
        r'[\U0001F300-\U0001F9FF]',  # Emojis
        r'[\u2600-\u26FF]',           # Miscellaneous Symbols
        r'[\u2700-\u27BF]',           # Dingbats
    ]
    
    # Find all Python files
    for py_file in Path('/mnt/host/c/CORA').rglob('*.py'):
        # Skip backup and archive directories
        if 'backup' in str(py_file).lower() or 'archive' in str(py_file).lower():
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for any emoji
            for emoji in EMOJI_REPLACEMENTS.keys():
                if emoji in content:
                    files.append(py_file)
                    break
                    
        except Exception:
            pass
    
    return files

def main():
    print("Unicode Fix Script")
    print("=" * 60)
    
    # Find files with Unicode
    print("Scanning for files with Unicode issues...")
    files = find_files_with_unicode()
    
    print(f"\nFound {len(files)} files with Unicode characters\n")
    
    if not files:
        print("No files need fixing!")
        return
    
    # Show files
    print("Files to fix:")
    for f in files[:20]:  # Show first 20
        print(f"  - {f}")
    if len(files) > 20:
        print(f"  ... and {len(files) - 20} more")
    
    print("\n" + "=" * 60)
    
    # Ask for confirmation
    response = input("\nProceed with fixing? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled")
        return
    
    # Fix files
    fixed_count = 0
    for filepath in files:
        if fix_unicode_in_file(filepath):
            fixed_count += 1
    
    print("\n" + "=" * 60)
    print(f"Fixed {fixed_count} files")
    print("\nBackups created with .unicode_backup extension")
    print("To restore: rename .unicode_backup files back to .py")

if __name__ == "__main__":
    main()