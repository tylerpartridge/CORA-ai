#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/migrate_sqlite_to_postgres.py
🎯 PURPOSE: Transactional SQLite to PostgreSQL migration with dry-run and JSONL logging
🔗 IMPORTS: SQLAlchemy, models, argparse, json
📤 EXPORTS: main() function for CLI execution
"""

import os
import sys
import json
import time
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, MetaData, Table, select, func, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

# Import all models in dependency order
from models.base import Base
from models.user import User
from models.expense_category import ExpenseCategory
from models.customer import Customer
from models.business_profile import BusinessProfile
from models.user_preference import UserPreference
from models.job import Job, JobNote
from models.expense import Expense
from models.payment import Payment
from models.subscription import Subscription
from models.password_reset_token import PasswordResetToken
from models.email_verification_token import EmailVerificationToken
from models.plaid_integration import PlaidIntegration, PlaidAccount, PlaidTransaction, PlaidSyncHistory
from models.quickbooks_integration import QuickBooksIntegration
from models.stripe_integration import StripeIntegration
from models.feedback import Feedback
from models.user_activity import UserActivity
from models.waitlist import ContractorWaitlist
from models.job_alert import JobAlert
from models.analytics import AnalyticsLog
from models.prediction_feedback import PredictionFeedback
from models.intelligence_state import IntelligenceSignal, EmotionalProfile

# Try to import optional model
try:
    from models.user_onboarding_step import UserOnboardingStep
    HAS_ONBOARDING = True
except ImportError:
    HAS_ONBOARDING = False


class MigrationLogger:
    """JSONL logger for migration events"""
    
    def __init__(self, log_path: Optional[str] = None):
        self.log_path = log_path
        self.events = []
        
    def log(self, event: dict):
        """Log an event"""
        event['timestamp'] = datetime.utcnow().isoformat()
        self.events.append(event)
        
        if self.log_path:
            with open(self.log_path, 'a') as f:
                f.write(json.dumps(event) + '\n')
    
    def summary(self):
        """Return summary of events"""
        return {
            'total_events': len(self.events),
            'errors': len([e for e in self.events if e.get('status') == 'error']),
            'tables_migrated': len([e for e in self.events if e.get('type') == 'table_complete'])
        }


def get_table_order():
    """Return tables in dependency order for migration"""
    # Core tables in FK dependency order
    tables = [
        # Independent tables first
        ('users', User),
        ('expense_categories', ExpenseCategory),
        ('business_profiles', BusinessProfile),
        
        # Tables with user FK
        ('user_preferences', UserPreference),
        ('customers', Customer),
        ('jobs', Job),
        ('password_reset_tokens', PasswordResetToken),
        ('email_verification_tokens', EmailVerificationToken),
        ('plaid_integrations', PlaidIntegration),
        ('quickbooks_integrations', QuickBooksIntegration),
        ('stripe_integrations', StripeIntegration),
        ('feedback', Feedback),
        ('user_activities', UserActivity),
        ('contractor_waitlist', ContractorWaitlist),
        ('job_alerts', JobAlert),
        ('analytics_logs', AnalyticsLog),
        ('intelligence_signals', IntelligenceSignal),
        ('emotional_profiles', EmotionalProfile),
        
        # Tables with job FK (must come after jobs)
        ('job_notes', JobNote),
        ('expenses', Expense),
        
        # Tables with multiple FKs
        ('payments', Payment),
        ('subscriptions', Subscription),
        ('prediction_feedback', PredictionFeedback),
        
        # Plaid sub-tables (after plaid_integrations)
        ('plaid_accounts', PlaidAccount),
        ('plaid_transactions', PlaidTransaction),
        ('plaid_sync_history', PlaidSyncHistory),
    ]
    
    # Add optional tables if available
    if HAS_ONBOARDING:
        tables.insert(tables.index(('user_preferences', UserPreference)) + 1, 
                     ('user_onboarding_steps', UserOnboardingStep))
    
    return tables


def hash_row(row: dict) -> str:
    """Create deterministic hash of a row for comparison"""
    # Sort keys for consistency
    sorted_items = sorted(row.items())
    # Convert to string representation
    row_str = str(sorted_items)
    return hashlib.md5(row_str.encode()).hexdigest()


def migrate_table(
    source_session: Session,
    target_session: Session,
    table_name: str,
    model_class: Any,
    batch_size: int = 1000,
    dry_run: bool = False,
    logger: Optional[MigrationLogger] = None
) -> Dict[str, Any]:
    """Migrate a single table"""
    
    start_time = time.time()
    result = {
        'table': table_name,
        'source_count': 0,
        'target_count': 0,
        'duration': 0,
        'status': 'pending'
    }
    
    try:
        # Get source count
        source_count = source_session.query(model_class).count()
        result['source_count'] = source_count
        
        if logger:
            logger.log({
                'type': 'table_start',
                'table': table_name,
                'source_count': source_count,
                'dry_run': dry_run
            })
        
        if dry_run:
            # In dry-run, just validate we can read the data
            sample = source_session.query(model_class).limit(10).all()
            result['status'] = 'dry_run'
            result['sample_count'] = len(sample)
        else:
            # Clear target table if requested (for rehearsal)
            # Note: This is handled by truncate-target option
            
            # Migrate in batches
            offset = 0
            migrated = 0
            
            while offset < source_count:
                batch = source_session.query(model_class).offset(offset).limit(batch_size).all()
                
                if not batch:
                    break
                
                for record in batch:
                    # Create new instance with same data
                    record_dict = {c.name: getattr(record, c.name) 
                                  for c in model_class.__table__.columns}
                    new_record = model_class(**record_dict)
                    target_session.add(new_record)
                    migrated += 1
                
                # Flush batch (but don't commit - that's done at transaction level)
                target_session.flush()
                offset += batch_size
                
                if logger:
                    logger.log({
                        'type': 'batch_complete',
                        'table': table_name,
                        'offset': offset,
                        'migrated': migrated
                    })
            
            result['target_count'] = migrated
            result['status'] = 'complete'
        
        result['duration'] = time.time() - start_time
        
        if logger:
            logger.log({
                'type': 'table_complete',
                'table': table_name,
                'source_count': source_count,
                'target_count': result.get('target_count', 0),
                'duration': result['duration'],
                'status': result['status']
            })
        
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
        result['duration'] = time.time() - start_time
        
        if logger:
            logger.log({
                'type': 'table_error',
                'table': table_name,
                'error': str(e),
                'duration': result['duration']
            })
        
        raise
    
    return result


def main():
    """Main migration function"""
    parser = argparse.ArgumentParser(description='SQLite to PostgreSQL migration')
    parser.add_argument('--sqlite-path', 
                       default=os.getenv('SQLITE_PATH', '/var/www/cora/cora.db'),
                       help='Path to source SQLite database')
    parser.add_argument('--pg-dsn',
                       default=os.getenv('REHEARSAL_PG_DSN'),
                       help='PostgreSQL DSN (e.g., postgresql://user:pass@host/db)')
    parser.add_argument('--batch-size', type=int, default=1000,
                       help='Batch size for migration')
    parser.add_argument('--dry-run', action='store_true',
                       help='Validate without writing')
    parser.add_argument('--stop-on-error', action='store_true',
                       help='Stop and rollback on first error')
    parser.add_argument('--jsonl', dest='log_path',
                       help='Path for JSONL log output')
    parser.add_argument('--tables',
                       help='Comma-separated list of tables to migrate')
    parser.add_argument('--truncate-target', action='store_true',
                       help='Truncate target tables before migration (REHEARSAL ONLY)')
    parser.add_argument('--sqlite-readonly', action='store_true',
                       help='Open SQLite source in read-only mode (prevents journal writes)')
    
    args = parser.parse_args()
    
    if not args.pg_dsn:
        print(json.dumps({
            'status': 'error',
            'message': 'PostgreSQL DSN required (--pg-dsn or REHEARSAL_PG_DSN env)'
        }))
        return 1
    
    # Initialize logger
    logger = MigrationLogger(args.log_path)
    
    # Create engines
    if args.sqlite_readonly:
        # Use URI mode to force read-only access to the SQLite file
        # file:/absolute/path?mode=ro&uri=true
        sqlite_url = f"sqlite+pysqlite:///file:{args.sqlite_path}?mode=ro&uri=true"
        source_engine = create_engine(sqlite_url, poolclass=NullPool)
    else:
        source_engine = create_engine(f"sqlite:///{args.sqlite_path}", poolclass=NullPool)
    target_engine = create_engine(args.pg_dsn, poolclass=NullPool)
    
    # Create sessions
    SourceSession = sessionmaker(bind=source_engine)
    TargetSession = sessionmaker(bind=target_engine)
    
    source_session = SourceSession()
    target_session = TargetSession()
    
    # Track results
    results = []
    success = True
    
    try:
        # Start transaction for target (all-or-nothing)
        if not args.dry_run:
            target_session.begin()
        
        logger.log({
            'type': 'migration_start',
            'source': args.sqlite_path,
            'target': args.pg_dsn,
            'dry_run': args.dry_run,
            'batch_size': args.batch_size
        })
        
        # Get tables to migrate
        table_order = get_table_order()
        
        if args.tables:
            # Filter to requested tables
            requested = set(args.tables.split(','))
            table_order = [(n, m) for n, m in table_order if n in requested]
        
        # Truncate target tables if requested (in reverse order for FKs)
        if args.truncate_target and not args.dry_run:
            print("Truncating target tables...")
            for table_name, _ in reversed(table_order):
                try:
                    target_session.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
                    logger.log({'type': 'truncate', 'table': table_name})
                except Exception as e:
                    logger.log({'type': 'truncate_skip', 'table': table_name, 'reason': str(e)})
        
        # Migrate each table
        for table_name, model_class in table_order:
            print(f"Migrating {table_name}...")
            
            try:
                result = migrate_table(
                    source_session,
                    target_session,
                    table_name,
                    model_class,
                    batch_size=args.batch_size,
                    dry_run=args.dry_run,
                    logger=logger
                )
                results.append(result)
                
                # Print progress
                if args.dry_run:
                    print(f"  ✓ {table_name}: {result['source_count']} rows validated")
                else:
                    print(f"  ✓ {table_name}: {result['target_count']}/{result['source_count']} rows migrated")
                
            except Exception as e:
                success = False
                print(f"  ✗ {table_name}: {str(e)}")
                
                if args.stop_on_error:
                    logger.log({
                        'type': 'migration_abort',
                        'table': table_name,
                        'error': str(e)
                    })
                    break
        
        # Commit or rollback
        if not args.dry_run:
            if success:
                target_session.commit()
                logger.log({'type': 'transaction_commit'})
                print("\n✓ Migration committed successfully")
            else:
                target_session.rollback()
                logger.log({'type': 'transaction_rollback'})
                print("\n✗ Migration rolled back due to errors")
        
        # Print summary
        print("\n=== Migration Summary ===")
        total_source = sum(r['source_count'] for r in results)
        total_target = sum(r.get('target_count', 0) for r in results)
        
        print(f"Tables processed: {len(results)}")
        print(f"Total source rows: {total_source}")
        if not args.dry_run:
            print(f"Total migrated rows: {total_target}")
        print(f"Success: {success}")
        
        if args.log_path:
            print(f"Log written to: {args.log_path}")
        
        logger.log({
            'type': 'migration_complete',
            'success': success,
            'tables_processed': len(results),
            'total_source_rows': total_source,
            'total_migrated_rows': total_target if not args.dry_run else 0
        })
        
        return 0 if success else 1
        
    except Exception as e:
        logger.log({
            'type': 'migration_error',
            'error': str(e)
        })
        print(f"\nFATAL ERROR: {str(e)}")
        if not args.dry_run:
            target_session.rollback()
        return 1
        
    finally:
        source_session.close()
        target_session.close()


if __name__ == "__main__":
    sys.exit(main())