#!/usr/bin/env python3
import os

PRODUCTION_IP = "159.203.183.48"

print("Final diagnosis of 502 error...")
print("=" * 50)

# Check current error
print("\n1. Current PM2 error...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 logs cora --err --lines 15 --nostream | grep -v TAILING"')

# Try to start directly to see error
print("\n2. Starting directly to see full error...")
os.system(f'ssh root@{PRODUCTION_IP} "cd /var/www/cora && timeout 5 ./venv/bin/python app.py 2>&1 | head -50"')

# Check what's missing now
print("\n3. Testing specific imports...")
os.system(f'''ssh root@{PRODUCTION_IP} "cd /var/www/cora && ./venv/bin/python -c 'from models import User, Expense'"''')

print("\n" + "=" * 50)