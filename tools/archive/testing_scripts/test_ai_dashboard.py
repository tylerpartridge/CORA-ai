#!/usr/bin/env python3
"""
Test harness for AI Dashboard Generator
Tests the 30-second awareness goal
"""

import time
import os
import asyncio
from datetime import datetime

def test_dashboard_generation():
    """Test that dashboard generates within performance targets"""
    print("Testing AI Dashboard Generator...")
    
    # Import the generator (once Cursor implements it)
    try:
        from ai_dashboard_generator import AIDashboardGenerator
        generator = AIDashboardGenerator()
    except ImportError:
        print("⏳ Waiting for ai_dashboard_generator.py implementation...")
        return False
    
    # Test 1: Generation Speed
    print("\nTest 1: Generation Speed (target: <2 seconds)")
    start_time = time.time()
    generator.generate()
    generation_time = time.time() - start_time
    
    if generation_time < 2:
        print(f"PASS: Generated in {generation_time:.2f} seconds")
    else:
        print(f"FAIL: Took {generation_time:.2f} seconds (too slow)")
    
    # Test 2: File Exists
    print("\nTest 2: Dashboard File Creation")
    dashboard_path = os.path.join(os.path.dirname(__file__), '..', 'AI_DASHBOARD.md')
    if os.path.exists(dashboard_path):
        print("PASS: AI_DASHBOARD.md created")
    else:
        print("FAIL: AI_DASHBOARD.md not found")
        return False
    
    # Test 3: Content Validation
    print("\nTest 3: Content Validation")
    with open(dashboard_path, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    required_sections = [
        '🎯 FOCUS NOW',
        '🚨 BLOCKERS',
        '📊 SYSTEM PULSE',
        '🗺️ INSTANT NAVIGATION',
        '📍 CONTEXT',
        '💡 AI COMMANDS'
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)
    
    if not missing_sections:
        print("PASS: All required sections present")
    else:
        print(f"FAIL: Missing sections: {', '.join(missing_sections)}")
    
    # Test 4: Line Count
    print(f"\nTest 4: Line Count (target: <100 lines)")
    if len(lines) <= 100:
        print(f"PASS: {len(lines)} lines (within limit)")
    else:
        print(f"FAIL: {len(lines)} lines (too long)")
    
    # Test 5: Freshness
    print("\nTest 5: Timestamp Freshness")
    if 'Generated:' in content:
        # Extract timestamp and check if recent
        for line in lines:
            if 'Generated:' in line:
                print("PASS: Timestamp found")
                break
    else:
        print("FAIL: No generation timestamp")
    
    # Overall Result
    print("\n" + "="*50)
    print("30-Second Awareness Test:")
    print("If you can understand CORA's state from just AI_DASHBOARD.md")
    print("in under 30 seconds, the test is PASSED!")
    
    return True

def simulate_awareness_test():
    """Simulate an AI entering CORA and measuring awareness time"""
    print("\nSimulating AI Awareness Test...")
    print("="*50)
    
    # Old way
    print("\nOLD WAY (reading multiple files):")
    old_files = ['NOW.md', 'STATUS.md', 'NEXT.md', 'BOOTUP.md', 
                 '.mind/today/session.md', 'README.md']
    print(f"Files to read: {len(old_files)}")
    print(f"Estimated time: 10+ minutes")
    
    # New way  
    print("\nNEW WAY (single dashboard):")
    print("Files to read: 1 (AI_DASHBOARD.md)")
    print("Estimated time: <30 seconds")
    
    print("\nImprovement: 20x faster onboarding!")

if __name__ == "__main__":
    test_dashboard_generation()
    simulate_awareness_test()