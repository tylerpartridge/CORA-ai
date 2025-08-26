# Database Lock Solution

## The Problem:
Git can't reset because `cora.db-shm` (SQLite shared memory file) is locked by the running server.

## Quick Solutions:

### Option 1: Stop Server, Reset, Restart (Recommended)
```powershell
# Step 1: Kill the running server
Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.CommandLine -like "*uvicorn*"} | Stop-Process -Force

# Or use Ctrl+C in the server terminal if you can access it

# Step 2: Wait a moment for file locks to release
Start-Sleep -Seconds 3

# Step 3: Answer 'y' to the git reset prompt
# (The reset command is still waiting for your response)

# Step 4: After reset completes, restart server
python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

### Option 2: Force the Reset (Nuclear)
```powershell
# Answer 'n' to the current prompt, then:
git reset --hard HEAD~1 --force

# If that fails:
Remove-Item cora.db-shm -Force -ErrorAction SilentlyContinue
Remove-Item cora.db-wal -Force -ErrorAction SilentlyContinue
git reset --hard HEAD~1
```

### Option 3: Skip Database Files
```powershell
# Answer 'n' to current prompt, then add to .gitignore:
echo "*.db-shm" >> .gitignore
echo "*.db-wal" >> .gitignore
git reset --hard HEAD~1
```

## After Reset Success:
```powershell
# Check status
git status

# Stage ONLY the webhook file
git add routes/payment_coordinator.py

# Verify only 1 file staged
git diff --cached --name-only

# Commit and push
git commit --no-verify -m "fix: stripe webhook handler"
git push origin main
```

## Current Prompt:
You're still being asked about `cora.db-shm`. I recommend:
1. Answer **'n'** (no) to stop trying
2. Kill the server process
3. Try the reset again

The database lock is preventing git from cleaning up, but once the server stops, the files will unlock.