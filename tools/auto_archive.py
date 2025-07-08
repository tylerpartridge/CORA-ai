"""
🧭 LOCATION: /CORA/tools/auto_archive.py
🎯 PURPOSE: Archive .mind/today/ files and enforce size limits (cross-platform)
🔗 IMPORTS: os, pathlib, datetime, shutil
📤 EXPORTS: archive_today_files(), check_and_split_large_files()
🔄 PATTERN: Utility script
📝 TODOS: Add automatic daily scheduling
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Configuration
MIND_DIR = Path(__file__).parent.parent / ".mind"
TODAY_DIR = MIND_DIR / "today"
ARCHIVE_DIR = MIND_DIR / "archive"
MAX_LINES = 300
TODAY = datetime.now().strftime("%Y-%m-%d")
NOW = datetime.now().strftime("%H-%M-%S")

# Colors for output (work on both Windows and Linux)
GREEN = '\033[0;32m' if os.name != 'nt' else ''
YELLOW = '\033[1;33m' if os.name != 'nt' else ''
RED = '\033[0;31m' if os.name != 'nt' else ''
NC = '\033[0m' if os.name != 'nt' else ''

def count_lines(file_path: Path) -> int:
    """Count lines in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except:
        return 0

def check_file_size(file_path: Path) -> bool:
    """Check if file exceeds limit"""
    lines = count_lines(file_path)
    if lines > MAX_LINES:
        print(f"{YELLOW}⚠️  File exceeds {MAX_LINES} lines: {file_path.name} ({lines} lines){NC}")
        return False
    return True

def split_large_file(file_path: Path):
    """Split a large file into parts"""
    lines = count_lines(file_path)
    print(f"{YELLOW}📄 Splitting {file_path.name} ({lines} lines)...{NC}")
    
    # Read all lines
    with open(file_path, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
    
    # Calculate parts needed
    split_lines = MAX_LINES - 10  # Leave room for headers
    parts_needed = (lines // split_lines) + (1 if lines % split_lines else 0)
    
    # Create parts
    for i in range(parts_needed):
        start = i * split_lines
        end = min((i + 1) * split_lines, lines)
        part_lines = all_lines[start:end]
        
        # Create part file
        part_name = file_path.stem + f"_part{i+1}.md"
        part_path = file_path.parent / part_name
        
        with open(part_path, 'w', encoding='utf-8') as f:
            f.write(f"# 📄 {file_path.stem} - Part {i+1}\n")
            f.write(f"Split from: {file_path.name} on {TODAY}\n")
            f.write("---\n")
            f.writelines(part_lines)
        
        print(f"{GREEN}✓ Created: {part_name}{NC}")
    
    # Archive original
    archive_path = ARCHIVE_DIR / TODAY / "large_files"
    archive_path.mkdir(parents=True, exist_ok=True)
    shutil.move(str(file_path), str(archive_path / file_path.name))
    print(f"{GREEN}✓ Archived original to: archive/{TODAY}/large_files/{NC}")

def archive_today_files():
    """Archive today's files"""
    if not TODAY_DIR.exists() or not any(TODAY_DIR.iterdir()):
        print("No files to archive in today/")
        return
    
    # Create archive directory
    archive_path = ARCHIVE_DIR / TODAY
    archive_path.mkdir(parents=True, exist_ok=True)
    
    print(f"{GREEN}📁 Archiving today's files to: archive/{TODAY}/{NC}")
    
    # Copy files to archive
    for file in TODAY_DIR.glob("*"):
        if file.is_file():
            shutil.copy2(str(file), str(archive_path / file.name))
            print(f"  ✓ Archived: {file.name}")
    
    # Create summary
    create_archive_summary(archive_path)
    
    # Clear today directory (except README)
    for file in TODAY_DIR.glob("*"):
        if file.is_file() and file.name != "README.md":
            file.unlink()
    
    print(f"{GREEN}✓ Cleared today/ directory{NC}")

def create_archive_summary(archive_path: Path):
    """Create archive summary"""
    summary_file = archive_path / "SUMMARY.md"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"# 📋 Archive Summary - {TODAY}\n\n")
        f.write("## Files Archived\n")
        
        for file in archive_path.glob("*.md"):
            if file.name != "SUMMARY.md":
                lines = count_lines(file)
                f.write(f"- {file.name} ({lines} lines)\n")
        
        f.write(f"\n## Archive Stats\n")
        f.write(f"- Total files: {len(list(archive_path.glob('*.md'))) - 1}\n")
        f.write(f"- Archive time: {NOW}\n")

def check_dashboard_files():
    """Check root directory dashboard files"""
    print(f"\n{GREEN}📊 Checking dashboard files...{NC}")
    cora_root = Path(__file__).parent.parent
    
    # Check NOW.md (50 line limit)
    now_file = cora_root / "NOW.md"
    if now_file.exists():
        lines = count_lines(now_file)
        if lines > 50:
            print(f"{RED}❌ NOW.md exceeds 50 lines ({lines} lines){NC}")
            print("   Please trim to most recent/relevant items")
        else:
            print(f"{GREEN}✓ NOW.md is within limit ({lines}/50 lines){NC}")
    
    # Check NEXT.md (100 line limit)
    next_file = cora_root / "NEXT.md"
    if next_file.exists():
        lines = count_lines(next_file)
        if lines > 100:
            print(f"{RED}❌ NEXT.md exceeds 100 lines ({lines} lines){NC}")
            print("   Consider moving items to archive or parking lot")
        else:
            print(f"{GREEN}✓ NEXT.md is within limit ({lines}/100 lines){NC}")

def update_status():
    """Update STATUS.md with last archive time"""
    cora_root = Path(__file__).parent.parent
    status_file = cora_root / "STATUS.md"
    
    if status_file.exists():
        with open(status_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update last checkpoint section
        checkpoint_section = f"## 💾 Last Checkpoint\n- **Time:** {TODAY} {NOW}\n- **Action:** Auto-archive check\n- **Next:** Continue current task"
        
        # Simple replace (works for our use case)
        if "## 💾 Last Checkpoint" in content:
            start = content.find("## 💾 Last Checkpoint")
            end = content.find("\n---", start)
            if end == -1:
                end = len(content)
            content = content[:start] + checkpoint_section + content[end:]
        
        with open(status_file, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    """Main function"""
    import sys
    
    print(f"{GREEN}🗄️  CORA Auto-Archive System{NC}")
    print(f"Date: {TODAY} | Time: {NOW}")
    print("----------------------------------------")
    
    # Check and split large files
    print(f"{GREEN}🔍 Checking file sizes in today/...{NC}")
    if TODAY_DIR.exists():
        for file in TODAY_DIR.glob("*.md"):
            if not check_file_size(file):
                split_large_file(file)
    
    # Check if daily archive requested
    if "--daily" in sys.argv or "--force" in sys.argv:
        archive_today_files()
    
    # Always check dashboard files
    check_dashboard_files()
    
    # Update status
    update_status()
    
    print(f"\n{GREEN}✅ Archive check complete!{NC}")

if __name__ == "__main__":
    main()