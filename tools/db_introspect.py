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
from sqlalchemy import text


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


def check_integrity(db):
    """Run basic integrity checks"""
    integrity = {}
    
    try:
        # Check for orphaned expenses (expenses without valid jobs)
        orphan_query = text("""
            SELECT COUNT(*) as count 
            FROM expenses e 
            LEFT JOIN jobs j ON e.job_id = j.id 
            WHERE e.job_id IS NOT NULL AND j.id IS NULL
        """)
        result = db.execute(orphan_query).first()
        integrity['orphaned_expenses'] = result.count if result else 0
        
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
        
    except Exception as e:
        integrity['error'] = str(e)
    
    return integrity


def main():
    """Main introspection function"""
    parser = argparse.ArgumentParser(description='Database introspection utility')
    parser.add_argument('--recent', type=int, help='Show N most recent records per table')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    args = parser.parse_args()
    
    db = SessionLocal()
    
    try:
        # Gather all data
        data = {
            'table_counts': get_table_counts(db),
            'integrity_checks': check_integrity(db)
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