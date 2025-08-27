# Card: PORT_CONFLICT_SOLUTION.md

> Source: `docs\ai-awareness\PORT_CONFLICT_SOLUTION.md`

## Headers:
- # Port 8001 Conflict - Server Start Failed
- ## The Problem:
- ## Solution - Kill Processes and Restart:
- # Kill any Python processes using port 8001
- # Note the PID from the output, then kill it:

## Content:
Port 8001 is still in use by a previous process, preventing the server from starting. ```powershell netstat -ano | findstr :8001 taskkill /F /PID <PID_NUMBER> taskkill /F /IM python.exe timeout /t 3 python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload ``` ```powershell python -m uvicorn app:app --host 0.0.0.0 --port 8002 --reload...
