#!/usr/bin/env python3
import os

PRODUCTION_IP = "159.203.183.48"

print("Checking all imports and dependencies...")
print("=" * 50)

# Check detailed import errors
print("\n1. Checking import errors in detail...")
os.system(f'''ssh root@{PRODUCTION_IP} "cd /var/www/cora && ./venv/bin/python -c 'import sys; sys.path.insert(0, \\".\\"); import app' 2>&1"''')

print("\n2. Checking PM2 error logs...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 logs cora --err --lines 30 --nostream | grep -E \'ModuleNotFoundError|ImportError|File\' | tail -20"')

print("\n3. Installing common missing dependencies...")
os.system(f'ssh root@{PRODUCTION_IP} "cd /var/www/cora && ./venv/bin/pip install python-jose python-multipart passlib bcrypt python-dotenv"')

print("\n4. Restarting app...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 restart cora"')

print("\n5. Final test...")
os.system(f'ssh root@{PRODUCTION_IP} "sleep 5 && curl -s http://localhost:8000/health"')

print("\n" + "=" * 50)