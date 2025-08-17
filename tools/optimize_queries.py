#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/optimize_queries.py
🎯 PURPOSE: Database query optimization utilities
🔗 IMPORTS: SQLAlchemy, logging
📤 EXPORTS: Query optimization functions
"""

from sqlalchemy.orm import Session, joinedload, selectinload, subqueryload
from sqlalchemy import text, func, and_, or_
from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def optimize_dashboard_queries(db: Session, user_id: str) -> Dict[str, Any]:
        """
        Optimized dashboard data fetching with eager loading
        Replaces multiple queries with efficient joins
        """
        from models.plaid_integration import PlaidIntegration, PlaidAccount, PlaidTransaction
        
        # Single query with eager loading instead of multiple queries
        integration = db.query(PlaidIntegration).options(
            joinedload(PlaidIntegration.accounts).options(
                selectinload(PlaidAccount.transactions)
            )
        ).filter(
            PlaidIntegration.user_id == user_id,
            PlaidIntegration.is_active == True
        ).first()
        
        if not integration:
            return {
                "connected": False,
                "accounts": [],
                "transactions": [],
                "summary": {}
            }
        
        # Process data in memory instead of multiple DB queries
        thirty_days_ago = datetime.now() - timedelta(days=30)
        all_transactions = []
        total_balance = 0
        
        for account in integration.accounts:
            total_balance += account.current_balance or 0
            # Filter transactions in memory
            recent_txns = [
                t for t in account.transactions 
                if t.date >= thirty_days_ago
            ]
            all_transactions.extend(recent_txns)
        
        # Sort in memory instead of DB query
        all_transactions.sort(key=lambda x: x.date, reverse=True)
        
        return {
            "connected": True,
            "integration": integration,
            "accounts": integration.accounts,
            "transactions": all_transactions[:100],  # Limit to 100 most recent
            "summary": {
                "total_balance": total_balance,
                "transaction_count": len(all_transactions)
            }
        }
    
    @staticmethod
    def optimize_expense_queries(db: Session, user_id: str) -> Dict[str, Any]:
        """
        Optimized expense fetching with single query
        """
        from models import Expense, ExpenseCategory
        
        # Use subquery for category counts
        category_counts = db.query(
            Expense.category_id,
            func.count(Expense.id).label('count'),
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.user_id == user_id
        ).group_by(Expense.category_id).subquery()
        
        # Single query with join
        results = db.query(
            ExpenseCategory,
            category_counts.c.count,
            category_counts.c.total
        ).outerjoin(
            category_counts,
            ExpenseCategory.id == category_counts.c.category_id
        ).all()
        
        return {
            "categories": [
                {
                    "name": cat.name,
                    "count": count or 0,
                    "total": float(total or 0)
                }
                for cat, count, total in results
            ]
        }
    
    @staticmethod
    def create_materialized_view(db: Session, view_name: str, query: str):
        """
        Create a materialized view for expensive queries
        """
        try:
            # Drop existing view if exists
            db.execute(text(f"DROP MATERIALIZED VIEW IF EXISTS {view_name}"))
            
            # Create new materialized view
            db.execute(text(f"""
                CREATE MATERIALIZED VIEW {view_name} AS
                {query}
            """))
            
            # Create index for better performance
            db.execute(text(f"""
                CREATE INDEX idx_{view_name}_user_id 
                ON {view_name}(user_id)
            """))
            
            db.commit()
            logger.info(f"Created materialized view: {view_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create materialized view {view_name}: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def refresh_materialized_view(db: Session, view_name: str):
        """
        Refresh a materialized view
        """
        try:
            db.execute(text(f"REFRESH MATERIALIZED VIEW {view_name}"))
            db.commit()
            logger.info(f"Refreshed materialized view: {view_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to refresh materialized view {view_name}: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def analyze_slow_queries(db: Session) -> List[Dict[str, Any]]:
        """
        Analyze slow queries from PostgreSQL stats
        """
        try:
            # Get slow queries from pg_stat_statements
            result = db.execute(text("""
                SELECT 
                    query,
                    calls,
                    total_exec_time,
                    mean_exec_time,
                    stddev_exec_time,
                    rows
                FROM pg_stat_statements
                WHERE mean_exec_time > 100  -- Queries taking more than 100ms
                ORDER BY mean_exec_time DESC
                LIMIT 20
            """))
            
            slow_queries = []
            for row in result:
                slow_queries.append({
                    "query": row.query[:200],  # Truncate long queries
                    "calls": row.calls,
                    "total_time": row.total_exec_time,
                    "avg_time": row.mean_exec_time,
                    "row_count": row.rows
                })
            
            return slow_queries
            
        except Exception as e:
            logger.error(f"Failed to analyze slow queries: {e}")
            return []
    
    @staticmethod
    def add_missing_indexes(db: Session):
        """
        Add commonly needed indexes
        """
        indexes = [
            # Expenses indexes
            "CREATE INDEX IF NOT EXISTS idx_expenses_user_date ON expenses(user_id, date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category_id)",
            "CREATE INDEX IF NOT EXISTS idx_expenses_job ON expenses(job_id)",
            
            # Plaid indexes
            "CREATE INDEX IF NOT EXISTS idx_plaid_transactions_date ON plaid_transactions(date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_plaid_transactions_account ON plaid_transactions(account_id)",
            
            # Users indexes
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_created ON users(created_at DESC)",
            
            # Jobs indexes
            "CREATE INDEX IF NOT EXISTS idx_jobs_user ON jobs(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)",
        ]
        
        for index_sql in indexes:
            try:
                db.execute(text(index_sql))
                logger.info(f"Created index: {index_sql[:50]}...")
            except Exception as e:
                logger.warning(f"Index creation failed (may already exist): {e}")
        
        db.commit()
        logger.info("Finished adding indexes")

# Singleton instance
optimizer = QueryOptimizer()

def optimize_all_queries(db: Session):
    """
    Run all query optimizations
    """
    logger.info("Starting query optimization...")
    
    # Add missing indexes
    optimizer.add_missing_indexes(db)
    
    # Create materialized views for expensive aggregations
    optimizer.create_materialized_view(
        db,
        "mv_user_expense_summary",
        """
        SELECT 
            user_id,
            DATE_TRUNC('month', date) as month,
            category_id,
            COUNT(*) as expense_count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount
        FROM expenses
        GROUP BY user_id, DATE_TRUNC('month', date), category_id
        """
    )
    
    optimizer.create_materialized_view(
        db,
        "mv_job_profitability",
        """
        SELECT 
            j.id as job_id,
            j.user_id,
            j.name as job_name,
            j.status,
            COUNT(e.id) as expense_count,
            COALESCE(SUM(e.amount), 0) as total_expenses,
            j.budget,
            (j.budget - COALESCE(SUM(e.amount), 0)) as profit
        FROM jobs j
        LEFT JOIN expenses e ON j.id = e.job_id
        GROUP BY j.id, j.user_id, j.name, j.status, j.budget
        """
    )
    
    logger.info("Query optimization complete")

if __name__ == "__main__":
    # Test optimization
    from models import get_db
    
    logging.basicConfig(level=logging.INFO)
    db = next(get_db())
    
    try:
        optimize_all_queries(db)
        
        # Analyze slow queries
        slow_queries = optimizer.analyze_slow_queries(db)
        if slow_queries:
            print("\nSlow Queries Found:")
            for q in slow_queries:
                print(f"- {q['query'][:50]}... (avg: {q['avg_time']:.2f}ms)")
        else:
            print("\nNo slow queries found")
            
    except Exception as e:
        print(f"Optimization failed: {e}")
    finally:
        db.close()