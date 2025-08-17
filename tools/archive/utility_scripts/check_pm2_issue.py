#!/usr/bin/env python3
import subprocess
import os

PRODUCTION_IP = "159.203.183.48"

commands = [
    "pm2 list",
    "pm2 logs cora --err --lines 20 --nostream",
    "ps aux | grep uvicorn | grep -v grep",
    "netstat -tlnp | grep 8000",
    "cd /var/www/cora && ./venv/bin/python app.py &",
    "sleep 3",
    "curl -s http://localhost:8000/health"
]

for cmd in commands:
    print(f"\n>>> {cmd}")
    os.system(f'ssh root@{PRODUCTION_IP} "{cmd}"')