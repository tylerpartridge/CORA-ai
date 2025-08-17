#!/usr/bin/env python3
import os
import time

PRODUCTION_IP = "159.203.183.48"

print("Installing psutil and starting app...")
print("=" * 50)

# Install psutil
print("\n1. Installing psutil...")
os.system(f'ssh root@{PRODUCTION_IP} "cd /var/www/cora && ./venv/bin/pip install psutil"')

# Restart PM2
print("\n2. Restarting app...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 restart cora"')

# Wait
print("\n3. Waiting for startup...")
time.sleep(5)

# Test health
print("\n4. Testing health endpoint...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -s http://localhost:8000/health | python3 -m json.tool || echo \'No JSON response\'"')

# Check PM2 status
print("\n5. PM2 Status...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 list"')

# Test public URL
print("\n6. Testing public URL...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -sI https://coraai.tech/health | head -5"')

print("\n" + "=" * 50)
print("The app should now be running!")
print("Visit https://coraai.tech to see the CSP headers in action.")
print("=" * 50)