#!/usr/bin/env python3
"""Direct start without Unicode issues"""

import subprocess

PRODUCTION_IP = "159.203.183.48"

commands = [
    # Check PM2 list
    "pm2 list --no-color",
    
    # Check if uvicorn is installed
    "which uvicorn || pip install uvicorn",
    
    # Try to start directly with Python
    "cd /var/www/cora && python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 > /tmp/cora_start.log 2>&1 & echo $! > /tmp/cora.pid",
    
    # Wait a bit
    "sleep 3",
    
    # Check if it started
    "cat /tmp/cora_start.log | tail -20",
    
    # Check if process is running
    "ps -p $(cat /tmp/cora.pid 2>/dev/null) || echo 'Process not running'",
    
    # Test health endpoint
    "curl -s http://localhost:8000/health || echo 'Still not responding'",
    
    # If not working, check imports
    "cd /var/www/cora && python3 -c 'import app' 2>&1 | head -20"
]

for cmd in commands:
    print(f"\nRunning: {cmd[:50]}...")
    result = subprocess.run(
        ['ssh', f'root@{PRODUCTION_IP}', cmd],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr and "Warning" not in result.stderr:
        print(f"Error: {result.stderr}")