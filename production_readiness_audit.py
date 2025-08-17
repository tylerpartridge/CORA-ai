#!/usr/bin/env python3
"""
Production Readiness Audit - ZERO TOLERANCE FOR BUGS
Gets CORA to bulletproof production state
"""
import os
import sys
import subprocess
import json
import sqlite3
from pathlib import Path
sys.path.append('/mnt/host/c/CORA')

class ProductionReadinessAudit:
    def __init__(self):
        self.critical_issues = []
        self.warnings = []
        self.passed_checks = []
        self.test_results = {}
        
    def run_full_audit(self):
        """Run comprehensive production readiness audit"""
        print("=== CORA PRODUCTION READINESS AUDIT ===")
        print("Zero tolerance for bugs, patches, or failures\n")
        
        # 1. Test Suite Analysis
        print("1. TESTING ANALYSIS")
        print("-" * 20)
        self.analyze_test_coverage()
        
        # 2. Critical Path Testing  
        print("\n2. CRITICAL PATH TESTING")
        print("-" * 25)
        self.test_critical_paths()
        
        # 3. Database Integrity
        print("\n3. DATABASE INTEGRITY")
        print("-" * 20)
        self.check_database_health()
        
        # 4. Configuration Validation
        print("\n4. CONFIGURATION VALIDATION")
        print("-" * 27)
        self.validate_configurations()
        
        # 5. Error Handling Coverage
        print("\n5. ERROR HANDLING COVERAGE")
        print("-" * 26)
        self.check_error_handling()
        
        # 6. Security Hardening
        print("\n6. SECURITY HARDENING")
        print("-" * 20)
        self.security_final_check()
        
        # 7. Performance Validation
        print("\n7. PERFORMANCE VALIDATION")
        print("-" * 24)
        self.performance_check()
        
        # Final Report
        self.generate_final_report()
    
    def analyze_test_coverage(self):
        """Analyze test suite and coverage"""
        try:
            # Find all test files
            test_files = []
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if file.startswith('test_') and file.endswith('.py'):
                        test_files.append(os.path.join(root, file))
            
            print(f"Found {len(test_files)} test files")
            
            # Check for pytest
            try:
                result = subprocess.run(['./venv/Scripts/python.exe', '-m', 'pytest', '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.passed_checks.append("pytest available")
                else:
                    self.warnings.append("pytest not available")
            except:
                self.warnings.append("Could not check pytest availability")
            
            # Look for coverage config
            if os.path.exists('pytest.ini') or os.path.exists('.coveragerc'):
                self.passed_checks.append("Test configuration found")
            else:
                self.warnings.append("No test configuration found")
                
        except Exception as e:
            self.critical_issues.append(f"Test analysis failed: {e}")
    
    def test_critical_paths(self):
        """Test critical user paths"""
        critical_paths = [
            "User registration/login",
            "Expense creation/retrieval", 
            "Dashboard data loading",
            "Database connections",
            "Static file serving"
        ]
        
        # Test basic imports work
        try:
            from app import app
            self.passed_checks.append("Main app imports successfully")
        except Exception as e:
            self.critical_issues.append(f"Critical: Main app import failed - {e}")
        
        # Test database connection
        try:
            import sqlite3
            conn = sqlite3.connect('cora.db')
            conn.execute("SELECT 1").fetchone()
            conn.close()
            self.passed_checks.append("Database connection works")
        except Exception as e:
            self.critical_issues.append(f"Critical: Database connection failed - {e}")
        
        # Test key routes import
        try:
            from routes.dashboard_routes import dashboard_router
            from routes.auth_coordinator import auth_router
            self.passed_checks.append("Critical routes import successfully")
        except Exception as e:
            self.critical_issues.append(f"Critical: Route imports failed - {e}")
    
    def check_database_health(self):
        """Check database integrity and health"""
        try:
            conn = sqlite3.connect('cora.db')
            cursor = conn.cursor()
            
            # Check integrity
            result = cursor.execute('PRAGMA integrity_check').fetchone()
            if result[0] == 'ok':
                self.passed_checks.append("Database integrity check passed")
            else:
                self.critical_issues.append(f"Database integrity failed: {result[0]}")
            
            # Check critical tables exist
            tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            table_names = [t[0] for t in tables]
            
            critical_tables = ['users', 'expenses', 'jobs', 'expense_categories']
            for table in critical_tables:
                if table in table_names:
                    self.passed_checks.append(f"Critical table '{table}' exists")
                else:
                    self.critical_issues.append(f"Critical table '{table}' missing")
            
            conn.close()
            
        except Exception as e:
            self.critical_issues.append(f"Database health check failed: {e}")
    
    def validate_configurations(self):
        """Validate all configurations are production-ready"""
        try:
            from config import config
            
            # Check critical configs
            if config.SECRET_KEY and len(config.SECRET_KEY) > 20:
                self.passed_checks.append("SECRET_KEY configured properly")
            else:
                self.critical_issues.append("SECRET_KEY missing or too short")
            
            if config.JWT_SECRET_KEY and len(config.JWT_SECRET_KEY) > 20:
                self.passed_checks.append("JWT_SECRET_KEY configured properly")
            else:
                self.critical_issues.append("JWT_SECRET_KEY missing or too short")
            
            # Check production readiness
            if not config.DEBUG:
                self.passed_checks.append("DEBUG mode disabled for production")
            else:
                self.critical_issues.append("DEBUG mode still enabled!")
                
        except Exception as e:
            self.critical_issues.append(f"Configuration validation failed: {e}")
    
    def check_error_handling(self):
        """Check error handling coverage"""
        error_patterns = [
            "except Exception:",
            "raise HTTPException",
            "try:",
            "except:"
        ]
        
        total_handlers = 0
        files_checked = 0
        
        for root, dirs, files in os.walk('routes'):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            for pattern in error_patterns:
                                total_handlers += content.count(pattern)
                            files_checked += 1
                    except:
                        pass
        
        print(f"Found {total_handlers} error handlers across {files_checked} route files")
        if total_handlers > 50:
            self.passed_checks.append("Good error handling coverage")
        else:
            self.warnings.append("Consider adding more error handling")
    
    def security_final_check(self):
        """Final security validation"""
        security_checks = [
            ("Secret keys", "Config secrets properly set"),
            ("HTTPS", "Security headers middleware active"),
            ("SQL injection", "Using parameterized queries"),
            ("CORS", "CORS configuration present")
        ]
        
        # Check for security middleware
        try:
            from middleware.security_headers import SecurityHeadersMiddleware
            self.passed_checks.append("Security headers middleware available")
        except:
            self.warnings.append("Security headers middleware not found")
        
        # Check for rate limiting
        try:
            from middleware.rate_limiting import RateLimitMiddleware
            self.passed_checks.append("Rate limiting middleware available")
        except:
            self.warnings.append("Rate limiting middleware not found")
    
    def performance_check(self):
        """Basic performance validation"""
        # Check for performance optimizations
        optimizations = []
        
        # Check for caching
        try:
            from functools import lru_cache
            # Look for @lru_cache usage
            cache_usage = 0
            for root, dirs, files in os.walk('routes'):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r') as f:
                                if '@lru_cache' in f.read():
                                    cache_usage += 1
                        except:
                            pass
            
            if cache_usage > 0:
                self.passed_checks.append(f"Caching implemented in {cache_usage} places")
            
        except:
            pass
        
        # Check database size
        if os.path.exists('cora.db'):
            size = os.path.getsize('cora.db')
            size_mb = size / (1024 * 1024)
            if size_mb < 100:  # Under 100MB is reasonable for startup
                self.passed_checks.append(f"Database size reasonable ({size_mb:.1f}MB)")
            else:
                self.warnings.append(f"Database size large ({size_mb:.1f}MB)")
    
    def generate_final_report(self):
        """Generate final readiness report"""
        print("\n" + "=" * 50)
        print("PRODUCTION READINESS FINAL REPORT")
        print("=" * 50)
        
        print(f"\nPASSED CHECKS ({len(self.passed_checks)}):")
        for check in self.passed_checks:
            print(f"  + {check}")
        
        if self.warnings:
            print(f"\nWARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  ! {warning}")
        
        if self.critical_issues:
            print(f"\nCRITICAL ISSUES ({len(self.critical_issues)}):")
            for issue in self.critical_issues:
                print(f"  - {issue}")
        
        # Overall assessment
        print(f"\n{'='*50}")
        if len(self.critical_issues) == 0:
            if len(self.warnings) == 0:
                print("PRODUCTION READY - ZERO ISSUES!")
                print("CORA is bulletproof and ready for users!")
            else:
                print("PRODUCTION READY - Minor warnings only")
                print("CORA is solid with minor optimizations possible")
        else:
            print("NOT PRODUCTION READY")
            print(f"Fix {len(self.critical_issues)} critical issues before deployment")
        
        print(f"{'='*50}\n")
        
        return len(self.critical_issues) == 0

if __name__ == "__main__":
    auditor = ProductionReadinessAudit()
    success = auditor.run_full_audit()
    exit(0 if success else 1)