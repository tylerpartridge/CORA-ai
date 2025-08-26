@echo off
echo Starting CORA...
echo.
echo [1] Starting server on http://localhost:8000
echo.
cd /d C:\CORA
venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
pause