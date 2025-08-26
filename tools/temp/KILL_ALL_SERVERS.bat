@echo off
echo Killing all Python and server processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM python3.exe 2>nul
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM node.exe 2>nul
echo.
echo All server processes killed.
echo You can now start fresh with: python app.py
pause