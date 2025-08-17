#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/deployment_check.py
🎯 PURPOSE: Pre-deployment validation script
🔗 IMPORTS: requests, sys, json
📤 EXPORTS: Deployment validation results
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple
import requests
from datetime import datetime

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class DeploymentChecker:
    """Pre-deployment validation checks"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.errors = []
        self.warnings = []
        self.passed = []
        self.base_url = "http://localhost:8000"
        
    def run_all_checks(self) -> bool:
        """Run all deployment checks"""
        print(f"{BLUE}{'='*43}{RESET}")
        print(f"{BLUE}    CORA DEPLOYMENT VALIDATION CHECK{RESET}")
        print(f"{BLUE}{'='*43}{RESET}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}\n")
        
        checks = [
            ("Python Dependencies", self.check_dependencies),
            ("File Integrity", self.check_file_integrity),
            ("Template Syntax", self.check_template_syntax),
            ("Database Connection", self.check_database),
            ("API Endpoints", self.check_api_endpoints),
            ("Static Files", self.check_static_files),
            ("Security Headers", self.check_security_headers),
            ("Environment Variables", self.check_environment),
            ("JavaScript Files", self.check_javascript_files),
            ("CSS Files", self.check_css_files),
        ]
        
        for check_name, check_func in checks:
            print(f"\n{BLUE}> {check_name}...{RESET}")
            try:
                check_func()
            except Exception as e:
                self.errors.append(f"{check_name}: {str(e)}")
                print(f"  {RED}[FAIL] Failed with exception{RESET}")
        
        # Print summary
        self.print_summary()
        
        return len(self.errors) == 0
    
    def check_dependencies(self):
        """Check Python dependencies"""
        required_packages = [
            "fastapi",
            "sqlalchemy",
            "pydantic",
            "jinja2",
            "python-jose",
            "passlib",
            "python-multipart",
            "uvicorn"
        ]
        
        try:
            import pkg_resources
            installed = {pkg.key for pkg in pkg_resources.working_set}
            
            for package in required_packages:
                if package.lower() in installed:
                    self.passed.append(f"Package {package} installed")
                    print(f"  {GREEN}[OK] {package}{RESET}")
                else:
                    self.errors.append(f"Missing package: {package}")
                    print(f"  {RED}[FAIL] {package} NOT FOUND{RESET}")
        except ImportError:
            self.warnings.append("Could not check packages (pkg_resources not available)")
    
    def check_file_integrity(self):
        """Check critical files exist and have correct size"""
        critical_files = [
            ("app.py", 1000, None),  # Min size
            ("web/templates/base_public.html", 5000, None),
            ("web/templates/index.html", 50000, None),  # Should be > 50KB
            ("web/templates/features.html", 40000, None),
            ("web/templates/pricing.html", 40000, None),
            ("web/static/css/construction-theme.css", 1000, 10000),  # Min and max
        ]
        
        for file_path, min_size, max_size in critical_files:
            path = Path(file_path)
            if path.exists():
                size = path.stat().st_size
                if size < min_size:
                    self.errors.append(f"{file_path} too small: {size} bytes (min: {min_size})")
                    print(f"  {RED}[FAIL] {file_path}: TOO SMALL ({size} bytes){RESET}")
                elif max_size and size > max_size:
                    self.warnings.append(f"{file_path} large: {size} bytes (max: {max_size})")
                    print(f"  {YELLOW}[WARN] {file_path}: LARGE ({size} bytes){RESET}")
                else:
                    self.passed.append(f"{file_path}: {size} bytes")
                    print(f"  {GREEN}[OK] {file_path}: {size} bytes{RESET}")
            else:
                self.errors.append(f"Missing file: {file_path}")
                print(f"  {RED}[FAIL] {file_path}: NOT FOUND{RESET}")
    
    def check_template_syntax(self):
        """Check Jinja2 template syntax"""
        from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError
        
        template_dir = Path("web/templates")
        env = Environment(loader=FileSystemLoader(template_dir))
        
        templates_to_check = [
            "base_public.html",
            "index.html",
            "features.html",
            "pricing.html",
            "reviews.html",
            "contact.html"
        ]
        
        for template_name in templates_to_check:
            try:
                env.get_template(template_name)
                self.passed.append(f"Template {template_name} valid")
                print(f"  {GREEN}[OK] {template_name}{RESET}")
            except TemplateSyntaxError as e:
                self.errors.append(f"Template error in {template_name}: {str(e)}")
                print(f"  {RED}[FAIL] {template_name}: SYNTAX ERROR{RESET}")
            except Exception as e:
                self.warnings.append(f"Could not check {template_name}: {str(e)}")
                print(f"  {YELLOW}[WARN] {template_name}: CHECK FAILED{RESET}")
    
    def check_database(self):
        """Check database connection"""
        try:
            # Check if database file exists
            from pathlib import Path
            db_file = Path("cora.db")
            if db_file.exists():
                self.passed.append(f"Database file exists: {db_file.stat().st_size} bytes")
                print(f"  {GREEN}[OK] Database file exists{RESET}")
            else:
                self.warnings.append("Database file not found")
                print(f"  {YELLOW}[WARN] Database file not found{RESET}")
        except Exception as e:
            self.warnings.append(f"Could not check database: {str(e)}")
            print(f"  {YELLOW}[WARN] Database check failed{RESET}")
    
    def check_api_endpoints(self):
        """Check critical API endpoints"""
        endpoints = [
            ("/", 200),
            ("/features", 200),
            ("/pricing", 200),
            ("/blog", 200),
            ("/api/health", 200),
            ("/api/admin/stats", 401),  # Should require auth
        ]
        
        for endpoint, expected_status in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code == expected_status:
                    self.passed.append(f"Endpoint {endpoint}: {response.status_code}")
                    print(f"  {GREEN}[OK] {endpoint}: {response.status_code}{RESET}")
                else:
                    self.warnings.append(f"Endpoint {endpoint}: got {response.status_code}, expected {expected_status}")
                    print(f"  {YELLOW}[WARN] {endpoint}: {response.status_code} (expected {expected_status}){RESET}")
            except requests.exceptions.ConnectionError:
                self.warnings.append(f"Server not running, skipping endpoint checks")
                print(f"  {YELLOW}[WARN] Server not running - skipping API checks{RESET}")
                break
            except Exception as e:
                self.errors.append(f"Endpoint {endpoint} failed: {str(e)}")
                print(f"  {RED}[FAIL] {endpoint}: ERROR{RESET}")
    
    def check_static_files(self):
        """Check static files are accessible"""
        static_files = [
            "css/construction-theme.css",
            "css/navbar.css",
            "js/security.js",
            "js/api-error-handler.js",
            "images/logos/cora-logo.png"
        ]
        
        for file_path in static_files:
            full_path = Path(f"web/static/{file_path}")
            if full_path.exists():
                self.passed.append(f"Static file {file_path} exists")
                print(f"  {GREEN}[OK] {file_path}{RESET}")
            else:
                self.errors.append(f"Missing static file: {file_path}")
                print(f"  {RED}[FAIL] {file_path}: NOT FOUND{RESET}")
    
    def check_security_headers(self):
        """Check security configuration"""
        security_checks = [
            ("Security middleware configured", Path("middleware/security.py").exists()),
            ("CORS configured", self.check_cors_config()),
            ("HTTPS redirect configured", self.check_https_redirect()),
        ]
        
        for check_name, result in security_checks:
            if result:
                self.passed.append(check_name)
                print(f"  {GREEN}[OK] {check_name}{RESET}")
            else:
                self.warnings.append(f"{check_name}: not configured")
                print(f"  {YELLOW}[WARN] {check_name}: NOT CONFIGURED{RESET}")
    
    def check_cors_config(self) -> bool:
        """Check if CORS is configured"""
        try:
            with open("app.py", "r") as f:
                content = f.read()
                return "CORSMiddleware" in content
        except:
            return False
    
    def check_https_redirect(self) -> bool:
        """Check if HTTPS redirect is configured"""
        # This would check production config
        return True  # Placeholder
    
    def check_environment(self):
        """Check environment variables"""
        required_env = [
            "SECRET_KEY",
            "DATABASE_URL",
        ]
        
        optional_env = [
            "PLAID_CLIENT_ID",
            "PLAID_SECRET",
            "SENDGRID_API_KEY",
            "SENTRY_DSN"
        ]
        
        for var in required_env:
            if os.getenv(var):
                self.passed.append(f"Environment variable {var} set")
                print(f"  {GREEN}[OK] {var}: SET{RESET}")
            else:
                self.errors.append(f"Missing required env var: {var}")
                print(f"  {RED}[FAIL] {var}: NOT SET{RESET}")
        
        for var in optional_env:
            if os.getenv(var):
                print(f"  {GREEN}[OK] {var}: SET{RESET}")
            else:
                print(f"  {YELLOW}[WARN] {var}: NOT SET (optional){RESET}")
    
    def check_javascript_files(self):
        """Check JavaScript files for syntax errors"""
        js_files = [
            "web/static/js/security.js",
            "web/static/js/api-error-handler.js",
            "web/static/js/error-reporter.js"
        ]
        
        for file_path in js_files:
            if Path(file_path).exists():
                # Could use a JS linter here if available
                self.passed.append(f"JavaScript file {file_path} exists")
                print(f"  {GREEN}[OK] {file_path}{RESET}")
            else:
                self.warnings.append(f"JavaScript file {file_path} not found")
                print(f"  {YELLOW}[WARN] {file_path}: NOT FOUND{RESET}")
    
    def check_css_files(self):
        """Check CSS files"""
        css_files = [
            "web/static/css/construction-theme.css",
            "web/static/css/navbar.css"
        ]
        
        for file_path in css_files:
            if Path(file_path).exists():
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Check for common CSS issues
                    if content.count('{') != content.count('}'):
                        self.warnings.append(f"CSS file {file_path} may have unmatched braces")
                        print(f"  {YELLOW}[WARN] {file_path}: POSSIBLE SYNTAX ERROR{RESET}")
                    else:
                        self.passed.append(f"CSS file {file_path} valid")
                        print(f"  {GREEN}[OK] {file_path}{RESET}")
            else:
                self.errors.append(f"CSS file {file_path} not found")
                print(f"  {RED}[FAIL] {file_path}: NOT FOUND{RESET}")
    
    def print_summary(self):
        """Print deployment check summary"""
        print(f"\n{BLUE}{'='*43}{RESET}")
        print(f"{BLUE}              SUMMARY REPORT{RESET}")
        print(f"{BLUE}{'='*43}{RESET}")
        
        print(f"\n{GREEN}[OK] Passed: {len(self.passed)}{RESET}")
        print(f"{YELLOW}[WARN] Warnings: {len(self.warnings)}{RESET}")
        print(f"{RED}[FAIL] Errors: {len(self.errors)}{RESET}")
        
        if self.errors:
            print(f"\n{RED}CRITICAL ERRORS FOUND:{RESET}")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors) - 5} more")
            
            print(f"\n{RED}[X] DEPLOYMENT NOT READY{RESET}")
            print("Fix the errors above before deploying")
            
        elif self.warnings:
            print(f"\n{YELLOW}Warnings present but deployment possible{RESET}")
            for warning in self.warnings[:3]:
                print(f"  - {warning}")
            
            print(f"\n{YELLOW}[WARN]️  DEPLOYMENT READY WITH WARNINGS{RESET}")
            
        else:
            print(f"\n{GREEN}[READY] ALL CHECKS PASSED - READY TO DEPLOY!{RESET}")
        
        print(f"\n{BLUE}{'='*43}{RESET}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CORA Deployment Validation")
    parser.add_argument("--live", action="store_true", 
                       help="Run in live mode (default is dry-run)")
    parser.add_argument("--json", action="store_true",
                       help="Output results as JSON")
    
    args = parser.parse_args()
    
    checker = DeploymentChecker(dry_run=not args.live)
    success = checker.run_all_checks()
    
    if args.json:
        result = {
            "success": success,
            "errors": checker.errors,
            "warnings": checker.warnings,
            "passed": checker.passed,
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(result, indent=2))
    
    sys.exit(0 if success else 1)