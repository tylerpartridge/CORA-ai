#!/usr/bin/env python3
"""
Simple script to test conversational onboarding
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import requests
import json

def test_onboarding_flow():
    """Test the onboarding flow as a new user"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Conversational Onboarding System")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Server health: {response.json()}")
    except Exception as e:
        print(f"❌ Server not running: {e}")
        return
    
    # Test 2: Check if onboarding routes exist
    try:
        response = requests.get(f"{base_url}/docs")
        print("✅ API docs available at /docs")
    except Exception as e:
        print(f"❌ API docs not accessible: {e}")
    
    print("\n🎯 Manual Testing Instructions:")
    print("1. Open http://localhost:8000 in your browser")
    print("2. Look for the chat widget in the bottom right")
    print("3. Click on it to start a conversation")
    print("4. Try these conversation flows:")
    
    print("\n📝 Conversation Flow 1 (New User):")
    print("You: 'Hi, I'm Glen'")
    print("CORA: [Should ask about your business]")
    print("You: 'I do bathroom remodeling'")
    print("CORA: [Should ask about recent jobs]")
    print("You: 'Just finished a $12k bathroom job'")
    print("CORA: [Should show profit insights]")
    
    print("\n📝 Conversation Flow 2 (Skip Option):")
    print("You: 'Can I skip this?'")
    print("CORA: [Should respect your choice]")
    
    print("\n🔍 What to Look For:")
    print("- Green border around chat (onboarding mode)")
    print("- 'Building your profile...' indicator")
    print("- 'View saved data' button")
    print("- Natural conversation (not scripted)")
    print("- Profit insights when you share job details")
    
    print("\n🚨 If Onboarding Doesn't Start:")
    print("1. Open browser console (F12)")
    print("2. Run: window.userNeedsOnboarding = true; location.reload();")
    print("3. This will force onboarding mode")

if __name__ == "__main__":
    test_onboarding_flow() 