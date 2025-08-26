# Generated: 2025-07-11 by SmartHeaderGenerator v1.0
"""
🧭 LOCATION: CORA/.archive/2025/01/11/root_cleanup/demo_ai_integration.py
🎯 PURPOSE: [Auto-generated header - could not analyze file]
🔗 IMPORTS: [Unknown]
📤 EXPORTS: [Unknown]
🔄 PATTERN: [Unknown]
📝 TODOS: [Unknown]
💡 AI HINT: [Unknown]
⚠️ NEVER: [Unknown]
"""

🧭 LOCATION: /CORA/.archive\2025\01\11\root_cleanup\demo_ai_integration.py
🎯 PURPOSE: [To be determined - please update]
🔗 IMPORTS: [To be determined - please update]
📤 EXPORTS: [To be determined - please update]
🔄 PATTERN: [To be determined - please update]
📝 TODOS: [To be determined - please update]
"""

#!/usr/bin/env python3
"""
Demo script to show AI integration is working
"""

import sys
sys.path.append('.')

print("AI INTEGRATION DEMO")
print("=" * 50)

# Test 1: Memory System
print("\n1. Testing Memory System...")
try:
    from tools.claude_live_memory import claude_memory
    
    # Store a memory
    memory_id = claude_memory.remember(
        category="demo",
        content="This is a test memory from the demo",
        metadata={"demo": True}
    )
    print(f"   [OK] Stored memory with ID: {memory_id}")
    
    # Recall it
    memories = claude_memory.recall("test memory demo")
    print(f"   [OK] Retrieved {len(memories)} memories")
    
except Exception as e:
    print(f"   [ERROR] {e}")

# Test 2: Expense Learning
print("\n2. Testing Expense Categorizer Learning...")
try:
    from routes.expense_categorizer import ExpenseCategorizer
    
    cat = ExpenseCategorizer()
    
    # Teach it
    pattern_id = cat.learn_correction(
        description="Spotify Premium",
        correct_category="Entertainment"
    )
    print(f"   [OK] Taught categorizer about Spotify")
    
    # Test it
    result = cat.categorize("Spotify monthly subscription")
    category = result.get('suggested_category', 'Unknown')
    confidence = result.get('confidence', 0)
    print(f"   [OK] Categorized as: {category} ({confidence}% confidence)")
    
except Exception as e:
    print(f"   [ERROR] {e}")

# Test 3: AI Hub
print("\n3. Testing AI Intelligence Hub...")
try:
    from tools.ai_intelligence_hub import AIIntelligenceHub
    
    hub = AIIntelligenceHub()
    print(f"   [OK] AI Hub initialized")
    
    # Check new methods exist
    has_memory = hasattr(hub, 'memory')
    has_query = hasattr(hub, 'query_intelligence')
    has_learn = hasattr(hub, 'learn_from_correction')
    
    print(f"   [OK] Memory integration: {'Yes' if has_memory else 'No'}")
    print(f"   [OK] Query method: {'Yes' if has_query else 'No'}")
    print(f"   [OK] Learning method: {'Yes' if has_learn else 'No'}")
    
except Exception as e:
    print(f"   [ERROR] {e}")

# Test 4: Unified Context
print("\n4. Testing Unified Context API...")
try:
    import importlib.util
    
    spec = importlib.util.spec_from_file_location(
        "unified_context",
        ".mind/integration/unified_context.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    ctx = module.UnifiedContext()
    result = ctx.get_context("test query")
    
    print(f"   [OK] Unified API response time: {result.response_time_ms:.2f}ms")
    print(f"   [OK] Found {len(result.memories)} memories")
    
except Exception as e:
    print(f"   [ERROR] {e}")

print("\n" + "=" * 50)
print("DEMO COMPLETE")
print("\nTo monitor your AI:")
print("- View insights: python tools/view_ai_insights.py")
print("- Check health: python tools/monitor_ai_memory.py")
print("- Full tests: python tools/test_ai_integration.py")