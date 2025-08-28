# 🚀 CORA Deployment Guide

## Quick Deploy to DigitalOcean

### 1. Prepare Your Code
```bash
# Make sure everything is committed
python git_smart.py "Ready for deployment"

# Push to GitHub
git push origin main
```

### 2. Create Droplet
- Go to DigitalOcean
- Create new Droplet
- Choose: Ubuntu 22.04
- Size: Basic, $6/month (1GB RAM)
- Region: NYC or SFO
- Add your SSH key

### 3. Initial Server Setup
```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Update system
apt update && apt upgrade -y

# Install Python and essentials
apt install python3-pip python3-venv nginx -y

# Create app user
adduser cora
usermod -aG sudo cora
su - cora
```

### 4. Deploy Application
```bash
# Clone your repo
git clone https://github.com/yourusername/cora.git
cd cora

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and edit environment
cp .env.example .env
nano .env  # Add your SECRET_KEY
```

### 5. Setup Systemd Service
Create `/etc/systemd/system/cora.service`:
```ini
[Unit]
Description=CORA AI FastAPI app
After=network.target

[Service]
Type=exec
User=cora
WorkingDirectory=/home/cora/cora
Environment="PATH=/home/cora/cora/venv/bin"
ExecStart=/home/cora/cora/venv/bin/gunicorn app:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

### 6. Configure Nginx
Create `/etc/nginx/sites-available/cora`:
```nginx
server {
    listen 80;
    server_name coraai.tech www.coraai.tech;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/cora/cora/static;
        expires 30d;
    }
}
```

### 7. Enable and Start
```bash
# Enable nginx site
ln -s /etc/nginx/sites-available/cora /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Start CORA service
systemctl enable cora
systemctl start cora
systemctl status cora
```

### 8. Point Domain
In your domain registrar:
- Add A record: @ → your-droplet-ip
- Add A record: www → your-droplet-ip

### 9. Add SSL (After DNS propagates)
```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d coraai.tech -d www.coraai.tech
```

### 10. Monitor
```bash
# Check logs
journalctl -u cora -f

# Check nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## 🎉 You're Live!

Visit https://coraai.tech and start collecting emails!

## Troubleshooting

### Port 8000 already in use?
```bash
sudo lsof -i :8000
kill -9 <PID>
```

### Changes not showing?
```bash
systemctl restart cora
systemctl restart nginx
```

### SSL not working?
Wait for DNS to propagate (can take up to 48 hours)

---

Remember: Keep it simple. Get it live. Iterate based on real feedback!TLS Renewal: See OPERATIONS.md for TLS renewal steps (renew before Sep 19, 2025).
