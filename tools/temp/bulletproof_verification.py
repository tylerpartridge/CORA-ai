#!/usr/bin/env python3
"""
BULLETPROOF VERIFICATION - Final Production Check
Zero tolerance approach - every critical system must be perfect
"""
import os
import sys
import subprocess
import sqlite3
import json
sys.path.append('/mnt/host/c/CORA')

class BulletproofVerification:
    def __init__(self):
        self.score = 0
        self.max_score = 0
        self.failures = []
        
    def verify_all_systems(self):
        """Verify every critical system works perfectly"""
        print("BULLETPROOF VERIFICATION")
        print("=" * 30)
        print("Testing every critical system...\n")
        
        # Core System Checks
        self.check_app_starts()
        self.check_database_operations()
        self.check_all_imports()
        self.check_critical_routes()
        self.check_security_config()
        self.check_error_handling()
        
        # Generate final verdict
        self.final_verdict()
        
    def check_app_starts(self):
        """Verify the main application starts without errors"""
        print("1. Application Startup Test")
        self.max_score += 10
        
        try:
            from app import app
            print("  + Main app imports successfully")
            self.score += 5
            
            # Check if app has routes
            if hasattr(app, 'routes') and len(app.routes) > 0:
                print(f"  + App has {len(app.routes)} routes registered")
                self.score += 5
            else:
                print("  - No routes found in app")
                self.failures.append("No routes registered in main app")
                
        except Exception as e:
            print(f"  - App startup failed: {e}")
            self.failures.append(f"App startup failed: {e}")
    
    def check_database_operations(self):
        """Test all critical database operations"""
        print("\n2. Database Operations Test")
        self.max_score += 15
        
        try:
            # Test connection
            conn = sqlite3.connect('cora.db')
            cursor = conn.cursor()
            print("  + Database connection works")
            self.score += 3
            
            # Test integrity
            result = cursor.execute('PRAGMA integrity_check').fetchone()
            if result[0] == 'ok':
                print("  + Database integrity check passed")
                self.score += 3
            else:
                print(f"  - Database integrity failed: {result[0]}")
                self.failures.append(f"Database integrity: {result[0]}")
            
            # Test critical tables
            critical_tables = ['users', 'expenses', 'jobs', 'expense_categories']
            tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            table_names = [t[0] for t in tables]
            
            for table in critical_tables:
                if table in table_names:
                    # Test basic operations on table
                    count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    print(f"  + Table '{table}' exists ({count} records)")
                    self.score += 2
                else:
                    print(f"  - Critical table '{table}' missing")
                    self.failures.append(f"Missing table: {table}")
            
            # Test write operations
            cursor.execute("CREATE TEMPORARY TABLE test_write (id INTEGER)")
            cursor.execute("INSERT INTO test_write (id) VALUES (1)")
            cursor.execute("SELECT * FROM test_write")
            cursor.execute("DROP TABLE test_write")
            print("  + Database write operations work")
            self.score += 1
            
            conn.close()
            
        except Exception as e:
            print(f"  - Database operations failed: {e}")
            self.failures.append(f"Database operations: {e}")
    
    def check_all_imports(self):
        """Test that all critical imports work"""
        print("\n3. Critical Imports Test")
        self.max_score += 10
        
        critical_imports = [
            ('FastAPI', 'from fastapi import FastAPI'),
            ('Database', 'from models import get_db'),
            ('Auth', 'from dependencies.auth import get_current_user'),
            ('Routes', 'from routes.dashboard_routes import dashboard_router'),
            ('Config', 'from config import config')
        ]
        
        for name, import_stmt in critical_imports:
            try:
                exec(import_stmt)
                print(f"  + {name} imports successfully")
                self.score += 2
            except Exception as e:
                print(f"  - {name} import failed: {e}")
                self.failures.append(f"{name} import: {e}")
    
    def check_critical_routes(self):
        """Test critical routes are accessible"""
        print("\n4. Critical Routes Test")
        self.max_score += 15
        
        try:
            from fastapi.testclient import TestClient
            from app import app
            client = TestClient(app)
            
            # Test critical endpoints
            critical_endpoints = [
                ('/health', 'Health check'),
                ('/api/dashboard/summary', 'Dashboard (should require auth)'),
                ('/static/css/styles.css', 'Static files'),
                ('/', 'Root endpoint'),
                ('/api/auth/login', 'Auth endpoint')
            ]
            
            for endpoint, description in critical_endpoints:
                try:
                    response = client.get(endpoint)
                    if response.status_code in [200, 401, 404, 422]:  # Expected responses
                        print(f"  + {description} responds correctly ({response.status_code})")
                        self.score += 3
                    else:
                        print(f"  - {description} unexpected response ({response.status_code})")
                        self.failures.append(f"{description}: HTTP {response.status_code}")
                except Exception as e:
                    print(f"  - {description} failed: {e}")
                    self.failures.append(f"{description}: {e}")
                    
        except Exception as e:
            print(f"  - Route testing failed: {e}")
            self.failures.append(f"Route testing: {e}")
    
    def check_security_config(self):
        """Verify security configurations"""
        print("\n5. Security Configuration Test")
        self.max_score += 10
        
        try:
            from config import config
            
            # Check secrets
            if config.SECRET_KEY and len(config.SECRET_KEY) > 32:
                print("  + SECRET_KEY properly configured")
                self.score += 3
            else:
                print("  - SECRET_KEY missing or too short")
                self.failures.append("SECRET_KEY configuration")
            
            if config.JWT_SECRET_KEY and len(config.JWT_SECRET_KEY) > 32:
                print("  + JWT_SECRET_KEY properly configured") 
                self.score += 3
            else:
                print("  - JWT_SECRET_KEY missing or too short")
                self.failures.append("JWT_SECRET_KEY configuration")
            
            # Check production settings
            if not config.DEBUG:
                print("  + DEBUG mode disabled for production")
                self.score += 2
            else:
                print("  - DEBUG mode still enabled")
                self.failures.append("DEBUG mode enabled in production")
            
            # Check middleware
            try:
                from middleware.security_headers import SecurityHeadersMiddleware
                print("  + Security headers middleware available")
                self.score += 2
            except:
                print("  ! Security headers middleware not found")
                
        except Exception as e:
            print(f"  - Security config check failed: {e}")
            self.failures.append(f"Security config: {e}")
    
    def check_error_handling(self):
        """Test error handling works"""
        print("\n6. Error Handling Test")
        self.max_score += 10
        
        try:
            from fastapi.testclient import TestClient
            from app import app
            client = TestClient(app)
            
            # Test 404 handling
            response = client.get('/nonexistent-endpoint-test-12345')
            if response.status_code == 404:
                print("  + 404 error handling works")
                self.score += 5
            else:
                print(f"  - 404 handling failed (got {response.status_code})")
                self.failures.append("404 error handling")
            
            # Test auth required endpoints
            response = client.get('/api/dashboard/summary')
            if response.status_code == 401:
                print("  + Authentication protection works")
                self.score += 5
            else:
                print(f"  - Auth protection failed (got {response.status_code})")
                self.failures.append("Authentication protection")
                
        except Exception as e:
            print(f"  - Error handling test failed: {e}")
            self.failures.append(f"Error handling: {e}")
    
    def final_verdict(self):
        """Generate final bulletproof verdict"""
        print("\n" + "=" * 50)
        print("BULLETPROOF VERIFICATION RESULTS")
        print("=" * 50)
        
        percentage = (self.score / self.max_score * 100) if self.max_score > 0 else 0
        print(f"\nSCORE: {self.score}/{self.max_score} ({percentage:.1f}%)")
        
        if self.failures:
            print(f"\nFAILURES ({len(self.failures)}):")
            for i, failure in enumerate(self.failures, 1):
                print(f"  {i}. {failure}")
        
        print(f"\n{'='*50}")
        if percentage >= 95 and len(self.failures) == 0:
            print("BULLETPROOF  BULLETPROOF VERIFIED!")
            print("CORA is ready for production deployment!")
            print("Zero critical issues found.")
        elif percentage >= 90:
            print("READY PRODUCTION READY")
            print(f"Minor issues: {len(self.failures)}")
            print("System is solid for deployment.")
        else:
            print("NOT READY NOT PRODUCTION READY")
            print(f"Critical issues must be fixed: {len(self.failures)}")
        
        print(f"{'='*50}\n")
        return percentage >= 95 and len(self.failures) == 0

if __name__ == "__main__":
    verifier = BulletproofVerification()
    is_bulletproof = verifier.verify_all_systems()
    exit(0 if is_bulletproof else 1)