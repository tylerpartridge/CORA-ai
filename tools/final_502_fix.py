#!/usr/bin/env python3
import subprocess
import os

PRODUCTION_IP = "159.203.183.48"

# Minimal commands to fix the issue
commands = [
    ("pip install uvicorn", "Installing uvicorn"),
    ("cd /var/www/cora && pm2 delete all", "Cleaning PM2"),
    ("cd /var/www/cora && pm2 start 'uvicorn app:app --host 0.0.0.0 --port 8000' --name cora", "Starting app"),
    ("sleep 5", "Waiting..."),
    ("curl -s http://localhost:8000/health | python3 -m json.tool", "Testing health"),
    ("pm2 save", "Saving PM2 config")
]

for cmd, desc in commands:
    print(f"\n{desc}...")
    try:
        # Use os.system to avoid encoding issues
        os.system(f'ssh root@{PRODUCTION_IP} "{cmd}"')
    except Exception as e:
        print(f"Error: {e}")

print("\nDone! Check https://coraai.tech/health")