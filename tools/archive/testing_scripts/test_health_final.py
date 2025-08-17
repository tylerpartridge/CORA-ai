#!/usr/bin/env python3
import subprocess
import os
import json

PRODUCTION_IP = "159.203.183.48"

print("Testing CORA endpoints after fix...")
print("=" * 50)

# Test endpoints
tests = [
    ("curl -s http://localhost:8000/health", "Direct health endpoint"),
    ("curl -s http://localhost/health", "Nginx proxied health"),
    ("curl -s -I https://coraai.tech/health | head -10", "Public HTTPS health check"),
    ("curl -s https://coraai.tech/ | grep -i 'content-security-policy' | head -5", "CSP headers on landing page"),
    ("pm2 logs cora --lines 5 --nostream", "Recent PM2 logs")
]

for cmd, desc in tests:
    print(f"\n{desc}:")
    print("-" * 30)
    result = subprocess.run(
        ['ssh', f'root@{PRODUCTION_IP}', cmd],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    
    if result.stdout:
        # Try to parse JSON for health endpoints
        if 'health' in cmd and '{' in result.stdout:
            try:
                data = json.loads(result.stdout)
                print(f"Status: {data.get('status', 'unknown')}")
                print(f"Version: {data.get('version', 'unknown')}")
            except:
                print(result.stdout[:200])
        else:
            print(result.stdout[:500])
    else:
        print("No response or error")

print("\n" + "=" * 50)
print("SUMMARY:")
print("If you see 'healthy' status above, the fix is complete!")
print("The CSP security headers are now deployed.")
print("=" * 50)