#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/test_postgresql_connection.py
🎯 PURPOSE: Test PostgreSQL connection and basic functionality
🔗 IMPORTS: SQLAlchemy, psycopg2
📤 EXPORTS: PostgreSQL connection test results
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config

def test_postgresql_connection():
    """Test PostgreSQL connection and basic functionality"""
    
    print("🔍 Testing PostgreSQL Connection...")
    
    # Check if DATABASE_URL is set
    db_url = config.DATABASE_URL
    if not db_url:
        print("❌ DATABASE_URL not set")
        return False
    
    if not db_url.startswith('postgresql://'):
        print(f"❌ DATABASE_URL is not PostgreSQL: {db_url}")
        return False
    
    try:
        # Create engine
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as conn:
            # Test basic query
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL connection successful")
            print(f"   Version: {version}")
            
            # Test database name
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"   Database: {db_name}")
            
            # Test user
            result = conn.execute(text("SELECT current_user"))
            user = result.fetchone()[0]
            print(f"   User: {user}")
            
            # Test if tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print(f"   Tables found: {', '.join(tables)}")
            else:
                print("   ⚠️  No tables found (schema may not be created yet)")
            
            return True
            
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_postgresql_performance():
    """Test PostgreSQL performance with basic queries"""
    
    print("\n⚡ Testing PostgreSQL Performance...")
    
    try:
        engine = create_engine(config.DATABASE_URL)
        
        with engine.connect() as conn:
            # Test simple query performance
            import time
            
            start_time = time.time()
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.fetchone()[0]
            query_time = time.time() - start_time
            
            print(f"   Users count: {user_count} (took {query_time:.3f}s)")
            
            # Test expense query
            start_time = time.time()
            result = conn.execute(text("SELECT COUNT(*) FROM expenses"))
            expense_count = result.fetchone()[0]
            query_time = time.time() - start_time
            
            print(f"   Expenses count: {expense_count} (took {query_time:.3f}s)")
            
            # Test complex query
            start_time = time.time()
            result = conn.execute(text("""
                SELECT u.email, COUNT(e.id) as expense_count, SUM(e.amount_cents)/100.0 as total_amount
                FROM users u
                LEFT JOIN expenses e ON u.id = e.user_id
                GROUP BY u.id, u.email
                ORDER BY total_amount DESC
                LIMIT 5
            """))
            users_with_expenses = result.fetchall()
            query_time = time.time() - start_time
            
            print(f"   Complex query: {len(users_with_expenses)} results (took {query_time:.3f}s)")
            
            return True
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def test_postgresql_features():
    """Test PostgreSQL-specific features"""
    
    print("\n🔧 Testing PostgreSQL Features...")
    
    try:
        engine = create_engine(config.DATABASE_URL)
        
        with engine.connect() as conn:
            # Test UUID extension
            result = conn.execute(text("SELECT gen_random_uuid()"))
            uuid_value = result.fetchone()[0]
            print(f"   UUID generation: {uuid_value[:8]}...")
            
            # Test JSONB support
            result = conn.execute(text("SELECT '{\"test\": \"value\"}'::jsonb"))
            jsonb_value = result.fetchone()[0]
            print(f"   JSONB support: {jsonb_value}")
            
            # Test full-text search
            result = conn.execute(text("SELECT to_tsvector('english', 'PostgreSQL full text search')"))
            tsvector = result.fetchone()[0]
            print(f"   Full-text search: {tsvector}")
            
            return True
            
    except Exception as e:
        print(f"❌ Feature test failed: {e}")
        return False

def main():
    """Run all PostgreSQL tests"""
    
    print("🚀 PostgreSQL Connection and Feature Tests")
    print("=" * 50)
    
    # Test 1: Basic connection
    if not test_postgresql_connection():
        print("\n❌ Basic connection test failed")
        return False
    
    # Test 2: Performance
    if not test_postgresql_performance():
        print("\n❌ Performance test failed")
        return False
    
    # Test 3: Features
    if not test_postgresql_features():
        print("\n❌ Feature test failed")
        return False
    
    print("\n✅ All PostgreSQL tests passed!")
    print("\n📋 PostgreSQL is ready for production use")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 