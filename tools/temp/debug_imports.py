#!/usr/bin/env python3
"""
Debug script to identify import issues
"""

import sys
import traceback

def test_import(module_name, description):
    """Test importing a specific module"""
    print(f"Testing import: {description}")
    try:
        __import__(module_name)
        print(f"✅ {description} - SUCCESS")
        return True
    except Exception as e:
        print(f"❌ {description} - FAILED: {str(e)}")
        traceback.print_exc()
        return False

def main():
    print("🔍 Starting import debugging...")
    print("=" * 50)
    
    # Test basic Python
    print("Testing basic Python...")
    print("✅ Basic Python - SUCCESS")
    
    # Test core modules
    modules_to_test = [
        ("fastapi", "FastAPI"),
        ("sqlalchemy", "SQLAlchemy"),
        ("redis", "Redis"),
        ("pydantic", "Pydantic"),
        ("models.base", "Database Models"),
        ("utils.redis_manager", "Redis Manager"),
        ("utils.validation", "Validation System"),
        ("utils.api_response", "API Response"),
        ("utils.api_response_optimizer", "API Response Optimizer"),
        ("middleware.response_optimization", "Response Optimization Middleware"),
    ]
    
    failed_imports = []
    
    for module_name, description in modules_to_test:
        if not test_import(module_name, description):
            failed_imports.append(module_name)
        print("-" * 30)
    
    print("=" * 50)
    print(f"📊 Results: {len(modules_to_test) - len(failed_imports)}/{len(modules_to_test)} imports successful")
    
    if failed_imports:
        print(f"❌ Failed imports: {failed_imports}")
        return 1
    else:
        print("🎉 All imports successful!")
        return 0

if __name__ == "__main__":
    exit(main()) 