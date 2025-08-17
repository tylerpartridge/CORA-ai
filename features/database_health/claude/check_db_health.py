#!/usr/bin/env python3
"""
Database Health Check - Simple Version
"""

import sqlite3
import os
from datetime import datetime, timedelta

def check_database_health(db_path="cora.db"):
    """Run database health checks"""
    
    print("\n" + "="*60)
    print("DATABASE HEALTH CHECK")
    print("="*60)
    print(f"Database: {db_path}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*60)
    
    issues = []
    stats = {}
    
    # Check file exists
    if not os.path.exists(db_path):
        print(f"ERROR: Database file {db_path} not found")
        return False
        
    stats['file_size_mb'] = round(os.path.getsize(db_path) / (1024 * 1024), 2)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Integrity check
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]
        if integrity != "ok":
            issues.append(f"Integrity check failed: {integrity}")
            
        # Get table list
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        stats['total_tables'] = len(tables)
        
        # Check for required tables
        required_tables = ['users', 'expenses', 'jobs', 'business_profiles']
        missing_tables = [t for t in required_tables if t not in tables]
        if missing_tables:
            issues.append(f"Missing tables: {', '.join(missing_tables)}")
            
        # Count records
        if 'users' in tables:
            cursor.execute("SELECT COUNT(*) FROM users")
            stats['total_users'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
            stats['active_users'] = cursor.fetchone()[0]
            
        if 'expenses' in tables:
            cursor.execute("SELECT COUNT(*) FROM expenses")
            stats['total_expenses'] = cursor.fetchone()[0]
            
        if 'jobs' in tables:
            cursor.execute("SELECT COUNT(*) FROM jobs")
            stats['total_jobs'] = cursor.fetchone()[0]
            
        # Check for orphaned expenses
        if 'expenses' in tables and 'users' in tables:
            cursor.execute("""
                SELECT COUNT(*) FROM expenses 
                WHERE user_id NOT IN (SELECT id FROM users)
            """)
            orphaned = cursor.fetchone()[0]
            if orphaned > 0:
                issues.append(f"Found {orphaned} orphaned expense records")
                
        # Check indexes
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type = 'index' AND sql IS NOT NULL
        """)
        stats['total_indexes'] = len(cursor.fetchall())
        
        # Check fragmentation
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA freelist_count") 
        freelist_count = cursor.fetchone()[0]
        
        if page_count > 0:
            fragmentation = round((freelist_count / page_count * 100), 2)
            stats['fragmentation_percent'] = fragmentation
            
            if fragmentation > 20:
                issues.append(f"High fragmentation: {fragmentation}%")
                
        conn.close()
        
    except Exception as e:
        print(f"ERROR during check: {str(e)}")
        return False
        
    # Print results
    print("\nDatabase Statistics:")
    for key, value in stats.items():
        formatted_key = key.replace('_', ' ').title()
        print(f"  - {formatted_key}: {value}")
        
    if issues:
        print("\nIssues Found:")
        for issue in issues:
            print(f"  ! {issue}")
    else:
        print("\nNo issues found - Database is healthy!")
        
    # Health score
    health_score = 100 - (len(issues) * 10)
    health_score = max(0, health_score)
    
    print(f"\nHealth Score: {health_score}%")
    
    if health_score >= 80:
        print("Status: HEALTHY")
    elif health_score >= 60:
        print("Status: NEEDS ATTENTION")
    else:
        print("Status: CRITICAL")
        
    print("\n" + "="*60 + "\n")
    
    return len(issues) == 0


if __name__ == "__main__":
    healthy = check_database_health()
    exit(0 if healthy else 1)