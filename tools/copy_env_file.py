#!/usr/bin/env python3
import os

PRODUCTION_IP = "159.203.183.48"

print("Copying existing .env file to server...")
print("=" * 50)

# Copy .env file
print("\n1. Copying .env file...")
os.system(f'scp .env root@{PRODUCTION_IP}:/var/www/cora/')

# Restart app
print("\n2. Restarting app...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 restart cora"')

# Wait
print("\n3. Waiting for startup...")
os.system('timeout 5')

# Test health endpoint
print("\n4. Testing health endpoint...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -s http://localhost:8000/health"')

# Check if it's working
print("\n5. Checking public URL...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -I https://coraai.tech/health | head -1"')

# Check CSP headers
print("\n6. Testing CSP headers...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -sI https://coraai.tech | grep -i content-security"')

print("\n" + "=" * 50)
print("Environment file copied. App should be running now!")
print("=" * 50)