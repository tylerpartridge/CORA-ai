#!/usr/bin/env python3
import subprocess
import os
import time

PRODUCTION_IP = "159.203.183.48"

print("Final health check...")
print("=" * 50)

# Give it a moment
time.sleep(3)

# Test health endpoint
print("\nTesting health endpoint directly...")
result = subprocess.run(
    ['ssh', f'root@{PRODUCTION_IP}', 'curl -s http://localhost:8000/health'],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace'
)

if result.stdout:
    print("Health response:", result.stdout)
else:
    print("No response - checking PM2 logs...")
    os.system(f'ssh root@{PRODUCTION_IP} "pm2 logs cora --err --lines 10 --nostream"')

# Test through nginx
print("\nTesting through nginx...")
result = subprocess.run(
    ['ssh', f'root@{PRODUCTION_IP}', 'curl -s http://localhost/health'],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace'
)

if '502' in str(result.stdout):
    print("Still getting 502")
elif result.stdout:
    print("Nginx response:", result.stdout)

# Check CSP headers
print("\nChecking CSP headers...")
result = subprocess.run(
    ['ssh', f'root@{PRODUCTION_IP}', 'curl -I https://coraai.tech 2>/dev/null | grep -i content-security'],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace'
)

if result.stdout:
    print("CSP Header found:", result.stdout.strip())
else:
    print("No CSP header found")

print("\n" + "=" * 50)
print("If health endpoint shows 'healthy', the deployment is complete!")
print("Check https://coraai.tech to verify CSP headers are working.")
print("=" * 50)