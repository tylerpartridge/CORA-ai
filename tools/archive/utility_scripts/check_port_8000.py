#!/usr/bin/env python3
import os

PRODUCTION_IP = "159.203.183.48"

print("Checking port 8000 and app status...")
print("=" * 50)

# Check if anything is listening on port 8000
print("\n1. Checking port 8000...")
os.system(f'ssh root@{PRODUCTION_IP} "ss -tlnp | grep 8000 || echo \'Nothing listening on port 8000\'"')

# Check PM2 error logs
print("\n2. Recent PM2 errors...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 logs cora --err --lines 20 --nostream | tail -20"')

# Try starting app WITHOUT PM2 to see direct output
print("\n3. Stopping PM2 and starting directly...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 stop cora"')
os.system(f'ssh root@{PRODUCTION_IP} "cd /var/www/cora && ./venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 > /tmp/direct_start.log 2>&1 & echo \'Started in background\'"')

# Wait and check
print("\n4. Waiting 5 seconds...")
os.system('timeout 5')

print("\n5. Checking if it started...")
os.system(f'ssh root@{PRODUCTION_IP} "tail -50 /tmp/direct_start.log"')

# Test port 8000
print("\n6. Testing port 8000...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -s http://localhost:8000/health || echo \'No response\'"')

print("\n" + "=" * 50)