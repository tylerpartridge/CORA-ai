#!/usr/bin/env python3
import subprocess
import os

PRODUCTION_IP = "159.203.183.48"

# Copy monitoring middleware
print("Copying monitoring middleware...")
os.system(f'scp middleware/monitoring.py root@{PRODUCTION_IP}:/var/www/cora/middleware/')

# Restart app
print("\nRestarting app...")
os.system(f'ssh root@{PRODUCTION_IP} "cd /var/www/cora && pm2 restart cora"')

# Wait and test
print("\nWaiting 5 seconds...")
os.system('timeout 5')

print("\nTesting health endpoint...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -s http://localhost:8000/health"')

print("\n\nChecking CSP headers on landing page...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -sI https://coraai.tech | grep -i content-security"')