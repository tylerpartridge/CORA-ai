#!/usr/bin/env python3
"""
CORA System Status Dashboard
Comprehensive health check for all system components
"""

import os
import sys
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

class SystemHealthDashboard:
    def __init__(self):
        self.checks = {}
        self.issues = []
        self.warnings = []
        self.successes = []
        
    def check_core_files(self):
        """Check that core application files exist"""
        core_files = [
            'app.py',
            'models.py', 
            'config.py',
            'requirements.txt',
            'cora.db'
        ]
        
        missing = []
        for file in core_files:
            if os.path.exists(file):
                self.successes.append(f"Core file exists: {file}")
            else:
                missing.append(file)
                self.issues.append(f"Missing core file: {file}")
                
        self.checks['core_files'] = len(missing) == 0
        return len(missing) == 0
        
    def check_database(self):
        """Check database health"""
        try:
            conn = sqlite3.connect('cora.db')
            cursor = conn.cursor()
            
            # Check integrity
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]
            
            if integrity != "ok":
                self.issues.append(f"Database integrity issue: {integrity}")
                self.checks['database_integrity'] = False
                return False
                
            # Get stats
            cursor.execute("SELECT COUNT(*) FROM users")
            users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM expenses")
            expenses = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM jobs")
            jobs = cursor.fetchone()[0]
            
            self.successes.append(f"Database OK - Users: {users}, Expenses: {expenses}, Jobs: {jobs}")
            self.checks['database'] = True
            
            conn.close()
            return True
            
        except Exception as e:
            self.issues.append(f"Database error: {str(e)}")
            self.checks['database'] = False
            return False
            
    def check_routes(self):
        """Check that API routes are registered"""
        try:
            from app import app
            
            route_count = len(app.routes)
            
            # Check for critical routes
            critical_paths = ['/api/auth/login', '/api/expenses', '/api/jobs']
            routes = [r.path for r in app.routes if hasattr(r, 'path')]
            
            missing_routes = [p for p in critical_paths if p not in routes]
            
            if missing_routes:
                self.warnings.append(f"Missing routes: {missing_routes}")
                
            self.successes.append(f"API routes registered: {route_count}")
            self.checks['routes'] = True
            return True
            
        except Exception as e:
            self.issues.append(f"Route check failed: {str(e)}")
            self.checks['routes'] = False
            return False
            
    def check_templates(self):
        """Check that template files exist"""
        template_dir = Path('web/templates')
        
        if not template_dir.exists():
            self.issues.append("Templates directory not found")
            self.checks['templates'] = False
            return False
            
        # Search recursively for all HTML templates
        templates = list(template_dir.glob('**/*.html'))
        
        critical_templates = ['index.html', 'login.html', 'dashboard.html']
        # Get all template names (including those in subdirectories)
        existing = [t.name for t in templates]
        
        missing = [t for t in critical_templates if t not in existing]
        
        if missing:
            self.warnings.append(f"Missing templates: {missing}")
            
        self.successes.append(f"Templates found: {len(templates)} (including subdirectories)")
        self.checks['templates'] = len(templates) > 0
        return len(templates) > 0
        
    def check_static_files(self):
        """Check static files"""
        static_dir = Path('web/static')
        
        if not static_dir.exists():
            self.issues.append("Static directory not found")
            self.checks['static_files'] = False
            return False
            
        css_files = list(static_dir.glob('**/*.css'))
        js_files = list(static_dir.glob('**/*.js'))
        
        self.successes.append(f"Static files - CSS: {len(css_files)}, JS: {len(js_files)}")
        self.checks['static_files'] = True
        return True
        
    def check_environment(self):
        """Check environment configuration"""
        env_vars = [
            'SECRET_KEY',
            'JWT_SECRET_KEY',
            'DATABASE_URL'
        ]
        
        missing_vars = []
        for var in env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
                
        if missing_vars:
            self.warnings.append(f"Missing env vars: {missing_vars}")
            
        self.checks['environment'] = len(missing_vars) < len(env_vars)
        return self.checks['environment']
        
    def check_security(self):
        """Check security configurations"""
        security_files = [
            'middleware/csrf.py',
            'middleware/rate_limit.py',
            'middleware/security_headers.py'
        ]
        
        found = 0
        for file in security_files:
            if os.path.exists(file):
                found += 1
                
        self.successes.append(f"Security middleware files: {found}/{len(security_files)}")
        self.checks['security'] = found > 0
        return found > 0
        
    def check_recent_activity(self):
        """Check for recent system activity"""
        try:
            conn = sqlite3.connect('cora.db')
            cursor = conn.cursor()
            
            # Check for recent data (last 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            try:
                cursor.execute("""
                    SELECT COUNT(*) FROM expenses 
                    WHERE created_at > ?
                """, (thirty_days_ago,))
                recent_expenses = cursor.fetchone()[0]
                
                if recent_expenses > 0:
                    self.successes.append(f"Recent activity: {recent_expenses} expenses in last 30 days")
                else:
                    self.warnings.append("No recent expense activity")
            except:
                # Table might not have created_at column
                pass
                
            conn.close()
            self.checks['activity'] = True
            return True
            
        except Exception as e:
            self.warnings.append(f"Could not check activity: {str(e)}")
            return True
            
    def generate_report(self):
        """Generate status report"""
        total_checks = len(self.checks)
        passed_checks = sum(1 for v in self.checks.values() if v)
        health_percentage = int((passed_checks / total_checks * 100) if total_checks > 0 else 0)
        
        print("\n" + "="*70)
        print(" "*20 + "CORA SYSTEM STATUS DASHBOARD")
        print("="*70)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Health Score: {health_percentage}% ({passed_checks}/{total_checks} checks passed)")
        print("-"*70)
        
        # Overall Status
        if health_percentage >= 80:
            status = "OPERATIONAL"
            status_symbol = "[OK]"
        elif health_percentage >= 60:
            status = "DEGRADED"
            status_symbol = "[WARN]"
        else:
            status = "CRITICAL"
            status_symbol = "[FAIL]"
            
        print(f"\nSystem Status: {status_symbol} {status}")
        
        # Component Status
        print("\nComponent Status:")
        print("-"*40)
        for component, status in self.checks.items():
            status_text = "[OK]" if status else "[FAIL]"
            formatted_name = component.replace('_', ' ').title()
            print(f"  {status_text:6} {formatted_name}")
            
        # Issues
        if self.issues:
            print("\nCritical Issues:")
            print("-"*40)
            for issue in self.issues:
                print(f"  [!] {issue}")
                
        # Warnings
        if self.warnings:
            print("\nWarnings:")
            print("-"*40)
            for warning in self.warnings:
                print(f"  [?] {warning}")
                
        # Successes
        if self.successes:
            print("\nOperational Components:")
            print("-"*40)
            for success in self.successes[:5]:  # Show first 5
                print(f"  [+] {success}")
                
        # Recommendations
        print("\nRecommendations:")
        print("-"*40)
        
        if health_percentage < 60:
            print("  1. Address critical issues immediately")
            print("  2. Check error logs for details")
            print("  3. Verify database integrity")
        elif health_percentage < 80:
            print("  1. Review warnings and plan fixes")
            print("  2. Monitor system performance")
            print("  3. Update missing environment variables")
        else:
            print("  1. System is healthy - continue monitoring")
            print("  2. Consider running tests regularly")
            print("  3. Keep dependencies updated")
            
        print("\n" + "="*70 + "\n")
        
        # Save report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'health_percentage': health_percentage,
            'status': status,
            'checks': self.checks,
            'issues': self.issues,
            'warnings': self.warnings,
            'successes': self.successes
        }
        
        report_file = f"system_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = Path(__file__).parent / report_file
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        print(f"Report saved to: features/system_health/claude/{report_file}")
        
        return health_percentage
        
    def run_health_check(self):
        """Run all health checks"""
        print("\nRunning system health checks...")
        
        self.check_core_files()
        self.check_database()
        self.check_routes()
        self.check_templates()
        self.check_static_files()
        self.check_environment()
        self.check_security()
        self.check_recent_activity()
        
        return self.generate_report()


if __name__ == "__main__":
    dashboard = SystemHealthDashboard()
    health_score = dashboard.run_health_check()
    
    # Exit with appropriate code
    if health_score >= 80:
        exit(0)  # Healthy
    elif health_score >= 60:
        exit(1)  # Degraded
    else:
        exit(2)  # Critical