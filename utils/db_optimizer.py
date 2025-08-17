#!/usr/bin/env python3
"""
Database Optimization Utilities for CORA
Simple database performance improvements without complex dependencies
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Simple database optimization utilities"""
    
    def __init__(self, db_path: str = "cora.db"):
        self.db_path = Path(db_path)
        
    def analyze_database(self) -> Dict[str, Any]:
        """Analyze database performance and structure"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get basic stats
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            stats = {
                "database_size_mb": self.db_path.stat().st_size / (1024*1024),
                "total_tables": len(tables),
                "tables": []
            }
            
            # Analyze each table
            for table in tables:
                if table == 'sqlite_sequence':
                    continue
                    
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    row_count = cursor.fetchone()[0]
                    
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    
                    stats["tables"].append({
                        "name": table,
                        "row_count": row_count,
                        "column_count": len(columns)
                    })
                except Exception as e:
                    logger.warning(f"Could not analyze table {table}: {e}")
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Database analysis failed: {e}")
            return {"error": str(e)}
    
    def optimize_database(self) -> Dict[str, Any]:
        """Perform basic database optimizations"""
        results = {
            "operations": [],
            "success": True,
            "errors": []
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 1. Run VACUUM to reclaim space
            try:
                cursor.execute("VACUUM")
                results["operations"].append("VACUUM completed - reclaimed unused space")
            except Exception as e:
                results["errors"].append(f"VACUUM failed: {e}")
            
            # 2. Run ANALYZE to update statistics
            try:
                cursor.execute("ANALYZE")
                results["operations"].append("ANALYZE completed - updated query statistics")
            except Exception as e:
                results["errors"].append(f"ANALYZE failed: {e}")
            
            # 3. Check and add basic indexes if missing
            basic_indexes = [
                ("idx_users_email", "users", "email"),
                ("idx_users_created_at", "users", "created_at"),
                ("idx_business_profiles_email", "business_profiles", "user_email"),
            ]
            
            for index_name, table_name, column_name in basic_indexes:
                try:
                    # Check if table exists
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                    if cursor.fetchone():
                        # Check if index exists
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name=?", (index_name,))
                        if not cursor.fetchone():
                            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})")
                            results["operations"].append(f"Created index: {index_name}")
                except Exception as e:
                    results["errors"].append(f"Index creation failed for {index_name}: {e}")
            
            conn.commit()
            conn.close()
            
            if results["errors"]:
                results["success"] = False
            
            return results
            
        except Exception as e:
            logger.error(f"Database optimization failed: {e}")
            return {
                "success": False,
                "operations": [],
                "errors": [str(e)]
            }
    
    def get_slow_queries_suggestions(self) -> List[str]:
        """Get suggestions for optimizing slow queries"""
        suggestions = [
            "Add indexes on frequently queried columns (email, created_at, user_id)",
            "Use LIMIT when querying large result sets",
            "Consider using compound indexes for multi-column WHERE clauses",
            "Use prepared statements to reduce parsing overhead",
            "Avoid SELECT * - specify only needed columns",
            "Use EXPLAIN QUERY PLAN to analyze query performance"
        ]
        return suggestions

def optimize_cora_database() -> Dict[str, Any]:
    """Optimize the CORA database - standalone function"""
    optimizer = DatabaseOptimizer()
    
    # First analyze
    analysis = optimizer.analyze_database()
    
    # Then optimize
    optimization = optimizer.optimize_database()
    
    return {
        "analysis": analysis,
        "optimization": optimization,
        "suggestions": optimizer.get_slow_queries_suggestions()
    }

if __name__ == "__main__":
    # Run optimization when script is called directly
    result = optimize_cora_database()
    
    print("CORA Database Optimization Results:")
    print("==================================")
    
    if "error" not in result["analysis"]:
        analysis = result["analysis"]
        print(f"Database size: {analysis['database_size_mb']:.2f} MB")
        print(f"Total tables: {analysis['total_tables']}")
        print(f"Total rows: {sum(t['row_count'] for t in analysis['tables'])}")
    
    optimization = result["optimization"]
    if optimization["success"]:
        print(f"\\nOptimization completed successfully!")
        for op in optimization["operations"]:
            print(f"  - {op}")
    else:
        print("\\nOptimization had errors:")
        for error in optimization["errors"]:
            print(f"  - {error}")
    
    print("\\nOptimization suggestions:")
    for suggestion in result["suggestions"]:
        print(f"  - {suggestion}")