#!/bin/bash
# Script to fix .mind directory git tracking issue

echo "=== Fixing .mind directory git tracking issue ==="
echo ""

# Step 1: Check current git status
echo "Step 1: Checking current git status..."
git status --porcelain | grep -i mind || echo "No .mind entries in git status"
echo ""

# Step 2: Check if .mind is a submodule
echo "Step 2: Checking for submodules..."
git submodule status 2>/dev/null || echo "No submodules found"
echo ""

# Step 3: Remove .mind from git index (force removal)
echo "Step 3: Removing .mind from git index..."
git rm -r --cached .mind 2>/dev/null || echo "Already removed from index"
echo ""

# Step 4: Also try with -f flag if needed
echo "Step 4: Force removing with -f flag..."
git rm -rf --cached .mind 2>/dev/null || echo "Already removed"
echo ""

# Step 5: Check git attributes
echo "Step 5: Checking .gitattributes..."
if [ -f .gitattributes ]; then
    grep -i mind .gitattributes || echo "No .mind entries in .gitattributes"
else
    echo "No .gitattributes file"
fi
echo ""

# Step 6: Reset git index if needed
echo "Step 6: Resetting git index..."
git reset
echo ""

# Step 7: Add all files except .mind
echo "Step 7: Re-adding all files (except .mind)..."
git add .
echo ""

# Step 8: Check final status
echo "Step 8: Final git status check..."
git status --porcelain | grep -i mind || echo "✅ SUCCESS: No .mind entries in git!"
echo ""

echo "=== Fix complete! ==="
echo ""
echo "Next steps:"
echo "1. Run: git status"
echo "2. If clean, commit: git commit -m 'Remove .mind directory from git tracking'"
echo "3. Push changes: git push origin main"