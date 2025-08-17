#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/query_performance_analyzer.py
🎯 PURPOSE: Database query performance analysis and optimization
🔗 IMPORTS: SQLAlchemy, time, logging, json
📤 EXPORTS: QueryPerformanceAnalyzer class
"""

import time
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryPerformanceAnalyzer:
    """Analyze and optimize database query performance"""
    
    def __init__(self, database_url: str = None):
        """Initialize analyzer with database connection"""
        if not database_url:
            database_url = os.getenv('DATABASE_URL', 'sqlite:///data/cora.db')
        
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.slow_queries = []
        self.query_stats = {}
        self.index_recommendations = []
        
        # Set up query event listeners
        self._setup_query_listeners()
    
    def _setup_query_listeners(self):
        """Set up SQLAlchemy event listeners for query monitoring"""
        @event.listens_for(self.engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()
        
        @event.listens_for(self.engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            query_time = time.time() - context._query_start_time
            
            # Log slow queries (> 100ms)
            if query_time > 0.1:
                self.slow_queries.append({
                    'sql': statement,
                    'parameters': str(parameters)[:200],
                    'execution_time': query_time,
                    'timestamp': datetime.now(),
                    'connection_id': id(conn)
                })
                logger.warning(f"Slow query detected: {query_time:.3f}s - {statement[:100]}...")
            
            # Track query statistics
            query_hash = hash(statement)
            if query_hash not in self.query_stats:
                self.query_stats[query_hash] = {
                    'sql': statement,
                    'count': 0,
                    'total_time': 0,
                    'avg_time': 0,
                    'min_time': float('inf'),
                    'max_time': 0
                }
            
            stats = self.query_stats[query_hash]
            stats['count'] += 1
            stats['total_time'] += query_time
            stats['avg_time'] = stats['total_time'] / stats['count']
            stats['min_time'] = min(stats['min_time'], query_time)
            stats['max_time'] = max(stats['max_time'], query_time)
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    def analyze_table_indexes(self) -> Dict[str, List[str]]:
        """Analyze existing indexes and identify missing ones"""
        indexes = {}
        
        try:
            with self.get_session() as session:
                # Get database type
                result = session.execute(text("SELECT sqlite_version()"))
                db_type = "sqlite" if result else "postgresql"
                
                if db_type == "sqlite":
                    # SQLite index analysis
                    result = session.execute(text("""
                        SELECT name, sql FROM sqlite_master 
                        WHERE type='index' AND sql IS NOT NULL
                    """))
                    
                    for row in result:
                        table_name = row[0].split('_')[0] if '_' in row[0] else 'unknown'
                        if table_name not in indexes:
                            indexes[table_name] = []
                        indexes[table_name].append(row[0])
                
                else:
                    # PostgreSQL index analysis
                    result = session.execute(text("""
                        SELECT 
                            schemaname,
                            tablename,
                            indexname,
                            indexdef
                        FROM pg_indexes 
                        WHERE schemaname = 'public'
                        ORDER BY tablename, indexname
                    """))
                    
                    for row in result:
                        table_name = row[1]
                        if table_name not in indexes:
                            indexes[table_name] = []
                        indexes[table_name].append(row[2])
        
        except SQLAlchemyError as e:
            logger.error(f"Error analyzing indexes: {e}")
        
        return indexes
    
    def generate_index_recommendations(self) -> List[Dict[str, Any]]:
        """Generate index recommendations based on query patterns"""
        recommendations = []
        
        # Common query patterns and recommended indexes
        patterns = [
            {
                'table': 'expenses',
                'description': 'User expenses by date range',
                'columns': ['user_id', 'expense_date'],
                'type': 'composite',
                'priority': 'high',
                'reason': 'Most common query pattern for user dashboards'
            },
            {
                'table': 'expenses',
                'description': 'Category filtering',
                'columns': ['user_id', 'category_id'],
                'type': 'composite',
                'priority': 'medium',
                'reason': 'Frequently used for expense categorization'
            },
            {
                'table': 'expenses',
                'description': 'Vendor searches',
                'columns': ['vendor'],
                'type': 'single',
                'priority': 'medium',
                'reason': 'Used for vendor-based expense filtering'
            },
            {
                'table': 'users',
                'description': 'Active user queries',
                'columns': ['is_active'],
                'type': 'single',
                'priority': 'medium',
                'reason': 'Used for user management and analytics'
            },
            {
                'table': 'users',
                'description': 'User creation date analytics',
                'columns': ['created_at'],
                'type': 'single',
                'priority': 'low',
                'reason': 'Used for user growth analytics'
            }
        ]
        
        existing_indexes = self.analyze_table_indexes()
        
        for pattern in patterns:
            table = pattern['table']
            columns = pattern['columns']
            
            # Check if index already exists
            index_name = f"idx_{table}_{'_'.join(columns)}"
            exists = False
            
            if table in existing_indexes:
                for existing in existing_indexes[table]:
                    if all(col in existing.lower() for col in columns):
                        exists = True
                        break
            
            if not exists:
                recommendations.append({
                    'table': table,
                    'index_name': index_name,
                    'columns': columns,
                    'type': pattern['type'],
                    'priority': pattern['priority'],
                    'description': pattern['description'],
                    'reason': pattern['reason'],
                    'sql': self._generate_index_sql(table, columns, index_name)
                })
        
        return recommendations
    
    def _generate_index_sql(self, table: str, columns: List[str], index_name: str) -> str:
        """Generate CREATE INDEX SQL statement"""
        columns_str = ', '.join(columns)
        return f"CREATE INDEX {index_name} ON {table} ({columns_str});"
    
    def analyze_query_performance(self, duration_minutes: int = 5) -> Dict[str, Any]:
        """Analyze query performance over a time period"""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        logger.info(f"Starting query performance analysis for {duration_minutes} minutes...")
        
        # Clear previous stats
        self.slow_queries.clear()
        self.query_stats.clear()
        
        # Wait for analysis period
        while datetime.now() < end_time:
            time.sleep(1)
        
        # Compile results
        results = {
            'analysis_period': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'duration_minutes': duration_minutes
            },
            'slow_queries': self.slow_queries,
            'query_statistics': self.query_stats,
            'index_recommendations': self.generate_index_recommendations(),
            'summary': self._generate_summary()
        }
        
        return results
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate performance summary"""
        total_queries = sum(stats['count'] for stats in self.query_stats.values())
        slow_query_count = len(self.slow_queries)
        
        if total_queries > 0:
            avg_query_time = sum(stats['total_time'] for stats in self.query_stats.values()) / total_queries
        else:
            avg_query_time = 0
        
        return {
            'total_queries': total_queries,
            'slow_queries': slow_query_count,
            'average_query_time': avg_query_time,
            'slowest_query_time': max([stats['max_time'] for stats in self.query_stats.values()], default=0),
            'fastest_query_time': min([stats['min_time'] for stats in self.query_stats.values()], default=0)
        }
    
    def generate_report(self, results: Dict[str, Any], output_file: str = None) -> str:
        """Generate a human-readable performance report"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"query_performance_report_{timestamp}.json"
        
        # Save detailed results
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Generate human-readable report
        report = []
        report.append("=" * 80)
        report.append("📊 DATABASE QUERY PERFORMANCE ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Analysis Period: {results['analysis_period']['start']} to {results['analysis_period']['end']}")
        report.append(f"Duration: {results['analysis_period']['duration_minutes']} minutes")
        report.append("")
        
        # Summary
        summary = results['summary']
        report.append("📈 PERFORMANCE SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Queries: {summary['total_queries']}")
        report.append(f"Slow Queries (>100ms): {summary['slow_queries']}")
        report.append(f"Average Query Time: {summary['average_query_time']:.3f}s")
        report.append(f"Slowest Query: {summary['slowest_query_time']:.3f}s")
        report.append(f"Fastest Query: {summary['fastest_query_time']:.3f}s")
        report.append("")
        
        # Slow queries
        if results['slow_queries']:
            report.append("🐌 SLOW QUERIES DETECTED")
            report.append("-" * 40)
            for i, query in enumerate(results['slow_queries'][:10], 1):  # Top 10
                report.append(f"{i}. {query['execution_time']:.3f}s - {query['sql'][:80]}...")
            report.append("")
        
        # Index recommendations
        recommendations = results['index_recommendations']
        if recommendations:
            report.append("🔧 INDEX RECOMMENDATIONS")
            report.append("-" * 40)
            for rec in recommendations:
                report.append(f"Priority: {rec['priority'].upper()}")
                report.append(f"Table: {rec['table']}")
                report.append(f"Columns: {', '.join(rec['columns'])}")
                report.append(f"SQL: {rec['sql']}")
                report.append(f"Reason: {rec['reason']}")
                report.append("")
        
        # Top queries by frequency
        if results['query_statistics']:
            report.append("📊 TOP QUERIES BY FREQUENCY")
            report.append("-" * 40)
            sorted_queries = sorted(
                results['query_statistics'].values(),
                key=lambda x: x['count'],
                reverse=True
            )
            
            for i, query in enumerate(sorted_queries[:5], 1):
                report.append(f"{i}. Count: {query['count']}, Avg: {query['avg_time']:.3f}s")
                report.append(f"   SQL: {query['sql'][:100]}...")
                report.append("")
        
        report.append("=" * 80)
        report.append(f"Detailed results saved to: {output_file}")
        report.append("=" * 80)
        
        report_text = "\n".join(report)
        
        # Save human-readable report
        report_file = output_file.replace('.json', '_readable.txt')
        with open(report_file, 'w') as f:
            f.write(report_text)
        
        return report_text
    
    def create_indexes(self, recommendations: List[Dict[str, Any]]) -> List[str]:
        """Create recommended indexes"""
        created_indexes = []
        
        with self.get_session() as session:
            for rec in recommendations:
                try:
                    session.execute(text(rec['sql']))
                    session.commit()
                    created_indexes.append(rec['index_name'])
                    logger.info(f"Created index: {rec['index_name']}")
                except SQLAlchemyError as e:
                    logger.error(f"Failed to create index {rec['index_name']}: {e}")
                    session.rollback()
        
        return created_indexes

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze database query performance")
    parser.add_argument("--duration", type=int, default=5, help="Analysis duration in minutes")
    parser.add_argument("--create-indexes", action="store_true", help="Create recommended indexes")
    parser.add_argument("--output", help="Output file for results")
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = QueryPerformanceAnalyzer()
    
    # Run analysis
    results = analyzer.analyze_query_performance(args.duration)
    
    # Generate report
    report = analyzer.generate_report(results, args.output)
    print(report)
    
    # Create indexes if requested
    if args.create_indexes:
        recommendations = results['index_recommendations']
        if recommendations:
            print(f"\nCreating {len(recommendations)} recommended indexes...")
            created = analyzer.create_indexes(recommendations)
            print(f"Successfully created {len(created)} indexes: {', '.join(created)}")
        else:
            print("No index recommendations to create.")

if __name__ == "__main__":
    main() 