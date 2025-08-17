#!/usr/bin/env python3
import subprocess
import os
import time

PRODUCTION_IP = "159.203.183.48"

def run_cmd(cmd):
    """Run command via SSH using os.system to avoid encoding issues"""
    print(f"\n>>> {cmd[:60]}...")
    return os.system(f'ssh root@{PRODUCTION_IP} "{cmd}"')

print("FIXING 502 ERROR - GETTING APP RUNNING NOW")
print("=" * 60)

# 1. Check current PM2 status
print("\n1. Current PM2 status:")
run_cmd("pm2 list")

# 2. Stop everything and clean up
print("\n2. Cleaning up...")
run_cmd("pm2 delete all 2>/dev/null || true")
run_cmd("pkill -f uvicorn || true")

# 3. Check for any import errors
print("\n3. Testing imports...")
run_cmd("cd /var/www/cora && ./venv/bin/python -c 'import app' 2>&1 | head -20")

# 4. Start app with explicit error output
print("\n4. Starting app with detailed output...")
run_cmd("cd /var/www/cora && ./venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 > /tmp/app.log 2>&1 & echo 'Started in background'")

# 5. Wait and check log
print("\n5. Waiting for startup...")
time.sleep(5)

print("\n6. Checking app log...")
run_cmd("tail -30 /tmp/app.log")

# 7. Check if process is running
print("\n7. Checking if uvicorn is running...")
run_cmd("ps aux | grep uvicorn | grep -v grep")

# 8. Test health endpoint
print("\n8. Testing health endpoint...")
run_cmd("curl -s http://localhost:8000/health || echo 'No response'")

# 9. If still not working, try with PM2 differently
print("\n9. Starting with PM2 (alternative method)...")
run_cmd("cd /var/www/cora && pm2 start './venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8000' --name cora")

# 10. Final check
print("\n10. Final status check...")
time.sleep(3)
run_cmd("pm2 status")
run_cmd("curl -s http://localhost:8000/health || echo 'Still no response'")

print("\n" + "=" * 60)
print("Check the output above for any errors.")
print("The app log at step 6 will show the exact issue.")
print("=" * 60)