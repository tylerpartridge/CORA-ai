# Port 8001 Conflict - Server Start Failed

## The Problem:
Port 8001 is still in use by a previous process, preventing the server from starting.

## Solution - Kill Processes and Restart:

```powershell
# Kill any Python processes using port 8001
netstat -ano | findstr :8001
# Note the PID from the output, then kill it:
taskkill /F /PID <PID_NUMBER>

# Alternative: Kill all Python processes (nuclear option)
taskkill /F /IM python.exe

# Wait a moment for cleanup
timeout /t 3

# Restart server
python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

## Alternative Port:
```powershell
# Use a different port if 8001 is stuck
python -m uvicorn app:app --host 0.0.0.0 --port 8002 --reload
```

## After Server Starts:
Once the server is running, I'll recreate the webhook fix that was lost in the git reset.

The webhook handler currently has the OLD broken version that returns 422 errors. We need to fix it to accept raw Stripe events.