#!/usr/bin/env python3
import subprocess
import os
import time

PRODUCTION_IP = "159.203.183.48"

print("FINAL HEALTH CHECK")
print("=" * 50)

# Give it more time to start
time.sleep(5)

# Check if app is responding
print("\n1. Testing health endpoint...")
result = subprocess.run(
    ['ssh', f'root@{PRODUCTION_IP}', 'curl -s http://localhost:8000/health'],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace'
)

if result.stdout and '{' in result.stdout:
    print("SUCCESS! Health endpoint is responding:")
    print(result.stdout)
else:
    print("Still not responding. Checking logs...")
    os.system(f'ssh root@{PRODUCTION_IP} "pm2 logs cora --err --lines 5 --nostream | tail -5"')

# Check process
print("\n2. Checking if uvicorn is running...")
os.system(f'ssh root@{PRODUCTION_IP} "ps aux | grep uvicorn | grep -v grep"')

# Test public URL
print("\n3. Testing public URL...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -I https://coraai.tech/health | head -1"')

# Check CSP headers
print("\n4. Checking CSP headers...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -sI https://coraai.tech | grep -i content-security"')

print("\n" + "=" * 50)
print("If you see a 'healthy' response above, the deployment is complete!")
print("If not, check the error logs above for the remaining issue.")
print("=" * 50)