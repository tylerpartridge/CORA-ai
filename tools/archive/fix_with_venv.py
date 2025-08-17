#!/usr/bin/env python3
import subprocess
import os

PRODUCTION_IP = "159.203.183.48"

commands = [
    # Create virtual environment
    ("cd /var/www/cora && python3 -m venv venv", "Creating virtual environment"),
    
    # Install dependencies in venv
    ("cd /var/www/cora && ./venv/bin/pip install uvicorn fastapi pydantic starlette sqlalchemy", "Installing dependencies in venv"),
    
    # Clean up PM2
    ("pm2 delete all 2>/dev/null || true", "Cleaning PM2"),
    
    # Start app with venv Python
    ("cd /var/www/cora && pm2 start './venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000' --name cora", "Starting app with venv"),
    
    # Wait
    ("sleep 5", "Waiting for startup"),
    
    # Test health
    ("curl -s http://localhost:8000/health", "Testing health endpoint"),
    
    # Check PM2 status
    ("pm2 status", "PM2 status"),
    
    # Save PM2
    ("pm2 save", "Saving PM2 config")
]

for cmd, desc in commands:
    print(f"\n{desc}...")
    os.system(f'ssh root@{PRODUCTION_IP} "{cmd}"')

print("\nDone! The app should now be running with the CSP security fix.")
print("Test at: https://coraai.tech/health")