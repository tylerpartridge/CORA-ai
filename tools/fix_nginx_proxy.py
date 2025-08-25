#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/fix_nginx_proxy.py
🎯 PURPOSE: Check and fix nginx proxy configuration
🔗 IMPORTS: subprocess
📤 EXPORTS: Nginx fix status
"""

import subprocess

PRODUCTION_IP = "159.203.183.48"

def check_and_fix_nginx():
    """Check nginx configuration and fix proxy issues"""
    print("🔧 Checking and fixing nginx configuration...")
    print(f"Server: {PRODUCTION_IP}")
    print("-" * 50)
    
    commands = [
        # 1. Check current nginx config
        (
            "cat /etc/nginx/sites-available/default | grep -A 10 -B 5 'location'",
            "Current nginx configuration"
        ),
        
        # 2. Test if app is actually running on port 8000
        (
            "curl -s http://localhost:8000/health || echo 'App not responding on port 8000'",
            "Testing app on localhost:8000"
        ),
        
        # 3. Check what port the app is actually running on
        (
            "netstat -tlnp | grep python || echo 'No Python process listening'",
            "Checking Python process ports"
        ),
        
        # 4. Create proper nginx config
        (
            """cat > /etc/nginx/sites-available/cora << 'EOF'
server {
    listen 80;
    server_name coraai.tech www.coraai.tech;
    
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
        proxy_read_timeout 86400;
    }
    
    location /static {
        alias /var/www/cora/web/static;
        expires 30d;
    }
}
EOF""",
            "Creating proper nginx config"
        ),
        
        # 5. Enable the site
        (
            "ln -sf /etc/nginx/sites-available/cora /etc/nginx/sites-enabled/ && rm -f /etc/nginx/sites-enabled/default",
            "Enabling CORA site config"
        ),
        
        # 6. Test nginx config
        (
            "nginx -t",
            "Testing nginx configuration"
        ),
        
        # 7. Reload nginx
        (
            "systemctl reload nginx",
            "Reloading nginx"
        ),
        
        # 8. Check if PM2 app is running on correct port
        (
            "pm2 describe cora | grep -E 'script|args|interpreter'",
            "Checking PM2 app configuration"
        ),
        
        # 9. Restart app with explicit port
        (
            "cd /var/www/cora && pm2 delete cora; pm2 start app.py --name cora --interpreter python3 -- --port 8000",
            "Restarting app on port 8000"
        ),
        
        # 10. Final health check
        (
            "sleep 5 && curl -I http://localhost/health",
            "Testing health endpoint through nginx"
        )
    ]
    
    for command, description in commands:
        print(f"\n📌 {description}...")
        try:
            result = subprocess.run(
                ['ssh', f'root@{PRODUCTION_IP}', command],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr and "Warning" not in result.stderr:
                print(f"Error: {result.stderr}")
        except Exception as e:
            print(f"Failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Nginx configuration check complete")
    print("\nTesting endpoints:")
    print("1. curl https://coraai.tech/health")
    print("2. curl https://coraai.tech/api/status")

if __name__ == "__main__":
    check_and_fix_nginx()