#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/infrastructure_setup.py
🎯 PURPOSE: Automated infrastructure setup for production scalability
🔗 IMPORTS: subprocess, yaml, json, os, pathlib
📤 EXPORTS: setup_redis, setup_monitoring, setup_load_balancer, setup_cdn
"""

import subprocess
import yaml
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InfrastructureSetup:
    def __init__(self, config_file: str = "infrastructure_config.yaml"):
        """Initialize infrastructure setup"""
        self.config_file = Path(config_file)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load infrastructure configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Default configuration
            return {
                'redis': {
                    'enabled': True,
                    'host': 'localhost',
                    'port': 6379,
                    'password': None,
                    'db': 0
                },
                'monitoring': {
                    'enabled': True,
                    'sentry_dsn': os.getenv('SENTRY_DSN'),
                    'prometheus_port': 9090,
                    'grafana_port': 3000
                },
                'load_balancer': {
                    'enabled': False,
                    'type': 'nginx',
                    'upstream_servers': ['localhost:8000']
                },
                'cdn': {
                    'enabled': False,
                    'provider': 'cloudflare',
                    'static_domain': 'static.coraai.tech'
                },
                'database': {
                    'type': 'sqlite',  # Will be PostgreSQL in production
                    'pool_size': 20,
                    'max_overflow': 30
                }
            }
    
    def setup_redis(self) -> bool:
        """Setup Redis for caching and session storage"""
        try:
            logger.info("Setting up Redis infrastructure...")
            
            # Create Redis configuration
            redis_config = {
                'redis': {
                    'host': self.config['redis']['host'],
                    'port': self.config['redis']['port'],
                    'password': self.config['redis']['password'],
                    'db': self.config['redis']['db'],
                    'max_connections': 50,
                    'connection_timeout': 5,
                    'retry_on_timeout': True
                }
            }
            
            # Save Redis configuration
            redis_config_file = Path("config/redis_config.json")
            redis_config_file.parent.mkdir(exist_ok=True)
            
            with open(redis_config_file, 'w') as f:
                json.dump(redis_config, f, indent=2)
            
            # Create Redis service
            self._create_redis_service()
            
            # Update application configuration
            self._update_app_config_for_redis()
            
            logger.info("Redis infrastructure setup complete")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Redis: {str(e)}")
            return False
    
    def _create_redis_service(self):
        """Create Redis service configuration"""
        redis_service = {
            'name': 'cora-redis',
            'script': 'redis-server',
            'instances': 1,
            'env': {
                'NODE_ENV': 'production'
            }
        }
        
        # Save PM2 configuration
        pm2_config = {
            'apps': [redis_service]
        }
        
        with open('ecosystem.config.js', 'w') as f:
            f.write(f"module.exports = {json.dumps(pm2_config, indent=2)}")
    
    def _update_app_config_for_redis(self):
        """Update application configuration to use Redis"""
        # Add Redis dependencies to requirements
        requirements_file = Path("requirements.txt")
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                requirements = f.read()
            
            if 'redis' not in requirements:
                with open(requirements_file, 'a') as f:
                    f.write('\nredis==5.0.1\n')
        
        # Create Redis connection module
        redis_conn = '''
import redis
import os
import json
from typing import Optional

class RedisManager:
    def __init__(self):
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        try:
            config_file = Path("config/redis_config.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)['redis']
            else:
                config = {
                    'host': os.getenv('REDIS_HOST', 'localhost'),
                    'port': int(os.getenv('REDIS_PORT', 6379)),
                    'password': os.getenv('REDIS_PASSWORD'),
                    'db': int(os.getenv('REDIS_DB', 0))
                }
            
            self.redis_client = redis.Redis(
                host=config['host'],
                port=config['port'],
                password=config['password'],
                db=config['db'],
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established")
            
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        if self.redis_client:
            try:
                return self.redis_client.get(key)
            except Exception as e:
                logger.error(f"Redis get error: {str(e)}")
        return None
    
    def set(self, key: str, value: str, expire: int = 3600) -> bool:
        """Set value in Redis with expiration"""
        if self.redis_client:
            try:
                return self.redis_client.setex(key, expire, value)
            except Exception as e:
                logger.error(f"Redis set error: {str(e)}")
        return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if self.redis_client:
            try:
                return bool(self.redis_client.delete(key))
            except Exception as e:
                logger.error(f"Redis delete error: {str(e)}")
        return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        if self.redis_client:
            try:
                return bool(self.redis_client.exists(key))
            except Exception as e:
                logger.error(f"Redis exists error: {str(e)}")
        return False

# Global Redis instance
redis_manager = RedisManager()
'''
        
        # Save Redis connection module
        redis_file = Path("utils/redis_manager.py")
        redis_file.parent.mkdir(exist_ok=True)
        
        with open(redis_file, 'w') as f:
            f.write(redis_conn)
    
    def setup_monitoring(self) -> bool:
        """Setup comprehensive monitoring infrastructure"""
        try:
            logger.info("Setting up monitoring infrastructure...")
            
            # Create monitoring configuration
            monitoring_config = {
                'sentry': {
                    'enabled': bool(self.config['monitoring']['sentry_dsn']),
                    'dsn': self.config['monitoring']['sentry_dsn']
                },
                'prometheus': {
                    'enabled': self.config['monitoring']['enabled'],
                    'port': self.config['monitoring']['prometheus_port']
                },
                'grafana': {
                    'enabled': self.config['monitoring']['enabled'],
                    'port': self.config['monitoring']['grafana_port']
                },
                'health_checks': {
                    'enabled': True,
                    'endpoints': [
                        '/api/health',
                        '/api/expenses/categories',
                        '/api/auth/login'
                    ]
                }
            }
            
            # Save monitoring configuration
            monitoring_file = Path("config/monitoring_config.json")
            monitoring_file.parent.mkdir(exist_ok=True)
            
            with open(monitoring_file, 'w') as f:
                json.dump(monitoring_config, f, indent=2)
            
            # Create monitoring middleware
            self._create_monitoring_middleware()
            
            # Create health check endpoints
            self._create_health_checks()
            
            # Create monitoring dashboard
            self._create_monitoring_dashboard()
            
            logger.info("✅ Monitoring infrastructure setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup monitoring: {str(e)}")
            return False
    
    def _create_monitoring_middleware(self):
        """Create monitoring middleware"""
        monitoring_middleware = '''
import time
import logging
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, generate_latest
import psutil
import os

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')
ACTIVE_CONNECTIONS = Counter('active_connections', 'Active database connections')
MEMORY_USAGE = Histogram('memory_usage_bytes', 'Memory usage in bytes')
CPU_USAGE = Histogram('cpu_usage_percent', 'CPU usage percentage')

logger = logging.getLogger(__name__)

async def monitoring_middleware(request: Request, call_next):
    """Monitoring middleware for metrics collection"""
    start_time = time.time()
    
    # Record request start
    method = request.method
    endpoint = request.url.path
    
    try:
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=response.status_code).inc()
        REQUEST_LATENCY.observe(duration)
        
        # Record system metrics
        MEMORY_USAGE.observe(psutil.virtual_memory().used)
        CPU_USAGE.observe(psutil.cpu_percent())
        
        return response
        
    except Exception as e:
        # Record error metrics
        duration = time.time() - start_time
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=500).inc()
        REQUEST_LATENCY.observe(duration)
        logger.error(f"Request failed: {str(e)}")
        raise

def get_metrics():
    """Get Prometheus metrics"""
    return generate_latest()

def get_system_health():
    """Get system health metrics"""
    return {
        'memory_usage': psutil.virtual_memory().percent,
        'cpu_usage': psutil.cpu_percent(),
        'disk_usage': psutil.disk_usage('/').percent,
        'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
    }
'''
        
        # Save monitoring middleware
        monitoring_file = Path("middleware/monitoring.py")
        monitoring_file.parent.mkdir(exist_ok=True)
        
        with open(monitoring_file, 'w') as f:
            f.write(monitoring_middleware)
    
    def _create_health_checks(self):
        """Create health check endpoints"""
        health_checks = '''
from fastapi import APIRouter, HTTPException
from middleware.monitoring import get_system_health, get_metrics
from utils.redis_manager import redis_manager
import sqlite3
import os

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with all components"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }
    
    # Database health
    try:
        db_path = "data/cora.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            health_status["components"]["database"] = "healthy"
        else:
            health_status["components"]["database"] = "missing"
    except Exception as e:
        health_status["components"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Redis health
    try:
        if redis_manager.redis_client and redis_manager.redis_client.ping():
            health_status["components"]["redis"] = "healthy"
        else:
            health_status["components"]["redis"] = "unavailable"
    except Exception as e:
        health_status["components"]["redis"] = f"error: {str(e)}"
    
    # System health
    try:
        system_health = get_system_health()
        health_status["components"]["system"] = system_health
    except Exception as e:
        health_status["components"]["system"] = f"error: {str(e)}"
    
    return health_status

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=get_metrics(), media_type="text/plain")

@router.get("/health/ready")
async def readiness_check():
    """Readiness check for load balancers"""
    # Check if all critical services are ready
    try:
        # Database check
        db_path = "data/cora.db"
        if not os.path.exists(db_path):
            raise HTTPException(status_code=503, detail="Database not ready")
        
        # Redis check (optional)
        if redis_manager.redis_client:
            redis_manager.redis_client.ping()
        
        return {"status": "ready"}
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")
'''
        
        # Save health checks
        health_file = Path("routes/health.py")
        health_file.parent.mkdir(exist_ok=True)
        
        with open(health_file, 'w') as f:
            f.write(health_checks)
    
    def _create_monitoring_dashboard(self):
        """Create monitoring dashboard configuration"""
        dashboard_config = {
            'title': 'CORA System Monitoring',
            'panels': [
                {
                    'title': 'Request Rate',
                    'type': 'graph',
                    'targets': [
                        {'expr': 'rate(http_requests_total[5m])', 'legendFormat': '{{method}} {{endpoint}}'}
                    ]
                },
                {
                    'title': 'Response Time',
                    'type': 'graph',
                    'targets': [
                        {'expr': 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))', 'legendFormat': '95th percentile'}
                    ]
                },
                {
                    'title': 'Error Rate',
                    'type': 'graph',
                    'targets': [
                        {'expr': 'rate(http_requests_total{status=~"5.."}[5m])', 'legendFormat': '5xx errors'}
                    ]
                },
                {
                    'title': 'System Resources',
                    'type': 'graph',
                    'targets': [
                        {'expr': 'memory_usage_bytes', 'legendFormat': 'Memory Usage'},
                        {'expr': 'cpu_usage_percent', 'legendFormat': 'CPU Usage'}
                    ]
                }
            ]
        }
        
        # Save dashboard configuration
        dashboard_file = Path("config/grafana_dashboard.json")
        dashboard_file.parent.mkdir(exist_ok=True)
        
        with open(dashboard_file, 'w') as f:
            json.dump(dashboard_config, f, indent=2)
    
    def setup_load_balancer(self) -> bool:
        """Setup load balancer configuration"""
        try:
            logger.info("Setting up load balancer configuration...")
            
            # Create Nginx configuration
            nginx_config = '''
upstream cora_backend {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
    keepalive 32;
}

server {
    listen 80;
    server_name coraai.tech www.coraai.tech;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name coraai.tech www.coraai.tech;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/coraai.tech/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/coraai.tech/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    
    # Static files
    location /static/ {
        alias /root/cora/web/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API endpoints with rate limiting
    location /api/auth/login {
        limit_req zone=login burst=3 nodelay;
        proxy_pass http://cora_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://cora_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health checks
    location /health {
        proxy_pass http://cora_backend;
        access_log off;
    }
    
    # Main application
    location / {
        proxy_pass http://cora_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
'''
            
            # Save Nginx configuration
            nginx_file = Path("config/nginx.conf")
            nginx_file.parent.mkdir(exist_ok=True)
            
            with open(nginx_file, 'w') as f:
                f.write(nginx_config)
            
            logger.info("✅ Load balancer configuration created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup load balancer: {str(e)}")
            return False
    
    def setup_cdn(self) -> bool:
        """Setup CDN configuration for static assets"""
        try:
            logger.info("Setting up CDN configuration...")
            
            # Create CDN configuration
            cdn_config = {
                'provider': self.config['cdn']['provider'],
                'static_domain': self.config['cdn']['static_domain'],
                'assets': {
                    'images': '/web/static/images/',
                    'css': '/web/static/css/',
                    'js': '/web/static/js/',
                    'fonts': '/web/static/fonts/'
                },
                'cache_policy': {
                    'images': '1 year',
                    'css': '1 month',
                    'js': '1 month',
                    'fonts': '1 year'
                }
            }
            
            # Save CDN configuration
            cdn_file = Path("config/cdn_config.json")
            cdn_file.parent.mkdir(exist_ok=True)
            
            with open(cdn_file, 'w') as f:
                json.dump(cdn_config, f, indent=2)
            
            # Create static asset optimization script
            self._create_static_optimization()
            
            logger.info("✅ CDN configuration created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup CDN: {str(e)}")
            return False
    
    def _create_static_optimization(self):
        """Create static asset optimization script"""
        optimization_script = '''
#!/usr/bin/env python3
"""
Static asset optimization for CDN deployment
"""

import os
import shutil
from pathlib import Path
from PIL import Image
import subprocess

def optimize_images():
    """Optimize images for web delivery"""
    static_dir = Path("web/static")
    images_dir = static_dir / "images"
    
    if not images_dir.exists():
        return
    
    for image_file in images_dir.rglob("*.png"):
        try:
            with Image.open(image_file) as img:
                # Convert to WebP if possible
                webp_file = image_file.with_suffix('.webp')
                img.save(webp_file, 'WEBP', quality=85, optimize=True)
                print(f"Optimized: {image_file} -> {webp_file}")
        except Exception as e:
            print(f"Failed to optimize {image_file}: {str(e)}")

def minify_css():
    """Minify CSS files"""
    css_dir = Path("web/static/css")
    if not css_dir.exists():
        return
    
    for css_file in css_dir.glob("*.css"):
        try:
            # Simple CSS minification (remove comments and whitespace)
            with open(css_file, 'r') as f:
                content = f.read()
            
            # Remove comments
            import re
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            
            # Remove extra whitespace
            content = re.sub(r'\\s+', ' ', content)
            content = re.sub(r'\\s*{\\s*', '{', content)
            content = re.sub(r'\\s*}\\s*', '}', content)
            
            # Save minified version
            minified_file = css_file.with_suffix('.min.css')
            with open(minified_file, 'w') as f:
                f.write(content)
            
            print(f"Minified: {css_file} -> {minified_file}")
            
        except Exception as e:
            print(f"Failed to minify {css_file}: {str(e)}")

def create_manifest():
    """Create asset manifest for versioning"""
    manifest = {}
    static_dir = Path("web/static")
    
    for asset_file in static_dir.rglob("*"):
        if asset_file.is_file():
            relative_path = str(asset_file.relative_to(static_dir))
            # Use file modification time as version
            manifest[relative_path] = str(asset_file.stat().st_mtime)
    
    # Save manifest
    with open("web/static/manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print("Created asset manifest")

if __name__ == "__main__":
    optimize_images()
    minify_css()
    create_manifest()
    print("Static asset optimization complete")
'''
        
        # Save optimization script
        optimization_file = Path("tools/optimize_static.py")
        optimization_file.parent.mkdir(exist_ok=True)
        
        with open(optimization_file, 'w') as f:
            f.write(optimization_script)
    
    def setup_all(self) -> bool:
        """Setup all infrastructure components"""
        logger.info("🚀 Setting up complete infrastructure...")
        
        success = True
        
        # Setup Redis
        if self.config['redis']['enabled']:
            success &= self.setup_redis()
        
        # Setup monitoring
        if self.config['monitoring']['enabled']:
            success &= self.setup_monitoring()
        
        # Setup load balancer
        if self.config['load_balancer']['enabled']:
            success &= self.setup_load_balancer()
        
        # Setup CDN
        if self.config['cdn']['enabled']:
            success &= self.setup_cdn()
        
        if success:
            logger.info("✅ All infrastructure components setup complete")
        else:
            logger.error("❌ Some infrastructure components failed to setup")
        
        return success

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORA Infrastructure Setup")
    parser.add_argument("component", choices=["all", "redis", "monitoring", "load_balancer", "cdn"])
    parser.add_argument("--config", default="infrastructure_config.yaml", help="Configuration file")
    
    args = parser.parse_args()
    
    setup = InfrastructureSetup(args.config)
    
    if args.component == "all":
        success = setup.setup_all()
    elif args.component == "redis":
        success = setup.setup_redis()
    elif args.component == "monitoring":
        success = setup.setup_monitoring()
    elif args.component == "load_balancer":
        success = setup.setup_load_balancer()
    elif args.component == "cdn":
        success = setup.setup_cdn()
    
    if success:
        print(f"✅ {args.component} setup completed successfully")
    else:
        print(f"❌ {args.component} setup failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 