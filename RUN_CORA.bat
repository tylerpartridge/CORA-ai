@echo off
cls
echo ========================================
echo           STARTING CORA
echo ========================================
echo.
echo Killing any existing servers...
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul
echo.
echo Starting CORA on port 8001...
echo.
echo ========================================
echo    OPEN YOUR BROWSER AND GO TO:
echo    http://localhost:8001
echo ========================================
echo.
python app.py --port