"""
🧭 LOCATION: /CORA/tools/check_sizes.py
🎯 PURPOSE: Check file sizes and flag files approaching limits
🔗 IMPORTS: os, pathlib
📤 EXPORTS: check_file_sizes(), main()
🔄 PATTERN: Utility script
📝 TODOS: Add more file types, integrate with health check
"""

import os
from pathlib import Path

def check_file(file_path: str, max_lines: int, label: str) -> None:
    """Check a single file and report its size status"""
    file_path = Path(file_path)
    
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            
            percent = (lines * 100) // max_lines
            
            if percent > 90:
                print(f"❌ {label}: {lines}/{max_lines} lines ({percent}%)")
            elif percent > 70:
                print(f"⚠️  {label}: {lines}/{max_lines} lines ({percent}%)")
            else:
                print(f"✓  {label}: {lines}/{max_lines} lines ({percent}%)")
        except Exception as e:
            print(f"⚠️  {label}: Error reading file - {e}")
    else:
        print(f"⚠️  {label}: Not found")

def check_file_sizes():
    """Check all important files for size limits"""
    print("📏 CORA File Size Check")
    print("========================")
    
    # Get CORA root directory
    cora_root = Path(__file__).parent.parent
    
    # Check dashboard files
    print("\n📊 Dashboard Files:")
    check_file(cora_root / "NOW.md", 50, "NOW.md")
    check_file(cora_root / "NEXT.md", 100, "NEXT.md")
    check_file(cora_root / "STATUS.md", 100, "STATUS.md")
    
    # Check today files
    print("\n📁 Today's Files:")
    today_dir = cora_root / ".mind" / "today"
    if today_dir.exists():
        for file in today_dir.glob("*.md"):
            check_file(file, 300, file.name)
    else:
        print("⚠️  .mind/today directory not found")
    
    # Check code files
    print("\n💻 Code Files:")
    check_file(cora_root / "app.py", 300, "app.py")
    
    # Check Python files in tools
    tools_dir = cora_root / "tools"
    if tools_dir.exists():
        for file in tools_dir.glob("*.py"):
            check_file(file, 300, f"tools/{file.name}")
    
    # Quick stats
    print("\n📈 Quick Stats:")
    root_files = len([f for f in cora_root.iterdir() if f.is_file()])
    print(f"- Root files: {root_files}")
    
    md_files = len(list(cora_root.rglob("*.md")))
    print(f"- Total .md files: {md_files}")
    
    py_files = len(list(cora_root.rglob("*.py")))
    print(f"- Total .py files: {py_files}")
    
    print("\n💡 Tip: Run 'python tools/auto_archive.py' to archive large files")

def main():
    """Main function"""
    check_file_sizes()

if __name__ == "__main__":
    main() 