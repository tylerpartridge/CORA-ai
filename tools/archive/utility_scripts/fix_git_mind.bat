@echo off
REM Script to fix .mind directory git tracking issue on Windows

echo === Fixing .mind directory git tracking issue ===
echo.

REM Step 1: Check current git status
echo Step 1: Checking current git status...
git status --porcelain | findstr /i mind
if errorlevel 1 echo No .mind entries in git status
echo.

REM Step 2: Remove .mind from git index
echo Step 2: Removing .mind from git index...
git rm -r --cached .mind 2>nul
if errorlevel 1 echo Already removed from index
echo.

REM Step 3: Force removal with -f flag
echo Step 3: Force removing with -f flag...
git rm -rf --cached .mind 2>nul
if errorlevel 1 echo Already removed
echo.

REM Step 4: Check for .gitattributes
echo Step 4: Checking .gitattributes...
if exist .gitattributes (
    findstr /i mind .gitattributes
    if errorlevel 1 echo No .mind entries in .gitattributes
) else (
    echo No .gitattributes file
)
echo.

REM Step 5: Reset git index
echo Step 5: Resetting git index...
git reset
echo.

REM Step 6: Re-add all files
echo Step 6: Re-adding all files (except .mind)...
git add .
echo.

REM Step 7: Final check
echo Step 7: Final git status check...
git status --porcelain | findstr /i mind
if errorlevel 1 echo SUCCESS: No .mind entries in git!
echo.

echo === Fix complete! ===
echo.
echo Next steps:
echo 1. Run: git status
echo 2. If clean, commit: git commit -m "Remove .mind directory from git tracking"
echo 3. Push changes: git push origin main
pause