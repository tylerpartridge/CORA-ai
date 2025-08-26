#!/usr/bin/env python3

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths

import sys
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.append('.')
from services.cora_ai_service import CORAAIService
import asyncio

async def test_direct():
    print("Testing CORA AI Service directly...")
    print(f"OpenAI Key configured: {'OPENAI_API_KEY' in os.environ}")
    print(f"Key starts with sk-: {os.environ.get('OPENAI_API_KEY', '').startswith('sk-')}")
    print("-" * 50)
    
    service = CORAAIService()
    print(f"AI Enabled: {service.ai_enabled}")
    
    if service.ai_enabled:
        print("Testing with 'plumber'...")
        response = await service.generate_response('plumber')
        print(f"Response: {response}")
    else:
        print("AI not enabled, will use fallback")
        response = service._fallback_response('plumber')
        print(f"Fallback Response: {response}")

if __name__ == "__main__":
    asyncio.run(test_direct())