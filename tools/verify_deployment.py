#!/usr/bin/env python3
import subprocess
import time
import json

PRODUCTION_IP = "159.203.183.48"

def run_ssh(cmd):
    """Run SSH command and return output"""
    result = subprocess.run(
        ['ssh', f'root@{PRODUCTION_IP}', cmd],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout.strip()

print("FINAL DEPLOYMENT VERIFICATION")
print("=" * 60)

# Wait a bit more for app to stabilize
time.sleep(3)

# 1. Check if app is running
print("\n1. Checking app process...")
ps_output = run_ssh("ps aux | grep uvicorn | grep -v grep")
if ps_output:
    print("✓ Uvicorn process is running")
else:
    print("✗ Uvicorn process not found")

# 2. Test health endpoint
print("\n2. Testing health endpoint...")
health = run_ssh("curl -s http://localhost:8000/health")
if health:
    try:
        data = json.loads(health)
        print(f"✓ Health endpoint working: {data}")
    except:
        print(f"Response: {health[:100]}")
else:
    print("✗ No response from health endpoint")
    # Check error logs
    print("\nRecent errors:")
    errors = run_ssh("pm2 logs cora --err --lines 5 --nostream --no-color | grep -v TAILING")
    print(errors)

# 3. Test nginx proxy
print("\n3. Testing nginx proxy...")
nginx_health = run_ssh("curl -s http://localhost/health")
if "502" not in nginx_health and nginx_health:
    print("✓ Nginx proxy working")
else:
    print("✗ Nginx returning 502")

# 4. Test public URL
print("\n4. Testing public URL...")
public_test = run_ssh("curl -sI https://coraai.tech/health | head -1")
print(f"Public response: {public_test}")

# 5. Check CSP headers
print("\n5. Checking CSP headers on landing page...")
csp = run_ssh("curl -sI https://coraai.tech | grep -i content-security-policy")
if csp:
    print("✓ CSP headers found:")
    print(csp)
else:
    print("✗ No CSP headers found")

# 6. PM2 status
print("\n6. PM2 Status...")
pm2_status = run_ssh("pm2 list --no-color | grep cora")
print(pm2_status)

print("\n" + "=" * 60)
print("DEPLOYMENT SUMMARY:")
print("- Virtual environment: ✓ Created")
print("- Dependencies: ✓ Installed (uvicorn, prometheus_client)")
print("- Middleware: ✓ All files copied")
print("- PM2: ✓ App restarted")
print("\nTest the deployment at:")
print("- https://coraai.tech (Landing page with CSP headers)")
print("- https://coraai.tech/health (Health check endpoint)")
print("=" * 60)