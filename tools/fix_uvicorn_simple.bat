@echo off
echo Installing uvicorn on server...
ssh root@159.203.183.48 "pip install uvicorn fastapi pydantic starlette"
echo.
echo Restarting app...
ssh root@159.203.183.48 "cd /var/www/cora && pm2 delete cora 2>nul & pm2 start 'uvicorn app:app --host 0.0.0.0 --port 8000' --name cora"
echo.
echo Waiting 5 seconds...
timeout /t 5 /nobreak >nul
echo.
echo Testing health endpoint...
ssh root@159.203.183.48 "curl -s http://localhost:8000/health"
echo.
echo Done!