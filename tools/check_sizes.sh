#!/bin/bash
# 🧭 LOCATION: /CORA/tools/check_sizes.sh
# 🎯 PURPOSE: Quick size check for all tracked files
# 📝 STAYS UNDER 100 LINES!

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}📏 CORA File Size Check${NC}"
echo "========================"

# Function to check file
check_file() {
    local file=$1
    local max_lines=$2
    local label=$3
    
    if [ -f "$file" ]; then
        local lines=$(wc -l < "$file" 2>/dev/null || echo 0)
        local percent=$((lines * 100 / max_lines))
        
        if [ $percent -gt 90 ]; then
            echo -e "${RED}❌ $label: $lines/$max_lines lines (${percent}%)${NC}"
        elif [ $percent -gt 70 ]; then
            echo -e "${YELLOW}⚠️  $label: $lines/$max_lines lines (${percent}%)${NC}"
        else
            echo -e "${GREEN}✓  $label: $lines/$max_lines lines (${percent}%)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  $label: Not found${NC}"
    fi
}

# Check dashboard files
echo -e "\n${GREEN}📊 Dashboard Files:${NC}"
check_file "/mnt/host/c/CORA/NOW.md" 50 "NOW.md"
check_file "/mnt/host/c/CORA/NEXT.md" 100 "NEXT.md"
check_file "/mnt/host/c/CORA/STATUS.md" 100 "STATUS.md"

# Check today files
echo -e "\n${GREEN}📁 Today's Files:${NC}"
for file in /mnt/host/c/CORA/.mind/today/*.md; do
    if [ -f "$file" ]; then
        check_file "$file" 300 "$(basename "$file")"
    fi
done

# Check code files
echo -e "\n${GREEN}💻 Code Files (sample):${NC}"
check_file "/mnt/host/c/CORA/app.py" 300 "app.py"

# Quick stats
echo -e "\n${GREEN}📈 Quick Stats:${NC}"
echo "- Root files: $(find /mnt/host/c/CORA -maxdepth 1 -type f | wc -l)"
echo "- Today files: $(find /mnt/host/c/CORA/.mind/today -type f 2>/dev/null | wc -l)"
echo "- Total .md files: $(find /mnt/host/c/CORA -name "*.md" | wc -l)"

echo -e "\n${GREEN}💡 Tip:${NC} Run './tools/auto_archive.sh' to archive large files"