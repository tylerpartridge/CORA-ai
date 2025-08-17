#!/usr/bin/env python3
"""
🚀 CORA Deployment Readiness Checker
Automated tool to verify system is ready for production deployment
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import sqlite3

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class DeploymentReadinessChecker:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "errors": [],
            "warnings": [],
            "passed": 0,
            "failed": 0,
            "total": 0
        }
        
    def run_all_checks(self):
        """Run all deployment readiness checks"""
        print("\n" + "="*60)
        print("CORA DEPLOYMENT READINESS CHECKER")
        print("="*60 + "\n")
        
        # Phase 1: Code Health
        self.check_python_syntax()
        self.check_javascript_syntax()
        self.check_json_files()
        self.check_imports()
        
        # Phase 2: File System
        self.check_required_files()
        self.check_missing_assets()
        self.check_deployment_package()
        
        # Phase 3: Database
        self.check_database_integrity()
        
        # Phase 4: Configuration
        self.check_environment_config()
        self.check_security_issues()
        
        # Phase 5: Routes
        self.check_api_routes()
        
        # Generate report
        self.generate_report()
        
    def check_python_syntax(self):
        """Check all Python files for syntax errors"""
        print("[*] Checking Python syntax...")
        errors = []
        py_files = list(self.base_path.rglob("*.py"))
        
        for py_file in py_files:
            # Skip virtual environments and deployment packages
            if any(skip in str(py_file) for skip in ['venv', 'env', '.env', 'deployment_package', '__pycache__']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), py_file, 'exec')
            except SyntaxError as e:
                errors.append(f"{py_file}: {e}")
                
        self.results["checks"]["python_syntax"] = {
            "passed": len(errors) == 0,
            "total_files": len(py_files),
            "errors": errors
        }
        
        if errors:
            print(f"  [!] Found {len(errors)} Python syntax errors")
            self.results["failed"] += 1
        else:
            print(f"  [OK] All {len(py_files)} Python files valid")
            self.results["passed"] += 1
            
        self.results["total"] += 1
        
    def check_javascript_syntax(self):
        """Check JavaScript files for basic issues"""
        print("[*] Checking JavaScript files...")
        js_files = list(self.base_path.rglob("*.js"))
        issues = []
        
        for js_file in js_files:
            if any(skip in str(js_file) for skip in ['node_modules', 'deployment_package', '.min.js']):
                continue
                
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for common issues
                if 'console.log(' in content and 'debug' not in str(js_file).lower():
                    issues.append(f"{js_file}: Contains console.log (should be removed for production)")
                if 'debugger;' in content:
                    issues.append(f"{js_file}: Contains debugger statement")
                if 'localhost' in content and 'service-worker' not in str(js_file):
                    issues.append(f"{js_file}: Contains localhost reference")
                    
        self.results["checks"]["javascript"] = {
            "passed": len(issues) == 0,
            "total_files": len(js_files),
            "warnings": issues
        }
        
        if issues:
            print(f"  [!] Found {len(issues)} JavaScript issues")
            self.results["warnings"].extend(issues)
        else:
            print(f"  [OK] All {len(js_files)} JavaScript files clean")
            self.results["passed"] += 1
            
        self.results["total"] += 1
        
    def check_json_files(self):
        """Validate all JSON files"""
        print("[*] Checking JSON files...")
        json_files = list(self.base_path.rglob("*.json"))
        errors = []
        
        for json_file in json_files:
            if 'node_modules' in str(json_file):
                continue
                
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                errors.append(f"{json_file}: {e}")
                
        self.results["checks"]["json_validation"] = {
            "passed": len(errors) == 0,
            "total_files": len(json_files),
            "errors": errors
        }
        
        if errors:
            print(f"  [!] Found {len(errors)} invalid JSON files")
            self.results["failed"] += 1
        else:
            print(f"  [OK] All {len(json_files)} JSON files valid")
            self.results["passed"] += 1
            
        self.results["total"] += 1
        
    def check_imports(self):
        """Check Python imports are valid"""
        print("[*] Checking Python imports...")
        
        # Try importing key modules
        modules_to_check = [
            'app',
            'models',
            'routes.auth_coordinator',
            'routes.expense_coordinator',
            'routes.pages',
            'dependencies.auth',
            'dependencies.database'
        ]
        
        failed_imports = []
        for module in modules_to_check:
            try:
                __import__(module)
            except ImportError as e:
                failed_imports.append(f"{module}: {e}")
                
        self.results["checks"]["imports"] = {
            "passed": len(failed_imports) == 0,
            "total_modules": len(modules_to_check),
            "errors": failed_imports
        }
        
        if failed_imports:
            print(f"  [!] {len(failed_imports)} import errors found")
            self.results["failed"] += 1
        else:
            print(f"  [OK] All core imports working")
            self.results["passed"] += 1
            
        self.results["total"] += 1
        
    def check_required_files(self):
        """Check for required files"""
        print("[*] Checking required files...")
        
        required_files = [
            'app.py',
            'requirements.txt',
            'package.json',
            '.env.example',
            'README.md',
            'models.py',
            'config.py'
        ]
        
        missing = []
        for file in required_files:
            if not (self.base_path / file).exists():
                missing.append(file)
                
        self.results["checks"]["required_files"] = {
            "passed": len(missing) == 0,
            "missing": missing
        }
        
        if missing:
            print(f"  [!] Missing {len(missing)} required files: {missing}")
            self.results["failed"] += 1
        else:
            print(f"  [OK] All required files present")
            self.results["passed"] += 1
            
        self.results["total"] += 1
        
    def check_missing_assets(self):
        """Check for 404 assets mentioned in templates"""
        print("[*] Checking for missing assets...")
        
        # Known assets that should exist
        assets_to_check = [
            'web/static/favicon-transparent.svg',
            'web/static/service-worker.js',
            'web/static/css/construction-theme.css',
            'web/static/css/navbar.css',
            'web/static/js/cora-chat-enhanced.js',
            'web/static/sounds/success.mp3'
        ]
        
        missing = []
        for asset in assets_to_check:
            if not (self.base_path / asset).exists():
                missing.append(asset)
                
        self.results["checks"]["assets"] = {
            "passed": len(missing) == 0,
            "missing": missing
        }
        
        if missing:
            print(f"  [!] Missing {len(missing)} assets")
            self.results["failed"] += 1
        else:
            print(f"  [OK] All critical assets present")
            self.results["passed"] += 1
            
        self.results["total"] += 1
        
    def check_deployment_package(self):
        """Check deployment package completeness"""
        print("[*] Checking deployment package...")
        
        deploy_path = self.base_path / 'deployment_package'
        
        if not deploy_path.exists():
            self.results["checks"]["deployment_package"] = {
                "passed": False,
                "error": "deployment_package directory not found"
            }
            self.results["failed"] += 1
        else:
            # Check for key components
            required_in_package = [
                'app.py',
                'requirements.txt',
                'web/templates',
                'web/static'
            ]
            
            missing = []
            for item in required_in_package:
                if not (deploy_path / item).exists():
                    missing.append(item)
                    
            self.results["checks"]["deployment_package"] = {
                "passed": len(missing) == 0,
                "missing": missing
            }
            
            if missing:
                print(f"  [!] Deployment package missing: {missing}")
                self.results["failed"] += 1
            else:
                print(f"  [OK] Deployment package appears complete")
                self.results["passed"] += 1
                
        self.results["total"] += 1
        
    def check_database_integrity(self):
        """Check database health"""
        print("[*] Checking database integrity...")
        
        db_path = self.base_path / 'cora.db'
        
        if not db_path.exists():
            self.results["checks"]["database"] = {
                "passed": False,
                "error": "Database file not found"
            }
            self.results["failed"] += 1
        else:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check tables exist
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                # Check for orphaned records (example)
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                
                conn.close()
                
                self.results["checks"]["database"] = {
                    "passed": True,
                    "tables": len(tables),
                    "users": user_count
                }
                print(f"  [OK] Database healthy: {len(tables)} tables, {user_count} users")
                self.results["passed"] += 1
                
            except Exception as e:
                self.results["checks"]["database"] = {
                    "passed": False,
                    "error": str(e)
                }
                print(f"  [!] Database error: {e}")
                self.results["failed"] += 1
                
        self.results["total"] += 1
        
    def check_environment_config(self):
        """Check environment configuration"""
        print("[*] Checking environment configuration...")
        
        issues = []
        
        # Check .env.example exists
        if not (self.base_path / '.env.example').exists():
            issues.append("Missing .env.example file")
            
        # Check for .env file (warn if missing)
        if not (self.base_path / '.env').exists():
            self.results["warnings"].append("No .env file found (needed for local development)")
            
        # Check critical environment variables in .env.example
        if (self.base_path / '.env.example').exists():
            with open(self.base_path / '.env.example', 'r') as f:
                env_example = f.read()
                required_vars = ['SECRET_KEY', 'DATABASE_URL', 'JWT_SECRET_KEY']
                for var in required_vars:
                    if var not in env_example:
                        issues.append(f"Missing {var} in .env.example")
                        
        self.results["checks"]["environment"] = {
            "passed": len(issues) == 0,
            "issues": issues
        }
        
        if issues:
            print(f"  [!] Environment config issues: {len(issues)}")
            self.results["failed"] += 1
        else:
            print(f"  [OK] Environment configuration looks good")
            self.results["passed"] += 1
            
        self.results["total"] += 1
        
    def check_security_issues(self):
        """Check for common security issues"""
        print("[*] Checking for security issues...")
        
        security_issues = []
        
        # Check for hardcoded secrets
        patterns_to_check = [
            ('SECRET_KEY = "', 'Hardcoded SECRET_KEY'),
            ('password = "', 'Hardcoded password'),
            ('api_key = "', 'Hardcoded API key'),
            ('AWS_', 'Possible AWS credentials'),
            ('sk_live_', 'Stripe live key exposed'),
        ]
        
        py_files = list(self.base_path.rglob("*.py"))
        for py_file in py_files:
            if any(skip in str(py_file) for skip in ['venv', 'deployment_package', 'test']):
                continue
                
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern, description in patterns_to_check:
                    if pattern in content:
                        security_issues.append(f"{py_file}: {description}")
                        
        # Check if DEBUG is False in production config
        config_file = self.base_path / 'config.py'
        if config_file.exists():
            with open(config_file, 'r') as f:
                if 'DEBUG = True' in f.read():
                    security_issues.append("DEBUG mode is True in config.py")
                    
        self.results["checks"]["security"] = {
            "passed": len(security_issues) == 0,
            "issues": security_issues
        }
        
        if security_issues:
            print(f"  [!] Found {len(security_issues)} security issues")
            self.results["failed"] += 1
        else:
            print(f"  [OK] No obvious security issues found")
            self.results["passed"] += 1
            
        self.results["total"] += 1
        
    def check_api_routes(self):
        """Test critical API routes"""
        print("[*] Checking API routes...")
        
        try:
            from app import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            
            # Test critical routes
            routes_to_test = [
                ('/', 200),
                ('/features', 200),
                ('/pricing', 200),
                ('/login', 200),
                ('/signup', 200),
                ('/api/health', 200),
            ]
            
            failed_routes = []
            for route, expected_status in routes_to_test:
                response = client.get(route, follow_redirects=False)
                if response.status_code != expected_status:
                    failed_routes.append(f"{route}: got {response.status_code}, expected {expected_status}")
                    
            self.results["checks"]["routes"] = {
                "passed": len(failed_routes) == 0,
                "tested": len(routes_to_test),
                "failed": failed_routes
            }
            
            if failed_routes:
                print(f"  [!] {len(failed_routes)} routes failed")
                self.results["failed"] += 1
            else:
                print(f"  [OK] All {len(routes_to_test)} critical routes working")
                self.results["passed"] += 1
                
        except Exception as e:
            self.results["checks"]["routes"] = {
                "passed": False,
                "error": str(e)
            }
            print(f"  [!] Could not test routes: {e}")
            self.results["failed"] += 1
            
        self.results["total"] += 1
        
    def generate_report(self):
        """Generate deployment readiness report"""
        print("\n" + "="*60)
        print("DEPLOYMENT READINESS REPORT")
        print("="*60)
        
        # Calculate readiness score
        if self.results["total"] > 0:
            readiness_score = (self.results["passed"] / self.results["total"]) * 100
        else:
            readiness_score = 0
            
        print(f"\nReadiness Score: {readiness_score:.1f}%")
        print(f"Checks Passed: {self.results['passed']}/{self.results['total']}")
        
        # Show failures
        if self.results["failed"] > 0:
            print(f"\n[!] FAILURES ({self.results['failed']}):")
            for check_name, check_data in self.results["checks"].items():
                if not check_data.get("passed", True):
                    print(f"  - {check_name}")
                    if "error" in check_data:
                        print(f"    Error: {check_data['error']}")
                    if "errors" in check_data:
                        for error in check_data["errors"][:3]:  # Show first 3
                            print(f"    - {error}")
                            
        # Show warnings
        if self.results["warnings"]:
            print(f"\n[!] WARNINGS ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"][:5]:  # Show first 5
                print(f"  - {warning}")
                
        # Final verdict
        print("\n" + "="*60)
        if readiness_score >= 95:
            print("[OK] System is READY for deployment!")
        elif readiness_score >= 80:
            print("[!] System is ALMOST ready - fix critical issues first")
        else:
            print("[X] System is NOT ready for deployment - significant issues found")
            
        # Save detailed report
        report_file = self.base_path / f"deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\nDetailed report saved to: {report_file}")
        
        return readiness_score

if __name__ == "__main__":
    checker = DeploymentReadinessChecker()
    score = checker.run_all_checks()
    
    # Exit with code based on readiness
    if score >= 95:
        sys.exit(0)  # Ready
    else:
        sys.exit(1)  # Not ready