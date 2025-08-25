#!/usr/bin/env python3
import os

PRODUCTION_IP = "159.203.183.48"

print("Copying config.py and fixing final import issue...")
print("=" * 50)

# Copy config.py
print("\n1. Copying config.py...")
os.system(f'scp config.py root@{PRODUCTION_IP}:/var/www/cora/')

# Copy requirements.txt too
print("\n2. Copying requirements.txt...")
os.system(f'scp requirements.txt root@{PRODUCTION_IP}:/var/www/cora/')

# Restart app
print("\n3. Restarting app...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 restart cora"')

# Wait
print("\n4. Waiting for startup...")
os.system('timeout 5')

# Test health endpoint
print("\n5. Testing health endpoint...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -s http://localhost:8000/health"')

# Check PM2 status
print("\n6. PM2 Status...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 list"')

# Test CSP headers
print("\n7. Testing CSP headers on landing page...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -sI https://coraai.tech | grep -i content-security"')

print("\n" + "=" * 50)
print("Config file copied. The app should now be running!")
print("Visit https://coraai.tech to see the CSP security fix in action.")
print("=" * 50)