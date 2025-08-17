#!/usr/bin/env python3
import os

PRODUCTION_IP = "159.203.183.48"

print("Installing schedule and starting app FINALLY...")
print("=" * 50)

# Install schedule
print("\n1. Installing schedule module...")
os.system(f'ssh root@{PRODUCTION_IP} "cd /var/www/cora && ./venv/bin/pip install schedule"')

# Start with PM2
print("\n2. Starting app with PM2...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 start cora"')

# Wait
print("\n3. Waiting for startup...")
os.system('timeout 8')

# Test health endpoint
print("\n4. Testing health endpoint...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -s http://localhost:8000/health"')

# Check if listening on port 8000
print("\n5. Checking port 8000...")
os.system(f'ssh root@{PRODUCTION_IP} "ss -tlnp | grep 8000"')

# Test public URL
print("\n6. Testing public URL...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -I https://coraai.tech | head -3"')

# Check CSP headers
print("\n7. CSP Headers check...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -sI https://coraai.tech | grep -i content-security"')

print("\n" + "=" * 50)
print("DEPLOYMENT COMPLETE!")
print("The app should now be running with the CSP security fix.")
print("Visit https://coraai.tech")
print("=" * 50)