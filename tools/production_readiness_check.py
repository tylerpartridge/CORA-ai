#!/usr/bin/env python3
"""
CORA Production Readiness Check
Comprehensive verification of all systems before deployment
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path
from datetime import datetime

class ProductionReadinessCheck:
    def __init__(self):
        self.checks = []
        self.failures = []
        self.warnings = []
        
    def add_check(self, name, result, details=""):
        """Add a check result"""
        check = {
            "name": name,
            "result": result,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.checks.append(check)
        
        if result == "FAIL":
            self.failures.append(check)
        elif result == "WARN":
            self.warnings.append(check)
            
        status_icon = "✅" if result == "PASS" else "⚠️" if result == "WARN" else "❌"
        print(f"{status_icon} {name}: {result}")
        if details:
            print(f"   {details}")
    
    def check_file_exists(self, filepath, description):
        """Check if a file exists"""
        path = Path(filepath)
        if path.exists():
            self.add_check(description, "PASS", f"File found: {path}")
        else:
            self.add_check(description, "FAIL", f"File missing: {path}")
    
    def check_command(self, command, description):
        """Check if a command runs successfully"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.add_check(description, "PASS", f"Command successful: {command}")
            else:
                self.add_check(description, "FAIL", f"Command failed: {command}")
        except Exception as e:
            self.add_check(description, "FAIL", f"Command error: {e}")
    
    def check_environment_variables(self):
        """Check critical environment variables"""
        self.add_check("Environment Variables Check", "INFO", "Checking .env files...")
        
        # Check for .env.production
        env_prod = Path(".env.production")
        if env_prod.exists():
            self.add_check("Production Environment File", "PASS", "Found .env.production")
            
            # Read and check for critical variables
            with open(env_prod, 'r') as f:
                content = f.read()
                
            critical_vars = [
                "DATABASE_URL",
                "SECRET_KEY", 
                "JWT_SECRET_KEY",
                "REDIS_URL",
                "OPENAI_API_KEY",
                "STRIPE_API_KEY"
            ]
            
            for var in critical_vars:
                if f"{var}=" in content and f"{var}=YOUR_" not in content:
                    self.add_check(f"Environment Variable: {var}", "PASS")
                else:
                    self.add_check(f"Environment Variable: {var}", "WARN", f"Missing or placeholder value")
        else:
            self.add_check("Production Environment File", "FAIL", "Missing .env.production")
    
    def check_docker_environment(self):
        """Check Docker environment"""
        self.add_check("Docker Environment Check", "INFO", "Checking Docker setup...")
        
        # Check Docker installation
        self.check_command("docker --version", "Docker Installation")
        
        # Check Docker Compose
        self.check_command("docker-compose --version", "Docker Compose Installation")
        
        # Check Docker daemon
        self.check_command("docker info", "Docker Daemon")
    
    def check_application_files(self):
        """Check critical application files"""
        self.add_check("Application Files Check", "INFO", "Checking critical files...")
        
        critical_files = [
            ("app.py", "Main Application"),
            ("requirements.txt", "Dependencies"),
            ("deployment/Dockerfile.production", "Production Dockerfile"),
            ("deployment/docker-compose.production.yml", "Production Compose"),
            ("config/env.production.template", "Environment Template")
        ]
        
        for filepath, description in critical_files:
            self.check_file_exists(filepath, description)
    
    def check_database_setup(self):
        """Check database configuration"""
        self.add_check("Database Setup Check", "INFO", "Checking database configuration...")
        
        # Check database files
        self.check_file_exists("cora.db", "SQLite Database")
        self.check_file_exists("schema/postgresql_schema.sql", "PostgreSQL Schema")
        
        # Check migration files
        migrations_dir = Path("schema/migrations")
        if migrations_dir.exists():
            migration_files = list(migrations_dir.glob("*.sql"))
            if migration_files:
                self.add_check("Database Migrations", "PASS", f"Found {len(migration_files)} migration files")
            else:
                self.add_check("Database Migrations", "WARN", "No migration files found")
        else:
            self.add_check("Database Migrations", "WARN", "Migrations directory not found")
    
    def check_security_configuration(self):
        """Check security configuration"""
        self.add_check("Security Configuration Check", "INFO", "Checking security setup...")
        
        # Check for security middleware
        security_files = [
            ("middleware/rate_limiting.py", "Rate Limiting"),
            ("middleware/error_handler.py", "Error Handling"),
            ("middleware/audit_logging.py", "Audit Logging"),
            ("utils/validation.py", "Input Validation")
        ]
        
        for filepath, description in security_files:
            self.check_file_exists(filepath, description)
    
    def check_monitoring_setup(self):
        """Check monitoring configuration"""
        self.add_check("Monitoring Setup Check", "INFO", "Checking monitoring configuration...")
        
        monitoring_files = [
            ("monitoring/docker-compose.yml", "Monitoring Stack"),
            ("monitoring/prometheus/prometheus.yml", "Prometheus Config"),
            ("monitoring/grafana/dashboards/", "Grafana Dashboards"),
            ("monitoring/alertmanager/alertmanager.yml", "AlertManager Config")
        ]
        
        for filepath, description in monitoring_files:
            self.check_file_exists(filepath, description)
    
    def check_api_endpoints(self):
        """Check API endpoints (if application is running)"""
        self.add_check("API Endpoints Check", "INFO", "Checking API endpoints...")
        
        try:
            # Try to connect to local development server
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                self.add_check("Health Endpoint", "PASS", "Local health endpoint responding")
                
                # Check other critical endpoints
                endpoints = [
                    ("/", "Home Page"),
                    ("/docs", "API Documentation"),
                    ("/api/status", "API Status")
                ]
                
                for endpoint, name in endpoints:
                    try:
                        response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
                        if response.status_code in [200, 302]:
                            self.add_check(f"Endpoint: {name}", "PASS")
                        else:
                            self.add_check(f"Endpoint: {name}", "WARN", f"Status: {response.status_code}")
                    except:
                        self.add_check(f"Endpoint: {name}", "WARN", "Not responding")
            else:
                self.add_check("Health Endpoint", "WARN", f"Status: {response.status_code}")
        except:
            self.add_check("Health Endpoint", "WARN", "Local server not running")
    
    def check_feature_completeness(self):
        """Check feature completeness"""
        self.add_check("Feature Completeness Check", "INFO", "Checking feature implementation...")
        
        # Core features
        core_features = [
            ("routes/auth_coordinator.py", "Authentication"),
            ("routes/onboarding_routes.py", "Onboarding"),
            ("routes/dashboard_routes.py", "Dashboard"),
            ("routes/expenses.py", "Expense Tracking"),
            ("routes/profit_intelligence.py", "Profit Intelligence"),
            ("routes/analytics.py", "User Analytics"),
            ("services/email_service.py", "Email Service"),
            ("services/stripe_service.py", "Payment Processing")
        ]
        
        for filepath, description in core_features:
            self.check_file_exists(filepath, description)
    
    def check_performance_optimization(self):
        """Check performance optimization"""
        self.add_check("Performance Optimization Check", "INFO", "Checking performance features...")
        
        performance_files = [
            ("utils/query_optimizer.py", "Query Optimization"),
            ("utils/materialized_views.py", "Materialized Views"),
            ("middleware/response_optimization.py", "Response Optimization"),
            ("utils/redis_manager.py", "Redis Caching")
        ]
        
        for filepath, description in performance_files:
            self.check_file_exists(filepath, description)
    
    def generate_report(self):
        """Generate comprehensive readiness report"""
        total_checks = len(self.checks)
        passed_checks = len([c for c in self.checks if c["result"] == "PASS"])
        failed_checks = len(self.failures)
        warning_checks = len(self.warnings)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_checks": total_checks,
                "passed": passed_checks,
                "failed": failed_checks,
                "warnings": warning_checks,
                "readiness_percentage": (passed_checks / total_checks * 100) if total_checks > 0 else 0
            },
            "checks": self.checks,
            "failures": self.failures,
            "warnings": self.warnings
        }
        
        # Save report
        report_file = Path(f"production_readiness_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("📊 PRODUCTION READINESS SUMMARY")
        print("="*60)
        print(f"Total Checks: {total_checks}")
        print(f"✅ Passed: {passed_checks}")
        print(f"⚠️  Warnings: {warning_checks}")
        print(f"❌ Failed: {failed_checks}")
        print(f"📈 Readiness: {report['summary']['readiness_percentage']:.1f}%")
        print("="*60)
        
        if failed_checks == 0:
            print("🎉 CORA is ready for production deployment!")
        else:
            print(f"⚠️  {failed_checks} issues need to be resolved before deployment")
            
        if warning_checks > 0:
            print(f"ℹ️  {warning_checks} warnings to review")
            
        print(f"📄 Detailed report saved to: {report_file}")
        
        return report
    
    def run_all_checks(self):
        """Run all production readiness checks"""
        print("🔍 CORA Production Readiness Check")
        print("="*50)
        
        # Run all check categories
        self.check_environment_variables()
        self.check_docker_environment()
        self.check_application_files()
        self.check_database_setup()
        self.check_security_configuration()
        self.check_monitoring_setup()
        self.check_api_endpoints()
        self.check_feature_completeness()
        self.check_performance_optimization()
        
        # Generate and return report
        return self.generate_report()

def main():
    """Main function"""
    checker = ProductionReadinessCheck()
    report = checker.run_all_checks()
    
    # Exit with appropriate code
    if report["summary"]["failed"] == 0:
        print("\n✅ All critical checks passed!")
        sys.exit(0)
    else:
        print(f"\n❌ {report['summary']['failed']} critical issues found!")
        sys.exit(1)

if __name__ == "__main__":
    main()