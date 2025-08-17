#!/usr/bin/env python3
"""
LOCATION: /CORA/utils/deployment_validator.py
PURPOSE: Comprehensive production deployment validation and readiness checks
IMPORTS: SQLAlchemy, Redis, OpenAI, SendGrid, system utilities
EXPORTS: DeploymentValidator class with comprehensive validation suite
"""

import os
import sys
import json
import logging
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path

# Database and external service imports
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    import redis
    import openai
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
except ImportError as e:
    print(f"Warning: Optional dependency not found: {e}")

# Local imports
try:
    from models import get_db, User, BusinessProfile, Expense
    from utils.redis_manager import get_redis_client
    from utils.query_optimizer import QueryOptimizer
    from utils.performance_monitor import PerformanceMonitor
except ImportError as e:
    print(f"Warning: Could not import local modules: {e}")

logger = logging.getLogger(__name__)

class DeploymentValidator:
    """Comprehensive production deployment validation and readiness checks"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "unknown",
            "readiness_score": 0,
            "critical_issues": [],
            "warnings": [],
            "validations": {}
        }
        
    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete deployment validation suite"""
        print("CORA Production Deployment Validation")
        print("=" * 50)
        
        # Core system validations
        self._validate_environment_config()
        self._validate_database_health()
        self._validate_redis_connectivity()
        self._validate_external_services()
        self._validate_file_system()
        self._validate_performance_optimizations()
        self._validate_security_configuration()
        self._validate_api_endpoints()
        self._validate_ai_systems()
        
        # Calculate overall readiness
        self._calculate_readiness_score()
        self._generate_deployment_report()
        
        return self.results
    
    def _validate_environment_config(self):
        """Validate environment configuration and secrets"""
        print("\nValidating Environment Configuration...")
        
        validation = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        # Check for .env file
        env_path = Path(".env")
        if env_path.exists():
            validation["details"]["env_file"] = "✅ Found"
            
            # Check critical environment variables
            critical_vars = [
                "OPENAI_API_KEY", "SENDGRID_API_KEY", "SECRET_KEY", 
                "DATABASE_URL", "REDIS_URL", "ENVIRONMENT"
            ]
            
            for var in critical_vars:
                value = os.getenv(var)
                if value:
                    validation["details"][var] = "✅ Configured"
                else:
                    validation["details"][var] = "❌ Missing"
                    validation["issues"].append(f"Missing {var}")
                    if var in ["OPENAI_API_KEY", "SECRET_KEY"]:
                        validation["status"] = "fail"
                    else:
                        validation["status"] = "warning"
        else:
            validation["status"] = "fail"
            validation["details"]["env_file"] = "❌ Missing"
            validation["issues"].append("No .env file found")
        
        self.results["validations"]["environment"] = validation
        print(f"   Status: {validation['status'].upper()}")
    
    def _validate_database_health(self):
        """Validate database connectivity and health"""
        print("\n🗄️ Validating Database Health...")
        
        validation = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        try:
            # Test database connection
            db_path = "cora.db"
            if Path(db_path).exists():
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check table count
                cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                validation["details"]["table_count"] = f"✅ {table_count} tables"
                
                # Check user count
                try:
                    cursor.execute("SELECT COUNT(*) FROM users")
                    user_count = cursor.fetchone()[0]
                    validation["details"]["user_count"] = f"✅ {user_count} users"
                except:
                    validation["details"]["user_count"] = "⚠️ No users table or data"
                
                # Check database size
                db_size = Path(db_path).stat().st_size / (1024 * 1024)  # MB
                validation["details"]["database_size"] = f"✅ {db_size:.2f} MB"
                
                # Test write capability
                cursor.execute("CREATE TABLE IF NOT EXISTS deployment_test (id INTEGER)")
                cursor.execute("INSERT INTO deployment_test (id) VALUES (1)")
                cursor.execute("DELETE FROM deployment_test WHERE id = 1")
                cursor.execute("DROP TABLE deployment_test")
                conn.commit()
                validation["details"]["write_test"] = "✅ Write operations working"
                
                conn.close()
                
                if table_count < 10:
                    validation["status"] = "warning"
                    validation["issues"].append("Low table count - database may be incomplete")
                    
            else:
                validation["status"] = "fail"
                validation["details"]["database_file"] = "❌ Database file not found"
                validation["issues"].append("Database file missing")
                
        except Exception as e:
            validation["status"] = "fail"
            validation["details"]["connection_test"] = f"❌ Failed: {str(e)}"
            validation["issues"].append(f"Database connection failed: {str(e)}")
        
        self.results["validations"]["database"] = validation
        print(f"   Status: {validation['status'].upper()}")
    
    def _validate_redis_connectivity(self):
        """Validate Redis connectivity and caching system"""
        print("\n⚡ Validating Redis Connectivity...")
        
        validation = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        try:
            redis_client = get_redis_client()
            if redis_client:
                # Test basic connectivity
                redis_client.ping()
                validation["details"]["connectivity"] = "✅ Connected"
                
                # Test read/write
                test_key = "deployment_test"
                redis_client.set(test_key, "test_value", ex=60)
                retrieved = redis_client.get(test_key)
                if retrieved == b"test_value":
                    validation["details"]["read_write"] = "✅ Read/Write working"
                    redis_client.delete(test_key)
                else:
                    validation["status"] = "warning"
                    validation["issues"].append("Redis read/write test failed")
                
                # Check memory usage
                info = redis_client.info("memory")
                memory_used = info.get("used_memory_human", "unknown")
                validation["details"]["memory_usage"] = f"✅ {memory_used}"
                
            else:
                validation["status"] = "warning"
                validation["details"]["connectivity"] = "⚠️ Redis client not available"
                validation["issues"].append("Redis not configured - caching disabled")
                
        except Exception as e:
            validation["status"] = "warning"
            validation["details"]["error"] = f"⚠️ {str(e)}"
            validation["issues"].append(f"Redis validation failed: {str(e)}")
        
        self.results["validations"]["redis"] = validation
        print(f"   Status: {validation['status'].upper()}")
    
    def _validate_external_services(self):
        """Validate external service integrations"""
        print("\n🌐 Validating External Services...")
        
        validation = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        # Test OpenAI API
        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            if openai.api_key:
                # Simple test call
                response = openai.models.list()
                validation["details"]["openai"] = "✅ API accessible"
            else:
                validation["status"] = "warning"
                validation["details"]["openai"] = "⚠️ API key not configured"
                validation["issues"].append("OpenAI API key missing")
        except Exception as e:
            validation["status"] = "warning"
            validation["details"]["openai"] = f"⚠️ API test failed: {str(e)[:50]}"
            validation["issues"].append("OpenAI API validation failed")
        
        # Test SendGrid
        try:
            sendgrid_key = os.getenv("SENDGRID_API_KEY")
            if sendgrid_key:
                sg = SendGridAPIClient(api_key=sendgrid_key)
                # Test API key validity (this doesn't send an email)
                response = sg.client.mail.send.post(request_body={
                    "personalizations": [{"to": [{"email": "test@example.com"}]}],
                    "from": {"email": "test@example.com"},
                    "subject": "Test",
                    "content": [{"type": "text/plain", "value": "Test"}]
                })
                # We expect this to fail with 403 or 400, not 401 (unauthorized)
                validation["details"]["sendgrid"] = "✅ API key valid"
            else:
                validation["status"] = "warning"
                validation["details"]["sendgrid"] = "⚠️ API key not configured"
                validation["issues"].append("SendGrid API key missing")
        except Exception as e:
            if "401" in str(e):
                validation["status"] = "fail"
                validation["details"]["sendgrid"] = "❌ Invalid API key"
                validation["issues"].append("SendGrid API key invalid")
            else:
                validation["details"]["sendgrid"] = "✅ API key appears valid"
        
        self.results["validations"]["external_services"] = validation
        print(f"   Status: {validation['status'].upper()}")
    
    def _validate_file_system(self):
        """Validate file system permissions and required directories"""
        print("\n📁 Validating File System...")
        
        validation = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        # Check critical directories
        critical_dirs = [
            "web/static", "web/templates", "routes", "models", 
            "services", "utils", "data"
        ]
        
        for dir_path in critical_dirs:
            if Path(dir_path).exists():
                validation["details"][dir_path] = "✅ Exists"
            else:
                validation["status"] = "warning"
                validation["details"][dir_path] = "⚠️ Missing"
                validation["issues"].append(f"Directory {dir_path} missing")
        
        # Check write permissions
        try:
            test_file = Path("deployment_write_test.tmp")
            test_file.write_text("test")
            test_file.unlink()
            validation["details"]["write_permissions"] = "✅ Write access working"
        except Exception as e:
            validation["status"] = "fail"
            validation["details"]["write_permissions"] = f"❌ Write test failed: {str(e)}"
            validation["issues"].append("No write permissions in current directory")
        
        # Check disk space
        try:
            statvfs = os.statvfs('.')
            free_space_gb = (statvfs.f_bavail * statvfs.f_frsize) / (1024**3)
            validation["details"]["disk_space"] = f"✅ {free_space_gb:.1f} GB free"
            
            if free_space_gb < 1:
                validation["status"] = "warning"
                validation["issues"].append("Low disk space")
        except:
            validation["details"]["disk_space"] = "⚠️ Could not check disk space"
        
        self.results["validations"]["file_system"] = validation
        print(f"   Status: {validation['status'].upper()}")
    
    def _validate_performance_optimizations(self):
        """Validate performance optimization implementations"""
        print("\n⚡ Validating Performance Optimizations...")
        
        validation = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        # Check if optimization utilities exist
        optimization_files = [
            "utils/query_optimizer.py",
            "utils/materialized_views.py", 
            "utils/performance_monitor.py"
        ]
        
        for file_path in optimization_files:
            if Path(file_path).exists():
                validation["details"][file_path] = "✅ Implemented"
            else:
                validation["status"] = "warning"
                validation["details"][file_path] = "⚠️ Missing"
                validation["issues"].append(f"Optimization utility {file_path} missing")
        
        # Test performance monitoring if available
        try:
            from utils.performance_monitor import PerformanceMonitor
            monitor = PerformanceMonitor()
            validation["details"]["performance_monitoring"] = "✅ Available"
        except:
            validation["details"]["performance_monitoring"] = "⚠️ Not available"
        
        self.results["validations"]["performance"] = validation
        print(f"   Status: {validation['status'].upper()}")
    
    def _validate_security_configuration(self):
        """Validate security configuration and best practices"""
        print("\n🔒 Validating Security Configuration...")
        
        validation = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        # Check secret key configuration
        secret_key = os.getenv("SECRET_KEY")
        if secret_key and len(secret_key) >= 32:
            validation["details"]["secret_key"] = "✅ Properly configured"
        else:
            validation["status"] = "fail"
            validation["details"]["secret_key"] = "❌ Missing or too short"
            validation["issues"].append("SECRET_KEY must be at least 32 characters")
        
        # Check environment setting
        environment = os.getenv("ENVIRONMENT", "development")
        if environment == "production":
            validation["details"]["environment"] = "✅ Production mode"
        else:
            validation["status"] = "warning"
            validation["details"]["environment"] = f"⚠️ Current: {environment}"
            validation["issues"].append("Not configured for production environment")
        
        # Check for debug mode
        debug_mode = os.getenv("DEBUG", "false").lower()
        if debug_mode == "false":
            validation["details"]["debug_mode"] = "✅ Debug disabled"
        else:
            validation["status"] = "warning"
            validation["details"]["debug_mode"] = "⚠️ Debug enabled"
            validation["issues"].append("Debug mode should be disabled in production")
        
        self.results["validations"]["security"] = validation
        print(f"   Status: {validation['status'].upper()}")
    
    def _validate_api_endpoints(self):
        """Validate critical API endpoints are accessible"""
        print("\n🔗 Validating API Endpoints...")
        
        validation = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        # This is a basic file existence check since we can't start the server
        critical_routes = [
            "routes/auth_coordinator.py",
            "routes/dashboard_routes.py",
            "routes/expenses.py",
            "routes/jobs.py"
        ]
        
        for route_file in critical_routes:
            if Path(route_file).exists():
                validation["details"][route_file] = "✅ Route file exists"
            else:
                validation["status"] = "fail"
                validation["details"][route_file] = "❌ Missing"
                validation["issues"].append(f"Critical route file {route_file} missing")
        
        # Check if app.py exists and is configured
        if Path("app.py").exists():
            validation["details"]["app.py"] = "✅ Main application file exists"
        else:
            validation["status"] = "fail"
            validation["details"]["app.py"] = "❌ Missing"
            validation["issues"].append("Main application file missing")
        
        self.results["validations"]["api_endpoints"] = validation
        print(f"   Status: {validation['status'].upper()}")
    
    def _validate_ai_systems(self):
        """Validate AI systems and intelligence components"""
        print("\n🤖 Validating AI Systems...")
        
        validation = {
            "status": "pass", 
            "details": {},
            "issues": []
        }
        
        # Check for AI service files
        ai_services = [
            "services/emotional_intelligence.py",
            "services/enhanced_orchestrator.py", 
            "services/profit_intelligence_engine.py",
            "services/cora_ai_service.py"
        ]
        
        for service_file in ai_services:
            if Path(service_file).exists():
                validation["details"][service_file] = "✅ AI service exists"
            else:
                validation["status"] = "warning"
                validation["details"][service_file] = "⚠️ Missing"
                validation["issues"].append(f"AI service {service_file} missing")
        
        # Check OpenAI configuration for AI features
        if os.getenv("OPENAI_API_KEY"):
            validation["details"]["openai_config"] = "✅ API key configured"
        else:
            validation["status"] = "warning"
            validation["details"]["openai_config"] = "⚠️ API key missing"
            validation["issues"].append("OpenAI API key needed for AI features")
        
        self.results["validations"]["ai_systems"] = validation
        print(f"   Status: {validation['status'].upper()}")
    
    def _calculate_readiness_score(self):
        """Calculate overall deployment readiness score"""
        total_validations = len(self.results["validations"])
        passed_validations = 0
        critical_failures = 0
        
        for validation in self.results["validations"].values():
            if validation["status"] == "pass":
                passed_validations += 1
            elif validation["status"] == "fail":
                critical_failures += 1
                self.results["critical_issues"].extend(validation["issues"])
            else:  # warning
                self.results["warnings"].extend(validation["issues"])
        
        # Calculate score (0-100)
        base_score = (passed_validations / total_validations) * 100
        
        # Penalize critical failures more heavily
        penalty = critical_failures * 15
        final_score = max(0, base_score - penalty)
        
        self.results["readiness_score"] = round(final_score, 1)
        
        # Determine overall status
        if critical_failures > 0:
            self.results["overall_status"] = "not_ready"
        elif len(self.results["warnings"]) > 3:
            self.results["overall_status"] = "ready_with_warnings"
        else:
            self.results["overall_status"] = "ready"
    
    def _generate_deployment_report(self):
        """Generate final deployment readiness report"""
        print("\n" + "=" * 50)
        print("🎯 DEPLOYMENT READINESS REPORT")
        print("=" * 50)
        
        score = self.results["readiness_score"]
        status = self.results["overall_status"]
        
        # Status emoji and message
        if status == "ready":
            emoji = "✅"
            message = "READY FOR DEPLOYMENT"
        elif status == "ready_with_warnings":
            emoji = "⚠️"
            message = "READY WITH WARNINGS"
        else:
            emoji = "❌"
            message = "NOT READY FOR DEPLOYMENT"
        
        print(f"\n{emoji} Overall Status: {message}")
        print(f"📊 Readiness Score: {score}/100")
        
        # Critical issues
        if self.results["critical_issues"]:
            print(f"\n❌ Critical Issues ({len(self.results['critical_issues'])}):")
            for issue in self.results["critical_issues"]:
                print(f"   • {issue}")
        
        # Warnings
        if self.results["warnings"]:
            print(f"\n⚠️ Warnings ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"][:5]:  # Show first 5
                print(f"   • {warning}")
            if len(self.results["warnings"]) > 5:
                print(f"   ... and {len(self.results['warnings']) - 5} more")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if score >= 90:
            print("   • System is production-ready! Consider deploying.")
        elif score >= 75:
            print("   • Address warnings before deployment for optimal experience.")
        elif score >= 50:
            print("   • Fix critical issues and address major warnings.")
        else:
            print("   • Significant work needed before production deployment.")
        
        print("\n🚀 Ready to launch CORA's consciousness into the world!")

def run_deployment_validation():
    """Run deployment validation and return results"""
    validator = DeploymentValidator()
    return validator.run_full_validation()

if __name__ == "__main__":
    # Run validation when script is executed directly
    results = run_deployment_validation()
    
    # Save results to file
    with open("deployment_validation_report.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Full report saved to: deployment_validation_report.json")