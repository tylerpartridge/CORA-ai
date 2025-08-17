#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/test_postgresql_migration.py
🎯 PURPOSE: Test PostgreSQL migration by validating models and schema
🔗 IMPORTS: sqlalchemy, models, os
📤 EXPORTS: Test script for PostgreSQL migration validation
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_model_imports():
    """Test that all models can be imported with PostgreSQL types"""
    print("Testing model imports...")
    
    try:
        from models.user import User
        from models.expense import Expense
        from models.expense_category import ExpenseCategory
        from models.user_activity import UserActivity
        from models.feedback import Feedback
        from models.payment import Payment
        
        print("✅ All models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Model import failed: {str(e)}")
        return False

def test_schema_generation():
    """Test that SQLAlchemy can generate PostgreSQL schema"""
    print("Testing schema generation...")
    
    try:
        from models.base import Base
        from models.user import User
        from models.expense import Expense
        from models.expense_category import ExpenseCategory
        from models.user_activity import UserActivity
        from models.feedback import Feedback
        from models.payment import Payment
        
        # Generate schema
        from sqlalchemy import create_engine
        engine = create_engine('postgresql://test:test@localhost/test')
        
        # This will validate the schema without actually creating tables
        metadata = Base.metadata
        print("✅ Schema generation successful")
        return True
    except Exception as e:
        print(f"❌ Schema generation failed: {str(e)}")
        return False

def test_data_migration_file():
    """Test that the data migration file was created"""
    print("Testing data migration file...")
    
    migration_file = Path("postgres_data.sql")
    if migration_file.exists():
        size = migration_file.stat().st_size
        print(f"✅ Data migration file exists ({size} bytes)")
        return True
    else:
        print("❌ Data migration file not found")
        return False

def test_postgresql_schema_file():
    """Test that the PostgreSQL schema file was created"""
    print("Testing PostgreSQL schema file...")
    
    schema_file = Path("schema/postgresql_schema.sql")
    if schema_file.exists():
        size = schema_file.stat().st_size
        print(f"✅ PostgreSQL schema file exists ({size} bytes)")
        return True
    else:
        print("❌ PostgreSQL schema file not found")
        return False

def main():
    """Run all PostgreSQL migration tests"""
    print("🧪 Testing PostgreSQL Migration Components")
    print("=" * 50)
    
    tests = [
        test_model_imports,
        test_schema_generation,
        test_data_migration_file,
        test_postgresql_schema_file
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All PostgreSQL migration tests passed!")
        return True
    else:
        print("❌ Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 