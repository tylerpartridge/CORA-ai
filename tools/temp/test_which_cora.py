#!/usr/bin/env python3
"""
Quick test to see which CORA chat system is responding
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths

import requests
import json

def test_old_system():
    """Test the old cora-chat system"""
    try:
        response = requests.post(
            "http://localhost:8000/api/cora-chat/",
            json={"message": "test_old_system"},
            timeout=5
        )
        print("OLD SYSTEM (/api/cora-chat/) Response:")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"OLD SYSTEM Error: {e}")
    print("-" * 50)

def test_new_system():
    """Test the new cora-ai system"""
    try:
        response = requests.post(
            "http://localhost:8000/api/cora-ai/chat",
            json={
                "message": "test_new_system", 
                "business_context": None,
                "personality_state": None
            },
            timeout=5
        )
        print("NEW SYSTEM (/api/cora-ai/chat) Response:")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"NEW SYSTEM Error: {e}")
    print("-" * 50)

if __name__ == "__main__":
    print("Testing which CORA system is responding...")
    print("=" * 60)
    test_old_system()
    test_new_system()