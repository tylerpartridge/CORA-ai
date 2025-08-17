#!/usr/bin/env python3
"""
Safe Database Index Addition Script
Purpose: Add performance indexes to speed up common queries
Author: Claude (Opus 4.1)
Date: 2025-08-10
Safety: Indexes are additive only - cannot break existing functionality
"""

import sqlite3
from datetime import datetime
from pathlib import Path

def add_indexes_safely():
    """Add performance indexes to database"""
    
    db_path = Path('cora.db')
    if not db_path.exists():
        print("❌ Database not found at cora.db")
        return False
    
    print("="*60)
    print("SAFE DATABASE INDEX ADDITION")
    print("="*60)
    print("\nThis will add indexes to speed up common queries.")
    print("Indexes are additive only and cannot break functionality.\n")
    
    # Define indexes to add
    indexes = [
        {
            'name': 'idx_expenses_user_job',
            'table': 'expenses',
            'columns': '(user_id, job_name)',
            'purpose': 'Speed up expense lookups by user and job'
        },
        {
            'name': 'idx_jobs_user_date',
            'table': 'jobs', 
            'columns': '(user_id, start_date)',
            'purpose': 'Speed up job queries by user and date'
        },
        {
            'name': 'idx_user_activity_timestamp',
            'table': 'user_activity',
            'columns': '(user_id, timestamp)',
            'purpose': 'Speed up activity tracking queries'
        },
        {
            'name': 'idx_expenses_date',
            'table': 'expenses',
            'columns': '(expense_date)',
            'purpose': 'Speed up expense reports by date'
        },
        {
            'name': 'idx_jobs_status',
            'table': 'jobs',
            'columns': '(status)',
            'purpose': 'Speed up job filtering by status'
        },
        {
            'name': 'idx_expenses_category',
            'table': 'expenses',
            'columns': '(category)',
            'purpose': 'Speed up expense category analysis'
        }
    ]
    
    try:
        conn = sqlite3.connect('cora.db')
        cursor = conn.cursor()
        
        # Check existing indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        existing_indexes = set(row[0] for row in cursor.fetchall())
        
        print(f"Current indexes: {len(existing_indexes)}")
        
        added = 0
        skipped = 0
        
        for index in indexes:
            if index['name'] in existing_indexes:
                print(f"⏭️  {index['name']} already exists - skipping")
                skipped += 1
            else:
                try:
                    sql = f"CREATE INDEX IF NOT EXISTS {index['name']} ON {index['table']} {index['columns']}"
                    cursor.execute(sql)
                    print(f"✅ Added {index['name']} - {index['purpose']}")
                    added += 1
                except sqlite3.Error as e:
                    print(f"⚠️  Could not add {index['name']}: {e}")
        
        conn.commit()
        
        # Verify new count
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        new_count = len(cursor.fetchall())
        
        print("\n" + "="*60)
        print("RESULTS:")
        print(f"  Indexes added: {added}")
        print(f"  Indexes skipped: {skipped}")
        print(f"  Total indexes now: {new_count}")
        print("="*60)
        
        # Run ANALYZE to update statistics
        print("\nOptimizing database statistics...")
        cursor.execute("ANALYZE")
        print("✅ Database statistics updated")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("This script will add performance indexes to the database.")
    print("These changes are SAFE and reversible.\n")
    
    response = input("Continue? (y/n): ")
    if response.lower() == 'y':
        success = add_indexes_safely()
        if success:
            print("\n✅ Index addition complete! Database queries should be faster.")
        else:
            print("\n❌ Index addition failed. No changes were made.")
    else:
        print("Cancelled.")