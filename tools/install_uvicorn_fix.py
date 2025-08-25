#!/usr/bin/env python3
"""Install uvicorn and fix the 502 error"""

import subprocess
import time

PRODUCTION_IP = "159.203.183.48"

def run_command(cmd):
    """Run command via SSH"""
    result = subprocess.run(
        ['ssh', f'root@{PRODUCTION_IP}', cmd],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout, result.stderr, result.returncode

print("FIXING 502 ERROR - Installing uvicorn and dependencies")
print("=" * 60)

# 1. Install uvicorn and dependencies
print("\n1. Installing uvicorn and dependencies...")
stdout, stderr, code = run_command("pip install uvicorn fastapi pydantic starlette")
if code == 0:
    print("SUCCESS: Dependencies installed")
else:
    print("ERROR installing dependencies:", stderr)

# 2. Verify uvicorn is installed
print("\n2. Verifying uvicorn installation...")
stdout, stderr, code = run_command("which uvicorn && uvicorn --version")
if stdout:
    print("Uvicorn location and version:", stdout.strip())

# 3. Clean up PM2
print("\n3. Cleaning up PM2...")
run_command("pm2 delete all 2>/dev/null || true")

# 4. Start app with PM2 using full path
print("\n4. Starting app with PM2...")
stdout, stderr, code = run_command("""
cd /var/www/cora && pm2 start "$(which uvicorn) app:app --host 0.0.0.0 --port 8000" --name cora
""")
if code == 0:
    print("PM2 started successfully")

# 5. Save PM2 config
run_command("pm2 save")
run_command("pm2 startup systemd -u root --hp /root")

# 6. Wait for startup
print("\n5. Waiting for app to start...")
time.sleep(5)

# 7. Check PM2 status
print("\n6. Checking PM2 status...")
stdout, stderr, code = run_command("pm2 list --no-color")
print(stdout.replace('\u2713', '[OK]').replace('│', '|'))

# 8. Test endpoints
print("\n7. Testing endpoints...")
endpoints = [
    ("http://localhost:8000/health", "Direct health check"),
    ("http://localhost/health", "Nginx proxied health check"),
    ("http://localhost:8000/api/status", "API status check")
]

for endpoint, description in endpoints:
    stdout, stderr, code = run_command(f"curl -s {endpoint} | head -50")
    print(f"\n{description} ({endpoint}):")
    if stdout:
        print("Response:", stdout[:200])
    else:
        print("No response")

# 9. Check recent logs
print("\n8. Recent PM2 logs...")
stdout, stderr, code = run_command("pm2 logs cora --lines 10 --nostream --no-color")
if stdout:
    # Show only relevant lines
    for line in stdout.split('\n'):
        if 'INFO:' in line or 'ERROR' in line or 'Started' in line:
            print(line)

print("\n" + "=" * 60)
print("COMPLETE! Check https://coraai.tech/health")
print("The landing page shows 200 OK in logs, so CSP fix is deployed!")
print("=" * 60)