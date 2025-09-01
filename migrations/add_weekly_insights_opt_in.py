#!/usr/bin/env python3
"""
Add weekly_insights_opt_in column to users table

Run this migration to add the weekly insights opt-in preference field.
"""

import sqlite3
import sys
from pathlib import Path

def upgrade():
    """Add weekly_insights_opt_in column to users table"""
    try:
        # Connect to database
        db_path = Path(__file__).parent.parent / "cora.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'weekly_insights_opt_in' not in columns:
            # Add the column with default value 'true'
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN weekly_insights_opt_in TEXT DEFAULT 'true'
            """)
            print("Added weekly_insights_opt_in column to users table")
        else:
            print("Column weekly_insights_opt_in already exists")
        
        conn.commit()
        conn.close()
        print("Migration completed successfully")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)

def downgrade():
    """Remove weekly_insights_opt_in column from users table"""
    # SQLite doesn't support DROP COLUMN directly
    # Would need to recreate table without the column
    print("Downgrade not implemented for SQLite")

if __name__ == "__main__":
    upgrade()