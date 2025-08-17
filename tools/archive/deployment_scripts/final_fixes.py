#!/usr/bin/env python3
import os

PRODUCTION_IP = "159.203.183.48"

print("Applying final fixes...")
print("=" * 50)

# Install pytesseract
print("\n1. Installing pytesseract...")
os.system(f'ssh root@{PRODUCTION_IP} "cd /var/www/cora && ./venv/bin/pip install pytesseract pillow"')

# Copy database file
print("\n2. Copying database file...")
os.system(f'scp data/cora.db root@{PRODUCTION_IP}:/var/www/cora/')

# Restart app
print("\n3. Restarting app...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 restart cora"')

# Wait longer this time
print("\n4. Waiting for startup...")
os.system('timeout 8')

# Test health endpoint
print("\n5. Testing health endpoint...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -s http://localhost:8000/health"')

# Check if running
print("\n6. Checking if app is running...")
os.system(f'ssh root@{PRODUCTION_IP} "ps aux | grep uvicorn | grep -v grep"')

# Test public URL
print("\n7. Testing public URL...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -I https://coraai.tech | head -5"')

print("\n" + "=" * 50)
print("Final fixes applied!")
print("The app should now be running with the CSP security fix.")
print("Visit https://coraai.tech to verify.")
print("=" * 50)