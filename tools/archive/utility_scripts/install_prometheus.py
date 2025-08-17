#!/usr/bin/env python3
import os

PRODUCTION_IP = "159.203.183.48"

print("Installing prometheus_client...")
os.system(f'ssh root@{PRODUCTION_IP} "cd /var/www/cora && ./venv/bin/pip install prometheus_client"')

print("\nRestarting app...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 restart cora"')

print("\nWaiting 5 seconds...")
os.system('timeout 5')

print("\nTesting health endpoint...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -s http://localhost:8000/health"')

print("\n\nDONE! The app should now be working.")