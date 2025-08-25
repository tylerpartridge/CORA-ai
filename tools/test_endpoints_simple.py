#!/usr/bin/env python3
"""Test endpoints without Unicode characters"""

import subprocess

PRODUCTION_IP = "159.203.183.48"

# Test if app is responding on localhost:8000
print("Testing localhost:8000/health...")
result = subprocess.run(
    ['ssh', f'root@{PRODUCTION_IP}', 'curl -s http://localhost:8000/health'],
    capture_output=True,
    text=True
)
print("Response:", result.stdout if result.stdout else "No response")

# Test if nginx is proxying correctly
print("\nTesting through nginx (localhost/health)...")
result = subprocess.run(
    ['ssh', f'root@{PRODUCTION_IP}', 'curl -s http://localhost/health'],
    capture_output=True,
    text=True
)
print("Response:", result.stdout if result.stdout else "No response")

# Check what port app is actually on
print("\nChecking app port...")
result = subprocess.run(
    ['ssh', f'root@{PRODUCTION_IP}', 'netstat -tlnp | grep python'],
    capture_output=True,
    text=True
)
print("Python ports:", result.stdout if result.stdout else "No Python process listening")

# Start app with uvicorn explicitly
print("\nRestarting app with uvicorn on port 8000...")
result = subprocess.run(
    ['ssh', f'root@{PRODUCTION_IP}', 
     'cd /var/www/cora && pm2 delete cora; pm2 start "uvicorn app:app --host 0.0.0.0 --port 8000" --name cora'],
    capture_output=True,
    text=True
)
print("PM2 output:", result.stdout)

# Wait and test again
print("\nWaiting 5 seconds for app to start...")
subprocess.run(['timeout', '5', 'echo', 'waiting...'], capture_output=True)

print("\nTesting health endpoint again...")
result = subprocess.run(
    ['ssh', f'root@{PRODUCTION_IP}', 'curl -s http://localhost:8000/health'],
    capture_output=True,
    text=True
)
print("Health response:", result.stdout if result.stdout else "No response")