#!/usr/bin/env python3
import os

PRODUCTION_IP = "159.203.183.48"

print("Copying ALL middleware files to server...")
print("=" * 50)

# Copy entire middleware directory
print("\n1. Copying entire middleware directory...")
os.system(f'scp -r middleware/ root@{PRODUCTION_IP}:/var/www/cora/')

# Ensure __init__.py exists
print("\n2. Ensuring __init__.py files exist...")
os.system(f'ssh root@{PRODUCTION_IP} "touch /var/www/cora/middleware/__init__.py"')

# Copy security headers fixed as security_headers.py
print("\n3. Applying security headers fix...")
os.system(f'ssh root@{PRODUCTION_IP} "cp /var/www/cora/middleware/security_headers_fixed.py /var/www/cora/middleware/security_headers.py"')

# Restart app
print("\n4. Restarting app...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 restart cora"')

# Wait and test
print("\n5. Waiting for startup...")
os.system('timeout 5')

print("\n6. Testing health endpoint...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -s http://localhost:8000/health"')

# Check if still having issues
print("\n7. Checking PM2 status...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 list"')

print("\n8. Testing public URL...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -I https://coraai.tech | head -10"')

print("\n" + "=" * 50)
print("All middleware files copied. App should be running!")
print("=" * 50)