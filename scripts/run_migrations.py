#!/usr/bin/env python3
"""
Migration runner for CORA database
Executes SQL migration files in order
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config

def get_db_connection():
    """Create database connection using config"""
    # Extract database URL components
    db_url = config.DATABASE_URL
    if db_url.startswith('postgresql://'):
        db_url = db_url.replace('postgresql://', '')
    
    # Parse connection string
    if '@' in db_url:
        auth, hostpath = db_url.split('@')
        if ':' in auth:
            user, password = auth.split(':')
        else:
            user = auth
            password = None
        
        if '/' in hostpath:
            hostport, dbname = hostpath.split('/', 1)
            if ':' in hostport:
                host, port = hostport.split(':')
            else:
                host = hostport
                port = '5432'
        else:
            host = hostpath
            port = '5432'
            dbname = 'cora'
    else:
        # Fallback to defaults
        user = 'postgres'
        password = None
        host = 'localhost'
        port = '5432'
        dbname = 'cora'
    
    return psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )

def create_migrations_table(conn):
    """Create migrations tracking table if it doesn't exist"""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def has_migration_been_applied(conn, filename):
    """Check if a migration has already been applied"""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM schema_migrations WHERE filename = %s",
            (filename,)
        )
        return cur.fetchone() is not None

def record_migration(conn, filename):
    """Record that a migration has been applied"""
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO schema_migrations (filename) VALUES (%s)",
            (filename,)
        )
        conn.commit()

def run_migration(conn, filepath, filename):
    """Execute a single migration file"""
    print(f"Running migration: {filename}")
    
    with open(filepath, 'r') as f:
        migration_sql = f.read()
    
    try:
        with conn.cursor() as cur:
            cur.execute(migration_sql)
        conn.commit()
        record_migration(conn, filename)
        print(f"✅ Successfully applied: {filename}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to apply {filename}: {str(e)}")
        return False

def main():
    """Run all pending migrations"""
    migrations_dir = os.path.join(os.path.dirname(__file__), '..', 'schema', 'migrations')
    
    if not os.path.exists(migrations_dir):
        print(f"Migrations directory not found: {migrations_dir}")
        return 1
    
    # Get all SQL files in migrations directory
    migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
    
    if not migration_files:
        print("No migration files found")
        return 0
    
    try:
        conn = get_db_connection()
        create_migrations_table(conn)
        
        applied_count = 0
        failed_count = 0
        
        for filename in migration_files:
            if has_migration_been_applied(conn, filename):
                print(f"⏭️  Skipping already applied: {filename}")
                continue
            
            filepath = os.path.join(migrations_dir, filename)
            if run_migration(conn, filepath, filename):
                applied_count += 1
            else:
                failed_count += 1
                # Stop on first failure
                break
        
        print(f"\n📊 Migration Summary:")
        print(f"   Applied: {applied_count}")
        print(f"   Failed: {failed_count}")
        print(f"   Total: {len(migration_files)}")
        
        conn.close()
        return 1 if failed_count > 0 else 0
        
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())