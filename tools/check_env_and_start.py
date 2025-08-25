#!/usr/bin/env python3
import os
import time

PRODUCTION_IP = "159.203.183.48"

print("Checking .env file and app status...")
print("=" * 50)

# Check if .env exists
print("\n1. Checking if .env file exists on server...")
os.system(f'ssh root@{PRODUCTION_IP} "ls -la /var/www/cora/.env"')

# Check PM2 logs for current error
print("\n2. Current error...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 logs cora --err --lines 10 --nostream | tail -10"')

# Test starting app directly to see all output
print("\n3. Starting app directly to see full output...")
os.system(f'ssh root@{PRODUCTION_IP} "cd /var/www/cora && timeout 5 ./venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 2>&1 | tail -50"')

# Check if database file exists
print("\n4. Checking if database exists...")
os.system(f'ssh root@{PRODUCTION_IP} "ls -la /var/www/cora/cora.db 2>/dev/null || echo \'No database file found\'"')

print("\n" + "=" * 50)