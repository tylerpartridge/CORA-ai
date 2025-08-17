#!/usr/bin/env python3
"""
PostgreSQL Migration Script for CORA
Migrates data from SQLite to PostgreSQL
"""

import os
import sys
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
import uuid
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base import Base
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuration
SQLITE_DB_PATH = "./data/cora.db"
POSTGRES_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'cora_db',
    'user': 'cora_user',
    'password': 'cora_password'
}

def log(message, level="INFO"):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def test_postgres_connection():
    """Test PostgreSQL connection"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        conn.close()
        log("✅ PostgreSQL connection successful")
        return True
    except Exception as e:
        log(f"❌ PostgreSQL connection failed: {e}", "ERROR")
        return False

def create_postgres_schema():
    """Create PostgreSQL schema using SQLAlchemy"""
    try:
        # Create PostgreSQL engine
        postgres_url = f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"
        engine = create_engine(postgres_url)
        
        # Create all tables
        Base.metadata.create_all(engine)
        log("✅ PostgreSQL schema created successfully")
        return True
    except Exception as e:
        log(f"❌ Failed to create PostgreSQL schema: {e}", "ERROR")
        return False

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
        sqlite_conn.row_factory = sqlite3.Row
        
        # Connect to PostgreSQL
        postgres_conn = psycopg2.connect(**POSTGRES_CONFIG)
        postgres_cursor = postgres_conn.cursor()
        
        # Get all tables from SQLite
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in sqlite_cursor.fetchall()]
        
        log(f"📋 Found {len(tables)} tables to migrate: {', '.join(tables)}")
        
        total_records = 0
        
        # Build email to UUID mapping for users
        user_email_to_uuid = {}
        if 'users' in tables:
            sqlite_cursor.execute("SELECT * FROM users")
            user_rows = sqlite_cursor.fetchall()
            user_columns = [description[0] for description in sqlite_cursor.description]
            user_data = []
            for row in user_rows:
                row_dict = {col: row[idx] for idx, col in enumerate(user_columns)}
                user_uuid = str(uuid.uuid4())
                user_email_to_uuid[row_dict['email']] = user_uuid
                # Compose row for PostgreSQL: id (uuid), email, hashed_password, created_at, is_active
                user_data.append((user_uuid, row_dict['email'], row_dict.get('hashed_password', ''), row_dict.get('created_at', None), bool(row_dict.get('is_active', 1))))
            # Clear users table before migration
            postgres_cursor.execute("DELETE FROM users")
            postgres_conn.commit()
            insert_query = "INSERT INTO users (id, email, hashed_password, created_at, is_active) VALUES (%s, %s, %s, %s, %s)"
            if user_data:
                postgres_cursor.executemany(insert_query, user_data)
                postgres_conn.commit()
            log(f"✅ Migrated {len(user_data)} records from users")
            total_records += len(user_data)

        for table in tables:
            if table == 'users':
                continue  # Already handled above
            try:
                sqlite_cursor.execute(f"SELECT * FROM {table}")
                rows = sqlite_cursor.fetchall()
                if not rows:
                    log(f"⏭️  Table {table} is empty, skipping")
                    continue
                columns = [description[0] for description in sqlite_cursor.description]
                data = []
                if table == 'feedback':
                    # Map user_email to user_id (UUID)
                    for row in rows:
                        row_dict = {col: row[idx] for idx, col in enumerate(columns)}
                        user_email = row_dict.get('user_email') or row_dict.get('email')
                        user_id = user_email_to_uuid.get(user_email)
                        if not user_id:
                            log(f"Skipping feedback row: cannot map user_email {user_email}", "ERROR")
                            continue
                        feedback_row = (
                            int(row_dict['id']) if 'id' in row_dict else None,
                            str(user_id),
                            row_dict['category'],
                            row_dict['message'],
                            row_dict.get('rating'),
                            row_dict.get('created_at')
                        )
                        data.append(feedback_row)
                    postgres_cursor.execute("DELETE FROM feedback")
                    postgres_conn.commit()
                    insert_query = "INSERT INTO feedback (id, user_id, category, message, rating, created_at) VALUES (%s, %s, %s, %s, %s, %s)"
                elif table == 'password_reset_tokens':
                    for row in rows:
                        row_dict = {col: row[idx] for idx, col in enumerate(columns)}
                        row_data = []
                        for col in columns:
                            value = row_dict[col]
                            if col == 'used':
                                value = str(value).lower() if value is not None else 'false'
                            if col == 'id':
                                value = int(value) if value is not None else None
                            row_data.append(value)
                        data.append(tuple(row_data))
                    postgres_cursor.execute("DELETE FROM password_reset_tokens")
                    postgres_conn.commit()
                    placeholders = ', '.join(['%s'] * len(columns))
                    insert_query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                else:
                    for row in rows:
                        row_dict = {col: row[idx] for idx, col in enumerate(columns)}
                        row_data = []
                        for col in columns:
                            value = row_dict[col]
                            if col == 'id' and (value is None or value == '' or (table in ['expenses', 'customers', 'subscriptions', 'payments'] and not isinstance(value, str))):
                                value = str(uuid.uuid4())
                            if table == 'expense_categories' and col == 'is_active':
                                value = bool(value)
                            row_data.append(value)
                        data.append(tuple(row_data))
                    postgres_cursor.execute(f"DELETE FROM {table}")
                    postgres_conn.commit()
                    placeholders = ', '.join(['%s'] * len(columns))
                    insert_query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                if data:
                    postgres_cursor.executemany(insert_query, data)
                    postgres_conn.commit()
                log(f"✅ Migrated {len(data)} records from {table}")
                total_records += len(data)
            except Exception as e:
                log(f"❌ Failed to migrate table {table}: {e}", "ERROR")
                postgres_conn.rollback()
                continue
        
        sqlite_conn.close()
        postgres_conn.close()
        
        log(f"🎉 Migration completed! Total records migrated: {total_records}")
        return True
        
    except Exception as e:
        log(f"❌ Migration failed: {e}", "ERROR")
        return False

def verify_migration():
    """Verify migration by comparing record counts"""
    try:
        # Connect to both databases
        sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
        postgres_conn = psycopg2.connect(**POSTGRES_CONFIG)
        
        sqlite_cursor = sqlite_conn.cursor()
        postgres_cursor = postgres_conn.cursor()
        
        # Get tables
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in sqlite_cursor.fetchall()]
        
        log("🔍 Verifying migration...")
        
        for table in tables:
            # Count SQLite records
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            sqlite_count = sqlite_cursor.fetchone()[0]
            
            # Count PostgreSQL records
            postgres_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            postgres_count = postgres_cursor.fetchone()[0]
            
            if sqlite_count == postgres_count:
                log(f"✅ {table}: {sqlite_count} records match")
            else:
                log(f"❌ {table}: SQLite={sqlite_count}, PostgreSQL={postgres_count}", "ERROR")
        
        sqlite_conn.close()
        postgres_conn.close()
        
    except Exception as e:
        log(f"❌ Verification failed: {e}", "ERROR")

def main():
    """Main migration function"""
    log("🚀 Starting PostgreSQL migration...")
    
    # Check if SQLite database exists
    if not os.path.exists(SQLITE_DB_PATH):
        log(f"❌ SQLite database not found at {SQLITE_DB_PATH}", "ERROR")
        return False
    
    # Test PostgreSQL connection
    if not test_postgres_connection():
        return False
    
    # Create PostgreSQL schema
    if not create_postgres_schema():
        return False
    
    # Migrate data
    if not migrate_data():
        return False
    
    # Verify migration
    verify_migration()
    
    log("🎉 PostgreSQL migration completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 