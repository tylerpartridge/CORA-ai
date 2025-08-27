# Card: DATABASE_LOCK_SOLUTION.md

> Source: `docs\ai-awareness\DATABASE_LOCK_SOLUTION.md`

## Headers:
- # Database Lock Solution
- ## The Problem:
- ## Quick Solutions:
- ### Option 1: Stop Server, Reset, Restart (Recommended)
- # Step 1: Kill the running server

## Content:
Git can't reset because `cora.db-shm` (SQLite shared memory file) is locked by the running server. ```powershell Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.CommandLine -like "*uvicorn*"} | Stop-Process -Force Start-Sleep -Seconds 3 python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload ``` ```powershell git reset --hard HEAD~1 --force Remove-Item cora.db-shm -Force -ErrorAction SilentlyContinue Remove-Item cora.db-wal -Force -ErrorAction SilentlyContinue...
