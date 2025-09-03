#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/db_introspect.py
🎯 PURPOSE: Read-only database introspection utility
🔗 IMPORTS: SQLAlchemy, models
📤 EXPORTS: main() function for CLI execution
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import SessionLocal, User, Job, Expense, ExpenseCategory, Customer, Payment, Subscription
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


def json_serializer(obj):
    """JSON serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def get_table_counts(db):
    """Get row counts for all major tables"""
    counts = {}
    
    # Core tables to inspect
    tables = [
        ('users', User),
        ('jobs', Job),
        ('expenses', Expense),
        ('expense_categories', ExpenseCategory),
        ('customers', Customer),
        ('payments', Payment),
        ('subscriptions', Subscription)
    ]
    
    for table_name, model in tables:
        try:
            count = db.query(model).count()
            counts[table_name] = count
        except Exception as e:
            counts[table_name] = f"Error: {str(e)}"
    
    return counts


def get_recent_records(db, table_model, limit=5):
    """Get most recent records from a table"""
    try:
        # Get records ordered by created_at if available, otherwise by id
        if hasattr(table_model, 'created_at'):
            records = db.query(table_model).order_by(table_model.created_at.desc()).limit(limit).all()
        else:
            records = db.query(table_model).order_by(table_model.id.desc()).limit(limit).all()
        
        # Convert to dict format
        result = []
        for record in records:
            if hasattr(record, '__dict__'):
                # Remove SQLAlchemy internal attributes
                record_dict = {k: v for k, v in record.__dict__.items() if not k.startswith('_')}
                result.append(record_dict)
        
        return result
    except Exception as e:
        return f"Error: {str(e)}"


def check_integrity(db, source_counts=None):
    """Run enhanced integrity checks"""
    integrity = {}
    
    try:
        # Check for orphaned expenses (expenses without valid jobs)
        orphan_query = text("""
            SELECT COUNT(*) AS count
            FROM expenses e
            LEFT JOIN jobs j ON CAST(e.job_id AS INTEGER) = j.id
            WHERE e.job_id IS NOT NULL AND j.id IS NULL
        """)
        result = db.execute(orphan_query).first()
        integrity['orphaned_expenses'] = result.count if result else 0
        
        # Check for orphaned jobs (jobs without valid users)
        orphan_jobs_query = text("""
            SELECT COUNT(*) AS count
            FROM jobs j
            LEFT JOIN users u ON CAST(j.user_id AS INTEGER) = u.id
            WHERE j.user_id IS NOT NULL AND u.id IS NULL
        """)
        result = db.execute(orphan_jobs_query).first()
        integrity['orphaned_jobs'] = result.count if result else 0
        
        # Check for users without timezone
        no_tz_query = text("""
            SELECT COUNT(*) as count 
            FROM users 
            WHERE timezone IS NULL OR timezone = ''
        """)
        result = db.execute(no_tz_query).first()
        integrity['users_without_timezone'] = result.count if result else 0
        
        # Check admin user count
        admin_query = text("""
            SELECT COUNT(*) as count 
            FROM users 
            WHERE is_admin = 'true'
        """)
        result = db.execute(admin_query).first()
        integrity['admin_users'] = result.count if result else 0
        
        # Check distinct user count in jobs vs users table
        job_users_query = text("""
            SELECT COUNT(DISTINCT user_id) as count
            FROM jobs
            WHERE user_id IS NOT NULL
        """)
        result = db.execute(job_users_query).first()
        integrity['distinct_users_in_jobs'] = result.count if result else 0
        
        user_count_query = text("SELECT COUNT(*) as count FROM users")
        result = db.execute(user_count_query).first()
        integrity['total_users'] = result.count if result else 0
        
        # Row count parity check if source counts provided
        if source_counts:
            parity = {}
            for table, source_count in source_counts.items():
                if isinstance(source_count, int):
                    target_query = text(f"SELECT COUNT(*) as count FROM {table}")
                    result = db.execute(target_query).first()
                    target_count = result.count if result else 0
                    parity[table] = {
                        'source': source_count,
                        'target': target_count,
                        'match': source_count == target_count
                    }
            integrity['row_count_parity'] = parity
        
    except Exception as e:
        integrity['error'] = str(e)
    
    return integrity


def main():
    """Main introspection function"""
    parser = argparse.ArgumentParser(description='Database introspection utility')
    parser.add_argument('--recent', type=int, help='Show N most recent records per table')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--dsn', help='Database DSN (optional, uses app default if not provided)')
    parser.add_argument('--source-counts', help='JSON file with source counts for parity check')
    args = parser.parse_args()
    
    # Create database session
    if args.dsn:
        # Use provided DSN
        engine = create_engine(args.dsn, poolclass=NullPool)
        Session = sessionmaker(bind=engine)
        db = Session()
    else:
        # Use app's default session
        db = SessionLocal()
    
    try:
        # Load source counts if provided
        source_counts = None
        if args.source_counts:
            with open(args.source_counts, 'r') as f:
                source_data = json.load(f)
                source_counts = source_data.get('table_counts', {})
        
        # Gather all data
        data = {
            'table_counts': get_table_counts(db),
            'integrity_checks': check_integrity(db, source_counts)
        }
        
        # Add recent records if requested
        if args.recent:
            recent = {}
            tables = [
                ('users', User),
                ('jobs', Job),
                ('expenses', Expense)
            ]
            for table_name, model in tables:
                recent[table_name] = get_recent_records(db, model, args.recent)
            data['recent_records'] = recent
        
        # Output results
        if args.json:
            print(json.dumps(data, default=json_serializer, indent=2))
        else:
            # Human-readable output
            print("=== Database Introspection ===\n")
            
            print("Table Counts:")
            for table, count in data['table_counts'].items():
                print(f"  {table}: {count}")
            
            print("\nIntegrity Checks:")
            for check, result in data['integrity_checks'].items():
                print(f"  {check}: {result}")
            
            if args.recent and 'recent_records' in data:
                print(f"\nRecent Records (last {args.recent}):")
                for table, records in data['recent_records'].items():
                    print(f"\n  {table}:")
                    if isinstance(records, list):
                        for record in records:
                            if isinstance(record, dict):
                                print(f"    - ID: {record.get('id', 'N/A')}, "
                                      f"Email/Name: {record.get('email', record.get('title', 'N/A'))}")
        
        return 0
        
    except Exception as e:
        error_msg = {"status": "error", "message": str(e)}
        if args.json:
            print(json.dumps(error_msg))
        else:
            print(f"Error: {str(e)}")
        return 1
    
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())