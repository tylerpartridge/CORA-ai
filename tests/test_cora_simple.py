
import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import json

BASE_URL = "http://localhost:8080"
CHAT_ENDPOINT = f"{BASE_URL}/api/cora-chat/"

# Test a few key scenarios
test_questions = [
    "How much does CORA cost?",
    "How are you different from QuickBooks?",
    "I'm too busy to learn a new system",
    "Is my data secure?",
    "How do I get started?"
]

print("Testing CORA Sales Intelligence System\n")

for i, question in enumerate(test_questions, 1):
    print(f"\nTest {i}: {question}")
    
    try:
        response = requests.post(CHAT_ENDPOINT, json={"message": question})
        if response.status_code == 200:
            data = response.json()
            print(f"CORA: {data['message']}")
            print(f"Messages remaining: {data['messages_remaining']}")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {str(e)}")

print("\nTest complete!")