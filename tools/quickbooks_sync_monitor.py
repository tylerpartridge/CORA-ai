#!/usr/bin/env python3
"""
QuickBooks Sync Monitoring Dashboard
Monitors sync operations, errors, and performance metrics
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from tabulate import tabulate
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.quickbooks_integration import QuickBooksIntegration, QuickBooksSyncHistory
from models.expense import Expense

class QuickBooksSyncMonitor:
    """Monitor QuickBooks sync operations and health"""
    
    def __init__(self, database_url=None):
        if not database_url:
            database_url = os.getenv("DATABASE_URL", "sqlite:///cora.db")
        
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_integration_summary(self):
        """Get summary of all QuickBooks integrations"""
        session = self.Session()
        try:
            integrations = session.query(QuickBooksIntegration).filter(
                QuickBooksIntegration.is_active == True
            ).all()
            
            summary = []
            for integration in integrations:
                # Check token status
                token_status = "Valid"
                if integration.needs_token_refresh:
                    token_status = "Needs Refresh"
                elif integration.token_expires_at < datetime.utcnow():
                    token_status = "Expired"
                
                summary.append({
                    "User ID": integration.user_id,
                    "Company": integration.company_name[:30],
                    "Total Synced": integration.total_expenses_synced,
                    "Last Sync": integration.last_sync_at.strftime("%Y-%m-%d %H:%M") if integration.last_sync_at else "Never",
                    "Token Status": token_status,
                    "Auto Sync": "Yes" if integration.auto_sync else "No",
                    "Last Error": integration.last_sync_error[:30] if integration.last_sync_error else "None"
                })
            
            return summary
        finally:
            session.close()
    
    def get_sync_statistics(self, hours=24):
        """Get sync statistics for the last N hours"""
        session = self.Session()
        try:
            since = datetime.utcnow() - timedelta(hours=hours)
            
            # Total syncs
            total_syncs = session.query(func.count(QuickBooksSyncHistory.id)).filter(
                QuickBooksSyncHistory.created_at >= since
            ).scalar()
            
            # Successful syncs
            successful_syncs = session.query(func.count(QuickBooksSyncHistory.id)).filter(
                QuickBooksSyncHistory.created_at >= since,
                QuickBooksSyncHistory.quickbooks_status == "success"
            ).scalar()
            
            # Failed syncs
            failed_syncs = session.query(func.count(QuickBooksSyncHistory.id)).filter(
                QuickBooksSyncHistory.created_at >= since,
                QuickBooksSyncHistory.quickbooks_status == "error"
            ).scalar()
            
            # Average sync duration
            avg_duration = session.query(func.avg(QuickBooksSyncHistory.sync_duration)).filter(
                QuickBooksSyncHistory.created_at >= since,
                QuickBooksSyncHistory.quickbooks_status == "success"
            ).scalar() or 0
            
            # Most common errors
            errors = session.query(
                QuickBooksSyncHistory.error_message,
                func.count(QuickBooksSyncHistory.id).label('count')
            ).filter(
                QuickBooksSyncHistory.created_at >= since,
                QuickBooksSyncHistory.quickbooks_status == "error",
                QuickBooksSyncHistory.error_message.isnot(None)
            ).group_by(
                QuickBooksSyncHistory.error_message
            ).order_by(
                func.count(QuickBooksSyncHistory.id).desc()
            ).limit(5).all()
            
            return {
                "period_hours": hours,
                "total_syncs": total_syncs,
                "successful_syncs": successful_syncs,
                "failed_syncs": failed_syncs,
                "success_rate": f"{(successful_syncs / total_syncs * 100):.1f}%" if total_syncs > 0 else "N/A",
                "avg_duration_ms": int(avg_duration),
                "top_errors": [{"error": e[0][:50], "count": e[1]} for e in errors]
            }
        finally:
            session.close()
    
    def get_recent_sync_history(self, limit=20):
        """Get recent sync history"""
        session = self.Session()
        try:
            history = session.query(QuickBooksSyncHistory).order_by(
                QuickBooksSyncHistory.created_at.desc()
            ).limit(limit).all()
            
            results = []
            for h in history:
                results.append({
                    "Time": h.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "Type": h.sync_type,
                    "Expense ID": h.expense_id,
                    "QB ID": h.quickbooks_id[:15] if h.quickbooks_id else "N/A",
                    "Status": h.quickbooks_status,
                    "Duration": f"{h.sync_duration}ms",
                    "Error": h.error_message[:30] if h.error_message else ""
                })
            
            return results
        finally:
            session.close()
    
    def get_unsynced_expenses(self):
        """Get count of expenses that haven't been synced"""
        session = self.Session()
        try:
            # Get all expenses
            total_expenses = session.query(func.count(Expense.id)).scalar()
            
            # Get synced expense IDs
            synced_expense_ids = session.query(
                QuickBooksSyncHistory.expense_id
            ).filter(
                QuickBooksSyncHistory.quickbooks_status == "success"
            ).distinct().subquery()
            
            # Count unsynced
            unsynced_count = session.query(func.count(Expense.id)).filter(
                ~Expense.id.in_(synced_expense_ids)
            ).scalar()
            
            return {
                "total_expenses": total_expenses,
                "unsynced_expenses": unsynced_count,
                "synced_expenses": total_expenses - unsynced_count,
                "sync_percentage": f"{((total_expenses - unsynced_count) / total_expenses * 100):.1f}%" if total_expenses > 0 else "N/A"
            }
        finally:
            session.close()
    
    def display_dashboard(self):
        """Display complete monitoring dashboard"""
        print("\n" + "=" * 80)
        print("QUICKBOOKS SYNC MONITORING DASHBOARD")
        print("=" * 80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Integration Summary
        print("\n[ACTIVE INTEGRATIONS]")
        integrations = self.get_integration_summary()
        if integrations:
            print(tabulate(integrations, headers="keys", tablefmt="grid"))
        else:
            print("No active QuickBooks integrations found.")
        
        # Sync Statistics
        print("\n[SYNC STATISTICS - LAST 24 HOURS]")
        stats = self.get_sync_statistics(24)
        print(f"Total Syncs: {stats['total_syncs']}")
        print(f"Successful: {stats['successful_syncs']} ({stats['success_rate']})")
        print(f"Failed: {stats['failed_syncs']}")
        print(f"Average Duration: {stats['avg_duration_ms']}ms")
        
        if stats['top_errors']:
            print("\nTop Errors:")
            for i, error in enumerate(stats['top_errors'], 1):
                print(f"  {i}. {error['error']} ({error['count']} occurrences)")
        
        # Unsynced Expenses
        print("\n[EXPENSE SYNC STATUS]")
        unsynced = self.get_unsynced_expenses()
        print(f"Total Expenses: {unsynced['total_expenses']}")
        print(f"Synced: {unsynced['synced_expenses']}")
        print(f"Unsynced: {unsynced['unsynced_expenses']}")
        print(f"Sync Coverage: {unsynced['sync_percentage']}")
        
        # Recent History
        print("\n[RECENT SYNC HISTORY]")
        history = self.get_recent_sync_history(10)
        if history:
            print(tabulate(history, headers="keys", tablefmt="grid"))
        else:
            print("No sync history found.")
        
        print("\n" + "=" * 80)
    
    def export_metrics(self, output_file="quickbooks_metrics.json"):
        """Export metrics to JSON file"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "integrations": self.get_integration_summary(),
            "statistics_24h": self.get_sync_statistics(24),
            "statistics_7d": self.get_sync_statistics(168),
            "unsynced_expenses": self.get_unsynced_expenses(),
            "recent_history": self.get_recent_sync_history(50)
        }
        
        with open(output_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        print(f"Metrics exported to {output_file}")
    
    def check_health(self):
        """Check overall health of QuickBooks integration"""
        issues = []
        
        # Check for expired tokens
        session = self.Session()
        try:
            expired_tokens = session.query(func.count(QuickBooksIntegration.id)).filter(
                QuickBooksIntegration.is_active == True,
                QuickBooksIntegration.token_expires_at < datetime.utcnow()
            ).scalar()
            
            if expired_tokens > 0:
                issues.append(f"WARNING: {expired_tokens} integration(s) have expired tokens")
            
            # Check sync failure rate
            stats = self.get_sync_statistics(24)
            if stats['total_syncs'] > 0:
                failure_rate = (stats['failed_syncs'] / stats['total_syncs']) * 100
                if failure_rate > 10:
                    issues.append(f"WARNING: High failure rate ({failure_rate:.1f}%) in last 24 hours")
            
            # Check for stale integrations
            stale_date = datetime.utcnow() - timedelta(days=7)
            stale_integrations = session.query(func.count(QuickBooksIntegration.id)).filter(
                QuickBooksIntegration.is_active == True,
                QuickBooksIntegration.last_sync_at < stale_date
            ).scalar()
            
            if stale_integrations > 0:
                issues.append(f"INFO: {stale_integrations} integration(s) haven't synced in 7+ days")
            
            # Check unsynced expenses
            unsynced = self.get_unsynced_expenses()
            if unsynced['total_expenses'] > 0:
                unsynced_rate = (unsynced['unsynced_expenses'] / unsynced['total_expenses']) * 100
                if unsynced_rate > 20:
                    issues.append(f"WARNING: {unsynced_rate:.1f}% of expenses are unsynced")
            
            if issues:
                print("\n[HEALTH CHECK ISSUES]")
                for issue in issues:
                    print(f"- {issue}")
            else:
                print("\n[HEALTH CHECK] All systems operational")
            
            return len([i for i in issues if i.startswith("WARNING")]) == 0
        finally:
            session.close()


def main():
    """Run the monitoring dashboard"""
    import argparse
    
    parser = argparse.ArgumentParser(description="QuickBooks Sync Monitoring")
    parser.add_argument("--export", action="store_true", help="Export metrics to JSON")
    parser.add_argument("--health", action="store_true", help="Run health check only")
    parser.add_argument("--continuous", action="store_true", help="Run continuously (refresh every 60s)")
    
    args = parser.parse_args()
    
    monitor = QuickBooksSyncMonitor()
    
    if args.health:
        monitor.check_health()
    elif args.export:
        monitor.export_metrics()
    elif args.continuous:
        import time
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            monitor.display_dashboard()
            monitor.check_health()
            print("\nRefreshing in 60 seconds... (Ctrl+C to exit)")
            time.sleep(60)
    else:
        monitor.display_dashboard()
        monitor.check_health()


if __name__ == "__main__":
    main()