#!/usr/bin/env python3
"""
Test script to evaluate Claude's AI integration work
"""

import sys
import os
sys.path.append('.')

def test_claude_memory():
    """Test Claude's live memory system"""
    print("🧠 Testing Claude Live Memory...")
    
    try:
        from tools.claude_live_memory import claude_memory
        
        # Test memory storage
        memory_id = claude_memory.remember(
            category="test",
            content="Integration test memory",
            metadata={"test": True, "integration": "claude"}
        )
        print(f"✅ Memory stored: {memory_id}")
        
        # Test memory recall
        memories = claude_memory.recall("integration test", limit=3)
        print(f"✅ Memory recall: {len(memories)} memories found")
        
        # Test pattern learning
        pattern_id = claude_memory.learn_pattern(
            pattern_type="test_pattern",
            example="test example",
            solution="test solution"
        )
        print(f"✅ Pattern learned: {pattern_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Claude memory test failed: {e}")
        return False

def test_unified_context():
    """Test unified context API"""
    print("\n🔗 Testing Unified Context API...")
    
    try:
        # Import with proper path handling
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "unified_context", 
            ".mind/integration/unified_context.py"
        )
        unified_context_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(unified_context_module)
        UnifiedContext = unified_context_module.UnifiedContext
        
        # Test unified context
        uc = UnifiedContext()
        result = uc.get_context("test query")
        
        print(f"✅ Unified context response time: {result.response_time_ms:.2f}ms")
        print(f"✅ Emergence score: {result.emergence_score}")
        print(f"✅ Memories found: {len(result.memories)}")
        print(f"✅ Patterns found: {len(result.patterns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Unified context test failed: {e}")
        return False

def test_ai_intelligence_hub():
    """Test AI intelligence hub integration"""
    print("\n🤖 Testing AI Intelligence Hub...")
    
    try:
        from tools.ai_intelligence_hub import AIIntelligenceHub
        
        # Test hub initialization
        hub = AIIntelligenceHub()
        print("✅ Hub initialized successfully")
        
        # Test memory property
        memory = hub.memory
        print("✅ Memory property accessed successfully")
        
        # Test system status
        status = hub.get_system_status()
        print(f"✅ System status: {status.orchestrator_status}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI intelligence hub test failed: {e}")
        return False

def check_build_rules_compliance():
    """Check compliance with BUILD_RULES.md"""
    print("\n📋 Checking BUILD_RULES.md Compliance...")
    
    compliance_issues = []
    
    # Check file headers
    files_to_check = [
        "tools/claude_live_memory.py",
        "tools/ai_intelligence_hub.py",
        ".mind/integration/unified_context.py"
    ]
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for CORA header format
            if "🧭 LOCATION:" not in content:
                compliance_issues.append(f"Missing CORA header in {file_path}")
            if "🎯 PURPOSE:" not in content:
                compliance_issues.append(f"Missing purpose in {file_path}")
            if "💡 AI HINT:" not in content:
                compliance_issues.append(f"Missing AI hint in {file_path}")
                
        except FileNotFoundError:
            compliance_issues.append(f"File not found: {file_path}")
    
    if compliance_issues:
        print("❌ Compliance issues found:")
        for issue in compliance_issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ All files comply with BUILD_RULES.md")
        return True

def check_performance():
    """Check performance metrics"""
    print("\n⚡ Checking Performance...")
    
    try:
        from tools.claude_live_memory import claude_memory
        import time
        
        # Test memory operation speed
        start_time = time.time()
        memory_id = claude_memory.remember("performance_test", "test content")
        memory_time = (time.time() - start_time) * 1000
        
        # Test recall speed
        start_time = time.time()
        memories = claude_memory.recall("performance_test")
        recall_time = (time.time() - start_time) * 1000
        
        print(f"✅ Memory storage: {memory_time:.2f}ms")
        print(f"✅ Memory recall: {recall_time:.2f}ms")
        
        # Check if within performance targets
        if memory_time < 50 and recall_time < 100:
            print("✅ Performance targets met")
            return True
        else:
            print("⚠️ Performance targets exceeded")
            return False
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 CORA AI Integration Evaluation")
    print("=" * 50)
    
    results = {
        "claude_memory": test_claude_memory(),
        "unified_context": test_unified_context(),
        "ai_intelligence_hub": test_ai_intelligence_hub(),
        "build_rules_compliance": check_build_rules_compliance(),
        "performance": check_performance()
    }
    
    print("\n📊 Test Results Summary:")
    print("=" * 30)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    main() 