@echo off
echo Killing all Python processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM python3.exe 2>nul
taskkill /F /IM uvicorn.exe 2>nul
timeout /t 2 >nul
echo.
echo Starting CORA on port 8001...
python app.py --port 8001
pause