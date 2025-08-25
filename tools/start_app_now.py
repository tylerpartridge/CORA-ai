#!/usr/bin/env python3
import subprocess
import sys

PRODUCTION_IP = "159.203.183.48"

# Set UTF-8 for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def run_ssh(cmd):
    """Run SSH command safely"""
    try:
        result = subprocess.run(
            ['ssh', f'root@{PRODUCTION_IP}', cmd],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)

print("Starting CORA app...")

# 1. Kill any existing processes
print("\n1. Cleaning up...")
stdout, stderr = run_ssh("pkill -f uvicorn; pkill -f 'python.*app.py'; pm2 delete all 2>/dev/null || true")

# 2. Start with PM2 and ecosystem file
print("\n2. Creating PM2 ecosystem file...")
ecosystem = '''module.exports = {
  apps: [{
    name: 'cora',
    script: '/usr/local/bin/uvicorn',
    args: 'app:app --host 0.0.0.0 --port 8000',
    cwd: '/var/www/cora',
    interpreter: 'none',
    env: {
      PYTHONPATH: '/var/www/cora'
    }
  }]
}'''

stdout, stderr = run_ssh(f"echo '{ecosystem}' > /var/www/cora/ecosystem.config.js")

# 3. Start with ecosystem file
print("\n3. Starting with PM2...")
stdout, stderr = run_ssh("cd /var/www/cora && pm2 start ecosystem.config.js")
if stdout:
    print("PM2 output:", stdout.replace('\u2713', '[OK]').replace('│', '|'))

# 4. Wait and check
print("\n4. Waiting for startup...")
import time
time.sleep(5)

# 5. Check if running
print("\n5. Checking status...")
stdout, stderr = run_ssh("pm2 list --no-color | grep cora")
if stdout:
    print("Status:", stdout)

# 6. Test health
print("\n6. Testing health endpoint...")
stdout, stderr = run_ssh("curl -s http://localhost:8000/health")
if stdout:
    print("Health response:", stdout)
else:
    print("No response - checking logs...")
    stdout, stderr = run_ssh("pm2 logs cora --lines 20 --nostream --no-color")
    if stdout:
        print("Recent logs:")
        print(stdout)

# 7. Alternative: start directly
print("\n7. If PM2 failed, trying direct start...")
stdout, stderr = run_ssh("cd /var/www/cora && nohup python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 > /tmp/cora.log 2>&1 & echo Started")
print("Direct start:", stdout)

time.sleep(3)
stdout, stderr = run_ssh("curl -s http://localhost:8000/health")
print("Health after direct start:", stdout if stdout else "No response")

# 8. Check what's in the log
stdout, stderr = run_ssh("tail -20 /tmp/cora.log 2>/dev/null")
if stdout:
    print("\nApp log:")
    print(stdout)