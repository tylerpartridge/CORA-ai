# INFRASTRUCTURE

Last verified: 2025-08-25 UTC

## Overview
FastAPI monolith served by uvicorn (systemd) on a DigitalOcean Ubuntu host. nginx terminates HTTP(S) and proxies to the app on :8000.

## Domains & TLS
- Domain: coraai.tech
- TLS: nginx active on :443
  - Certificate path: `/etc/ssl/certs/coraai.tech.crt`
  - Key path: `/etc/ssl/private/coraai.tech.key`
  - Current validity: notBefore=Jun 28 2025, notAfter=Sep 26 2025  
    👉 Renew before **Sep 19, 2025** to be safe.

## Hosts / OS
- Ubuntu 24.10 (prod)
- System service: `cora.service` (uvicorn)

## Runtime / Ports
- App: 0.0.0.0:8000 (uvicorn via systemd)
- Frontend proxy: nginx on :80 and :443

## Runtime / Proxy (nginx → uvicorn)
- **nginx**: :80 / :443
- **app**: uvicorn on 127.0.0.1:8000 (via `cora.service`)
- **vhost file**: `/etc/nginx/sites-available/coraai.tech` (enabled at `/etc/nginx/sites-enabled/coraai.tech`)
- **active snippet**:

server {
listen 80;
server_name coraai.tech www.coraai.tech
;
location / {
proxy_pass http://127.0.0.1:8000
;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
}
}

server {
listen 443 ssl;
server_name coraai.tech www.coraai.tech
;
ssl_certificate /etc/ssl/certs/coraai.tech.crt;
ssl_certificate_key /etc/ssl/private/coraai.tech.key;
location / {
proxy_pass http://127.0.0.1:8000
;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto https;
}
}
