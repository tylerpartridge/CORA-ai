#!/usr/bin/env python3
"""
Database Health Check Script
Monitors database integrity, performance, and issues
"""

import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path
import json

class DatabaseHealthChecker:
    def __init__(self, db_path="cora.db"):
        self.db_path = db_path
        self.issues = []
        self.stats = {}
        
    def check_database_exists(self):
        """Check if database file exists and is accessible"""
        if not os.path.exists(self.db_path):
            self.issues.append(f"❌ Database file {self.db_path} not found")
            return False
            
        if not os.access(self.db_path, os.R_OK):
            self.issues.append(f"❌ Database file {self.db_path} is not readable")
            return False
            
        self.stats['file_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
        return True
        
    def check_integrity(self):
        """Run SQLite integrity check"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            
            if result != "ok":
                self.issues.append(f"❌ Database integrity check failed: {result}")
                return False
                
            conn.close()
            return True
        except Exception as e:
            self.issues.append(f"❌ Could not check integrity: {str(e)}")
            return False
            
    def check_schema(self):
        """Check for required tables and columns"""
        required_tables = [
            'users',
            'expenses', 
            'jobs',
            'business_profiles',
            'email_verification_tokens',
            'password_reset_tokens'
        ]
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            self.stats['total_tables'] = len(existing_tables)
            
            # Check for missing tables
            missing_tables = [t for t in required_tables if t not in existing_tables]
            if missing_tables:
                self.issues.append(f"❌ Missing required tables: {', '.join(missing_tables)}")
                
            # Check critical table columns
            cursor.execute("PRAGMA table_info(users)")
            user_columns = [row[1] for row in cursor.fetchall()]
            
            required_user_columns = ['id', 'email', 'hashed_password', 'is_active']
            missing_columns = [c for c in required_user_columns if c not in user_columns]
            
            if missing_columns:
                self.issues.append(f"❌ Missing columns in users table: {', '.join(missing_columns)}")
                
            conn.close()
            return len(missing_tables) == 0
            
        except Exception as e:
            self.issues.append(f"❌ Schema check failed: {str(e)}")
            return False
            
    def check_data_statistics(self):
        """Gather statistics about the data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count users
            cursor.execute("SELECT COUNT(*) FROM users")
            self.stats['total_users'] = cursor.fetchone()[0]
            
            # Count active users
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
            self.stats['active_users'] = cursor.fetchone()[0]
            
            # Count expenses
            cursor.execute("SELECT COUNT(*) FROM expenses")
            self.stats['total_expenses'] = cursor.fetchone()[0]
            
            # Count jobs
            cursor.execute("SELECT COUNT(*) FROM jobs")
            self.stats['total_jobs'] = cursor.fetchone()[0]
            
            # Check for orphaned records
            cursor.execute("""
                SELECT COUNT(*) FROM expenses 
                WHERE user_id NOT IN (SELECT id FROM users)
            """)
            orphaned_expenses = cursor.fetchone()[0]
            
            if orphaned_expenses > 0:
                self.issues.append(f"⚠️ Found {orphaned_expenses} orphaned expense records")
                
            conn.close()
            return True
            
        except Exception as e:
            self.issues.append(f"⚠️ Could not gather statistics: {str(e)}")
            return False
            
    def check_performance(self):
        """Check database performance indicators"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for missing indexes
            cursor.execute("""
                SELECT name, tbl_name FROM sqlite_master 
                WHERE type = 'index' AND sql IS NOT NULL
            """)
            indexes = cursor.fetchall()
            self.stats['total_indexes'] = len(indexes)
            
            # Check page count and fragmentation
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA freelist_count")
            freelist_count = cursor.fetchone()[0]
            
            fragmentation = (freelist_count / page_count * 100) if page_count > 0 else 0
            self.stats['fragmentation_percent'] = round(fragmentation, 2)
            
            if fragmentation > 20:
                self.issues.append(f"⚠️ Database fragmentation is high: {fragmentation:.1f}%")
                
            conn.close()
            return True
            
        except Exception as e:
            self.issues.append(f"⚠️ Performance check failed: {str(e)}")
            return False
            
    def check_recent_activity(self):
        """Check for recent database activity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for recent expenses (last 7 days)
            seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT COUNT(*) FROM expenses 
                WHERE created_at > ?
            """, (seven_days_ago,))
            
            recent_expenses = cursor.fetchone()[0]
            self.stats['recent_expenses_7d'] = recent_expenses
            
            # Check for recent users
            cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE created_at > ?
            """, (seven_days_ago,))
            
            recent_users = cursor.fetchone()[0]
            self.stats['recent_users_7d'] = recent_users
            
            conn.close()
            return True
            
        except Exception as e:
            # Not critical if timestamps don't exist
            return True
            
    def generate_report(self):
        """Generate health check report"""
        print("\n" + "="*60)
        print("📊 DATABASE HEALTH CHECK REPORT")
        print("="*60)
        print(f"Database: {self.db_path}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*60)
        
        # Overall health
        health_score = 100 - (len(self.issues) * 10)
        health_score = max(0, health_score)
        
        if health_score >= 80:
            health_status = "✅ HEALTHY"
            health_color = ""
        elif health_score >= 60:
            health_status = "⚠️ NEEDS ATTENTION"
            health_color = ""
        else:
            health_status = "❌ CRITICAL"
            health_color = ""
            
        print(f"\n🏥 Overall Health: {health_status} ({health_score}%)")
        
        # Statistics
        print("\n📈 Database Statistics:")
        for key, value in self.stats.items():
            formatted_key = key.replace('_', ' ').title()
            if isinstance(value, float):
                print(f"  • {formatted_key}: {value:.2f}")
            else:
                print(f"  • {formatted_key}: {value}")
                
        # Issues
        if self.issues:
            print("\n⚠️ Issues Found:")
            for issue in self.issues:
                print(f"  {issue}")
        else:
            print("\n✅ No issues found!")
            
        # Recommendations
        print("\n💡 Recommendations:")
        if self.stats.get('fragmentation_percent', 0) > 10:
            print("  • Run VACUUM to reduce fragmentation")
        if self.stats.get('total_indexes', 0) < 5:
            print("  • Consider adding indexes for frequently queried columns")
        if self.stats.get('file_size_mb', 0) > 100:
            print("  • Consider archiving old data")
        if not self.issues:
            print("  • Continue regular monitoring")
            
        print("\n" + "="*60 + "\n")
        
        # Save report to file
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'database': self.db_path,
            'health_score': health_score,
            'statistics': self.stats,
            'issues': self.issues
        }
        
        report_file = f"database_health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(f"/mnt/host/c/CORA/features/database_health/claude/{report_file}", 'w') as f:
            json.dump(report_data, f, indent=2)
            
        print(f"📄 Report saved to: features/database_health/claude/{report_file}")
        
    def run_health_check(self):
        """Run complete health check"""
        print("🔍 Starting database health check...")
        
        if not self.check_database_exists():
            self.generate_report()
            return False
            
        self.check_integrity()
        self.check_schema()
        self.check_data_statistics()
        self.check_performance()
        self.check_recent_activity()
        
        self.generate_report()
        return len(self.issues) == 0


if __name__ == "__main__":
    checker = DatabaseHealthChecker()
    healthy = checker.run_health_check()
    
    # Exit with appropriate code
    exit(0 if healthy else 1)