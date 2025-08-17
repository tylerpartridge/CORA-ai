#!/usr/bin/env python3
import os

PRODUCTION_IP = "159.203.183.48"

print("Final check for 502 error...")
print("=" * 50)

# Check current PM2 error
print("\n1. Current error from PM2...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 logs cora --err --lines 10 --nostream | grep -v TAILING | tail -10"')

# Install any missing Python packages
print("\n2. Installing additional dependencies...")
os.system(f'ssh root@{PRODUCTION_IP} "cd /var/www/cora && ./venv/bin/pip install redis email-validator slowapi"')

# Restart
print("\n3. Restarting app...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 restart cora"')

# Wait and test
print("\n4. Waiting...")
os.system('timeout 5')

print("\n5. Final test...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -s http://localhost:8000/health || echo \'No response\'"')

# If still failing, try starting manually
print("\n6. Manual start test...")
os.system(f'ssh root@{PRODUCTION_IP} "cd /var/www/cora && timeout 3 ./venv/bin/python app.py 2>&1 | head -30"')

print("\n" + "=" * 50)