#!/bin/bash
# 🧭 LOCATION: /CORA/tools/auto_archive.sh
# 🎯 PURPOSE: Archive .mind/today/ files and enforce size limits
# 📝 RULES: This script MUST stay under 300 lines!

# Configuration
MIND_DIR="/mnt/host/c/CORA/.mind"
TODAY_DIR="$MIND_DIR/today"
ARCHIVE_DIR="$MIND_DIR/archive"
MAX_LINES=300
TODAY=$(date +%Y-%m-%d)
NOW=$(date +%H-%M-%S)

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🗄️  CORA Auto-Archive System${NC}"
echo "Date: $TODAY | Time: $NOW"
echo "----------------------------------------"

# Function to count lines in a file
count_lines() {
    wc -l < "$1" 2>/dev/null || echo 0
}

# Function to check if file exceeds limit
check_file_size() {
    local file=$1
    local lines=$(count_lines "$file")
    
    if [ $lines -gt $MAX_LINES ]; then
        echo -e "${YELLOW}⚠️  File exceeds $MAX_LINES lines: $(basename $file) ($lines lines)${NC}"
        return 1
    fi
    return 0
}

# Function to split large files
split_large_file() {
    local file=$1
    local basename=$(basename "$file" .md)
    local dir=$(dirname "$file")
    local lines=$(count_lines "$file")
    
    echo -e "${YELLOW}📄 Splitting $basename.md ($lines lines)...${NC}"
    
    # Calculate split size
    local split_lines=$((MAX_LINES - 10)) # Leave room for headers
    
    # Split the file
    split -l $split_lines "$file" "$dir/${basename}_part_" --numeric-suffixes=1
    
    # Add .md extension and headers to parts
    for part in "$dir/${basename}_part_"*; do
        if [ -f "$part" ]; then
            local part_num=$(echo "$part" | grep -o '[0-9]*$')
            local new_name="${dir}/${basename}_part${part_num}.md"
            
            # Add header to part
            {
                echo "# 📄 $basename - Part $part_num"
                echo "Split from: $basename.md on $TODAY"
                echo "---"
                cat "$part"
            } > "$new_name"
            
            rm "$part"
            echo -e "${GREEN}✓ Created: $(basename $new_name)${NC}"
        fi
    done
    
    # Archive the original
    local archive_path="$ARCHIVE_DIR/$TODAY/large_files"
    mkdir -p "$archive_path"
    mv "$file" "$archive_path/"
    echo -e "${GREEN}✓ Archived original to: archive/$TODAY/large_files/${NC}"
}

# Function to archive today's files
archive_today_files() {
    local archive_path="$ARCHIVE_DIR/$TODAY"
    
    # Check if today directory has files
    if [ ! -d "$TODAY_DIR" ] || [ -z "$(ls -A "$TODAY_DIR" 2>/dev/null)" ]; then
        echo "No files to archive in today/"
        return
    fi
    
    # Create archive directory
    mkdir -p "$archive_path"
    
    echo -e "${GREEN}📁 Archiving today's files to: archive/$TODAY/${NC}"
    
    # Copy files to archive
    for file in "$TODAY_DIR"/*; do
        if [ -f "$file" ]; then
            local filename=$(basename "$file")
            cp "$file" "$archive_path/"
            echo "  ✓ Archived: $filename"
        fi
    done
    
    # Create summary
    create_archive_summary "$archive_path"
    
    # Clear today directory (except README if exists)
    find "$TODAY_DIR" -type f ! -name "README.md" -delete
    echo -e "${GREEN}✓ Cleared today/ directory${NC}"
}

# Function to create archive summary
create_archive_summary() {
    local archive_path=$1
    local summary_file="$archive_path/SUMMARY.md"
    
    {
        echo "# 📋 Archive Summary - $TODAY"
        echo ""
        echo "## Files Archived"
        for file in "$archive_path"/*.md; do
            if [ -f "$file" ] && [ "$(basename "$file")" != "SUMMARY.md" ]; then
                local lines=$(count_lines "$file")
                echo "- $(basename "$file") ($lines lines)"
            fi
        done
        echo ""
        echo "## Archive Stats"
        echo "- Total files: $(find "$archive_path" -name "*.md" ! -name "SUMMARY.md" | wc -l)"
        echo "- Archive time: $NOW"
    } > "$summary_file"
}

# Function to check root directory dashboard files
check_dashboard_files() {
    echo -e "\n${GREEN}📊 Checking dashboard files...${NC}"
    
    # Check NOW.md (50 line limit)
    local now_file="/mnt/host/c/CORA/NOW.md"
    if [ -f "$now_file" ]; then
        local lines=$(count_lines "$now_file")
        if [ $lines -gt 50 ]; then
            echo -e "${RED}❌ NOW.md exceeds 50 lines ($lines lines)${NC}"
            echo "   Please trim to most recent/relevant items"
        else
            echo -e "${GREEN}✓ NOW.md is within limit ($lines/50 lines)${NC}"
        fi
    fi
    
    # Check NEXT.md (100 line limit)
    local next_file="/mnt/host/c/CORA/NEXT.md"
    if [ -f "$next_file" ]; then
        local lines=$(count_lines "$next_file")
        if [ $lines -gt 100 ]; then
            echo -e "${RED}❌ NEXT.md exceeds 100 lines ($lines lines)${NC}"
            echo "   Consider moving items to archive or parking lot"
        else
            echo -e "${GREEN}✓ NEXT.md is within limit ($lines/100 lines)${NC}"
        fi
    fi
}

# Main execution
main() {
    # Check and split large files in today/
    echo -e "${GREEN}🔍 Checking file sizes in today/...${NC}"
    for file in "$TODAY_DIR"/*.md; do
        if [ -f "$file" ]; then
            if ! check_file_size "$file"; then
                split_large_file "$file"
            fi
        fi
    done
    
    # Check if it's a new day (for daily archive)
    if [ "$1" == "--daily" ] || [ "$1" == "--force" ]; then
        archive_today_files
    fi
    
    # Always check dashboard files
    check_dashboard_files
    
    # Update STATUS.md with last archive time
    local status_file="/mnt/host/c/CORA/STATUS.md"
    if [ -f "$status_file" ]; then
        # Update the last checkpoint section
        sed -i "/## 💾 Last Checkpoint/,/^---/c\## 💾 Last Checkpoint\\n- **Time:** $TODAY $NOW\\n- **Action:** Auto-archive check\\n- **Next:** Continue current task\\n\\n---" "$status_file"
    fi
    
    echo -e "\n${GREEN}✅ Archive check complete!${NC}"
}

# Run with arguments
main "$@"