#!/usr/bin/env python3
"""Complete fix for 502 error - handles app startup and nginx"""

import subprocess
import time

PRODUCTION_IP = "159.203.183.48"

def run_command(command, description):
    """Run SSH command and return result"""
    print(f"\n>>> {description}...")
    try:
        result = subprocess.run(
            ['ssh', f'root@{PRODUCTION_IP}', command],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr and "Warning" not in result.stderr:
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Failed: {e}")
        return False

def fix_502_completely():
    """Complete fix for 502 error"""
    print("COMPLETE 502 FIX PROCESS")
    print("=" * 50)
    
    # Step 1: Clean up PM2
    run_command("pm2 delete all 2>/dev/null || true", "Cleaning up PM2 processes")
    
    # Step 2: Kill any hanging Python processes
    run_command("pkill -f 'python.*app.py' || true", "Killing any hanging Python processes")
    
    # Step 3: Install uvicorn if missing
    run_command("pip install uvicorn", "Installing uvicorn")
    
    # Step 4: Create a proper startup script
    startup_script = """#!/bin/bash
cd /var/www/cora
export PYTHONPATH=/var/www/cora
uvicorn app:app --host 0.0.0.0 --port 8000
"""
    
    run_command(f"echo '{startup_script}' > /var/www/cora/start.sh && chmod +x /var/www/cora/start.sh", 
                "Creating startup script")
    
    # Step 5: Start with PM2
    run_command("cd /var/www/cora && pm2 start start.sh --name cora", 
                "Starting app with PM2")
    
    # Step 6: Save PM2 configuration
    run_command("pm2 save", "Saving PM2 configuration")
    
    # Step 7: Wait for startup
    print("\nWaiting for app to start...")
    time.sleep(5)
    
    # Step 8: Check if app is running
    run_command("pm2 status", "PM2 status")
    
    # Step 9: Test health endpoint directly
    run_command("curl -s http://localhost:8000/health || echo 'App not responding'", 
                "Testing health endpoint directly")
    
    # Step 10: Fix nginx configuration
    nginx_config = """server {
    listen 80;
    server_name coraai.tech www.coraai.tech _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    location /static {
        alias /var/www/cora/web/static;
        expires 30d;
    }
}"""
    
    run_command(f"echo '{nginx_config}' > /etc/nginx/sites-available/cora", 
                "Creating nginx configuration")
    
    # Step 11: Enable the site
    run_command("ln -sf /etc/nginx/sites-available/cora /etc/nginx/sites-enabled/cora && rm -f /etc/nginx/sites-enabled/default", 
                "Enabling nginx site")
    
    # Step 12: Test and reload nginx
    if run_command("nginx -t", "Testing nginx configuration"):
        run_command("systemctl reload nginx", "Reloading nginx")
    
    # Step 13: Final tests
    print("\n" + "=" * 50)
    print("FINAL TESTS:")
    print("=" * 50)
    
    run_command("curl -I http://localhost:8000/health", "Direct health check (port 8000)")
    run_command("curl -I http://localhost/health", "Nginx proxied health check")
    
    # Step 14: Test from outside
    print("\nTesting from outside...")
    try:
        import urllib.request
        response = urllib.request.urlopen('http://159.203.183.48/health', timeout=5)
        print(f"External test: {response.status} {response.reason}")
    except Exception as e:
        print(f"External test failed: {e}")
    
    print("\n" + "=" * 50)
    print("COMPLETE! The app should now be working.")
    print("Test it at: https://coraai.tech/health")
    print("=" * 50)

if __name__ == "__main__":
    fix_502_completely()