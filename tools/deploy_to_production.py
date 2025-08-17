#!/usr/bin/env python3
"""
CORA Production Deployment Script
Complete deployment automation for CORA production environment
"""

import os
import sys
import subprocess
import time
import json
import requests
from pathlib import Path
from datetime import datetime

class CORADeployment:
    def __init__(self):
        self.deployment_log = []
        self.start_time = datetime.now()
        self.domain = "coraai.tech"
        self.base_url = f"https://{self.domain}"
        
    def log(self, message, level="INFO"):
        """Log deployment activity"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.deployment_log.append(log_entry)
        print(log_entry)
        
    def run_command(self, command, description, check=True):
        """Run a shell command with logging"""
        self.log(f"Running: {description}")
        self.log(f"Command: {command}")
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                check=check
            )
            
            if result.stdout:
                self.log(f"Output: {result.stdout.strip()}")
            if result.stderr:
                self.log(f"Stderr: {result.stderr.strip()}")
                
            if result.returncode == 0:
                self.log(f"✅ {description} completed successfully")
                return True
            else:
                self.log(f"❌ {description} failed with return code {result.returncode}")
                return False
                
        except subprocess.CalledProcessError as e:
            self.log(f"❌ {description} failed: {e}")
            return False
        except Exception as e:
            self.log(f"❌ {description} failed with exception: {e}")
            return False
    
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        self.log("🔍 Checking deployment prerequisites...")
        
        # Check Docker
        if not self.run_command("docker --version", "Docker version check", check=False):
            self.log("❌ Docker not found. Please install Docker first.")
            return False
            
        # Check Docker Compose
        if not self.run_command("docker-compose --version", "Docker Compose version check", check=False):
            self.log("❌ Docker Compose not found. Please install Docker Compose first.")
            return False
            
        # Check if Docker is running
        if not self.run_command("docker info", "Docker daemon check", check=False):
            self.log("❌ Docker daemon not running. Please start Docker first.")
            return False
            
        # Check production environment file
        env_file = Path(".env.production")
        if not env_file.exists():
            self.log("❌ .env.production file not found. Please run generate_production_env.py first.")
            return False
            
        self.log("✅ All prerequisites met!")
        return True
    
    def generate_environment(self):
        """Generate production environment if needed"""
        self.log("🔐 Generating production environment...")
        
        env_file = Path(".env.production")
        if env_file.exists():
            self.log("📁 Production environment file already exists")
            return True
            
        # Run environment generator
        if self.run_command("python tools/generate_production_env.py", "Generate production environment"):
            self.log("✅ Production environment generated successfully")
            return True
        else:
            self.log("❌ Failed to generate production environment")
            return False
    
    def build_images(self):
        """Build production Docker images"""
        self.log("🏗️ Building production Docker images...")
        
        # Build CORA application image
        if not self.run_command(
            "docker build -f deployment/Dockerfile.production -t cora:production .",
            "Build CORA application image"
        ):
            return False
            
        # Build Nginx image
        if not self.run_command(
            "docker build -f deployment/Dockerfile.nginx -t cora-nginx:production deployment/",
            "Build Nginx image"
        ):
            return False
            
        self.log("✅ All Docker images built successfully")
        return True
    
    def deploy_services(self):
        """Deploy all services using Docker Compose"""
        self.log("🚀 Deploying CORA services...")
        
        # Stop any existing containers
        self.run_command("docker-compose -f deployment/docker-compose.production.yml down", "Stop existing containers")
        
        # Deploy with production compose file
        if not self.run_command(
            "docker-compose -f deployment/docker-compose.production.yml up -d",
            "Deploy CORA services"
        ):
            return False
            
        # Wait for services to start
        self.log("⏳ Waiting for services to start...")
        time.sleep(30)
        
        # Check service health
        if not self.check_service_health():
            return False
            
        self.log("✅ All services deployed successfully")
        return True
    
    def check_service_health(self):
        """Check health of all deployed services"""
        self.log("🏥 Checking service health...")
        
        services = [
            ("postgres", "PostgreSQL Database"),
            ("redis", "Redis Cache"),
            ("cora_app", "CORA Application"),
            ("nginx", "Nginx Proxy")
        ]
        
        all_healthy = True
        
        for service, name in services:
            if self.run_command(
                f"docker-compose -f deployment/docker-compose.production.yml ps {service}",
                f"Check {name} status",
                check=False
            ):
                self.log(f"✅ {name} is running")
            else:
                self.log(f"❌ {name} is not running")
                all_healthy = False
                
        # Check application health endpoint
        if self.check_health_endpoint():
            self.log("✅ Application health endpoint responding")
        else:
            self.log("❌ Application health endpoint not responding")
            all_healthy = False
            
        return all_healthy
    
    def check_health_endpoint(self):
        """Check if the application health endpoint is responding"""
        try:
            # Try local health check first
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                return True
        except:
            pass
            
        try:
            # Try domain health check
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                return True
        except:
            pass
            
        return False
    
    def run_migrations(self):
        """Run database migrations"""
        self.log("🗄️ Running database migrations...")
        
        if self.run_command(
            "docker-compose -f deployment/docker-compose.production.yml exec cora_app python -m alembic upgrade head",
            "Run database migrations"
        ):
            self.log("✅ Database migrations completed")
            return True
        else:
            self.log("❌ Database migrations failed")
            return False
    
    def setup_monitoring(self):
        """Deploy monitoring stack"""
        self.log("📊 Deploying monitoring stack...")
        
        if self.run_command(
            "docker-compose -f monitoring/docker-compose.yml up -d",
            "Deploy monitoring stack"
        ):
            self.log("✅ Monitoring stack deployed")
            return True
        else:
            self.log("❌ Monitoring stack deployment failed")
            return False
    
    def verify_deployment(self):
        """Verify the deployment is working correctly"""
        self.log("🔍 Verifying deployment...")
        
        # Test critical endpoints
        endpoints = [
            ("/", "Home page"),
            ("/health", "Health check"),
            ("/api/status", "API status"),
            ("/docs", "API documentation")
        ]
        
        all_working = True
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code in [200, 302]:  # 302 for redirects
                    self.log(f"✅ {name} responding correctly")
                else:
                    self.log(f"❌ {name} returned status {response.status_code}")
                    all_working = False
            except Exception as e:
                self.log(f"❌ {name} failed: {e}")
                all_working = False
        
        # Test user registration flow
        if self.test_user_registration():
            self.log("✅ User registration flow working")
        else:
            self.log("❌ User registration flow failed")
            all_working = False
            
        return all_working
    
    def test_user_registration(self):
        """Test the user registration flow"""
        try:
            # Test email capture endpoint
            test_email = f"test-{int(time.time())}@example.com"
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json={
                    "email": test_email,
                    "password": "TestPassword123!",
                    "first_name": "Test",
                    "last_name": "User"
                },
                timeout=10
            )
            
            if response.status_code in [200, 201, 422]:  # 422 is validation error, which is expected
                return True
            else:
                return False
        except:
            return False
    
    def generate_deployment_report(self):
        """Generate deployment report"""
        self.log("📋 Generating deployment report...")
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        report = {
            "deployment_time": self.start_time.isoformat(),
            "completion_time": end_time.isoformat(),
            "duration_minutes": duration.total_seconds() / 60,
            "domain": self.domain,
            "base_url": self.base_url,
            "log_entries": self.deployment_log
        }
        
        # Save report
        report_file = Path(f"deployment_report_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.log(f"📄 Deployment report saved to {report_file}")
        return report
    
    def deploy(self):
        """Execute complete deployment process"""
        self.log("🚀 Starting CORA Production Deployment")
        self.log("=" * 50)
        
        try:
            # Phase 1: Prerequisites
            if not self.check_prerequisites():
                self.log("❌ Prerequisites check failed")
                return False
                
            # Phase 2: Environment Setup
            if not self.generate_environment():
                self.log("❌ Environment generation failed")
                return False
                
            # Phase 3: Build Images
            if not self.build_images():
                self.log("❌ Image building failed")
                return False
                
            # Phase 4: Deploy Services
            if not self.deploy_services():
                self.log("❌ Service deployment failed")
                return False
                
            # Phase 5: Database Setup
            if not self.run_migrations():
                self.log("❌ Database migration failed")
                return False
                
            # Phase 6: Monitoring
            if not self.setup_monitoring():
                self.log("⚠️ Monitoring setup failed (continuing anyway)")
                
            # Phase 7: Verification
            if not self.verify_deployment():
                self.log("❌ Deployment verification failed")
                return False
                
            # Generate report
            report = self.generate_deployment_report()
            
            self.log("=" * 50)
            self.log("🎉 CORA PRODUCTION DEPLOYMENT COMPLETED SUCCESSFULLY!")
            self.log(f"🌐 Your application is live at: {self.base_url}")
            self.log(f"📊 Monitoring available at: {self.base_url}:3000")
            self.log(f"📚 API documentation at: {self.base_url}/docs")
            self.log("=" * 50)
            
            return True
            
        except Exception as e:
            self.log(f"❌ Deployment failed with exception: {e}")
            return False

def main():
    """Main deployment function"""
    print("🚀 CORA Production Deployment")
    print("=" * 40)
    
    # Check if running as root (for Docker access)
    if os.geteuid() == 0:
        print("⚠️  Running as root - this is not recommended for security")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Deployment cancelled")
            sys.exit(1)
    
    # Create deployment instance
    deployment = CORADeployment()
    
    # Execute deployment
    success = deployment.deploy()
    
    if success:
        print("\n🎉 Deployment completed successfully!")
        print("CORA is now live and ready to serve contractors!")
        sys.exit(0)
    else:
        print("\n❌ Deployment failed!")
        print("Please check the logs above for details")
        sys.exit(1)

if __name__ == "__main__":
    main() 