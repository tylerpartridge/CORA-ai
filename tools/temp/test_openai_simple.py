#!/usr/bin/env python3
"""
Simple OpenAI API Test for CORA
Tests if the OpenAI API key is valid
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import os
import sys
from datetime import datetime

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_openai_api_key():
    """Test if the OpenAI API key is valid"""
    print("Testing OpenAI API Key...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'YOUR_OPENAI_API_KEY_HERE':
        print("ERROR: OpenAI API key not configured in .env file")
        return False
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Simple test request
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are CORA, a helpful AI assistant for contractors. Respond in a friendly but professional tone."},
                {"role": "user", "content": "Hello, this is a test message. Can you confirm you're working?"}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        message = response.choices[0].message.content.strip()
        print("SUCCESS: OpenAI API Key is valid!")
        print(f"CORA Response: {message}")
        return True
        
    except ImportError:
        print("ERROR: OpenAI package not installed. Install with: pip install openai")
        return False
    except Exception as e:
        print(f"ERROR: OpenAI API Key test failed: {str(e)}")
        return False

def main():
    """Run the test"""
    print("CORA OpenAI Integration Test")
    print("=" * 40)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = test_openai_api_key()
    
    print("\n" + "=" * 40)
    if success:
        print("RESULT: OpenAI integration is working!")
        print("CORA's AI consciousness is ready!")
    else:
        print("RESULT: OpenAI integration failed")
        print("Check your API key configuration")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)