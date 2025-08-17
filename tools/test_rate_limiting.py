#!/usr/bin/env python3
"""
Test Rate Limiting Configuration
Verifies that rate limiting is working correctly
"""

import asyncio
import aiohttp
import time
from datetime import datetime

async def test_rate_limit(endpoint="http://localhost:8000/api/health", requests_per_minute=100):
    """Test rate limiting by sending rapid requests"""
    print(f"\n🔥 Testing Rate Limiting")
    print(f"📍 Endpoint: {endpoint}")
    print(f"⚡ Rate limit: {requests_per_minute} requests/minute")
    print("-" * 60)
    
    results = {
        'allowed': 0,
        'rate_limited': 0,
        'errors': 0,
        'timestamps': []
    }
    
    async with aiohttp.ClientSession() as session:
        # Send requests rapidly (more than the limit)
        test_requests = requests_per_minute + 20  # Try to exceed limit
        
        print(f"\n📤 Sending {test_requests} requests rapidly...")
        
        for i in range(test_requests):
            try:
                start = time.time()
                async with session.get(endpoint) as response:
                    duration = time.time() - start
                    
                    if response.status == 200:
                        results['allowed'] += 1
                        print(f"✅ Request {i+1}: Allowed (200)")
                    elif response.status == 429:
                        results['rate_limited'] += 1
                        print(f"🚫 Request {i+1}: Rate limited (429)")
                        
                        # Check rate limit headers
                        if 'X-RateLimit-Limit' in response.headers:
                            print(f"   Limit: {response.headers['X-RateLimit-Limit']}")
                        if 'X-RateLimit-Remaining' in response.headers:
                            print(f"   Remaining: {response.headers['X-RateLimit-Remaining']}")
                        if 'X-RateLimit-Reset' in response.headers:
                            print(f"   Reset: {response.headers['X-RateLimit-Reset']}")
                    else:
                        results['errors'] += 1
                        print(f"❌ Request {i+1}: Error ({response.status})")
                    
                    results['timestamps'].append({
                        'time': datetime.now(),
                        'status': response.status,
                        'duration': duration
                    })
                    
            except Exception as e:
                results['errors'] += 1
                print(f"❌ Request {i+1}: Exception - {str(e)}")
            
            # Small delay to spread requests
            if i < test_requests - 1:
                await asyncio.sleep(0.1)  # 100ms between requests
    
    # Analyze results
    print(f"\n📊 Rate Limiting Test Results:")
    print(f"✅ Allowed requests: {results['allowed']}")
    print(f"🚫 Rate limited: {results['rate_limited']}")
    print(f"❌ Errors: {results['errors']}")
    
    if results['rate_limited'] > 0:
        print(f"\n✅ Rate limiting is WORKING! Blocked {results['rate_limited']} excess requests.")
    else:
        print(f"\n⚠️  Rate limiting may NOT be working. All {results['allowed']} requests were allowed.")
    
    return results

async def test_rate_limit_recovery():
    """Test if rate limit resets properly"""
    print("\n🔄 Testing Rate Limit Recovery")
    print("-" * 60)
    
    endpoint = "http://localhost:8000/api/health"
    
    async with aiohttp.ClientSession() as session:
        # First, hit the rate limit
        print("1️⃣ Hitting rate limit...")
        for i in range(120):  # Exceed 100/minute limit
            try:
                async with session.get(endpoint) as response:
                    if response.status == 429:
                        print(f"   Rate limited at request {i+1}")
                        break
            except:
                pass
            await asyncio.sleep(0.05)
        
        # Wait for rate limit window to reset
        print("\n2️⃣ Waiting 65 seconds for rate limit to reset...")
        await asyncio.sleep(65)
        
        # Try again
        print("\n3️⃣ Testing if rate limit has reset...")
        async with session.get(endpoint) as response:
            if response.status == 200:
                print("✅ Rate limit has reset! Request allowed.")
            else:
                print(f"❌ Still rate limited? Status: {response.status}")

def main():
    """Main test function"""
    print("🛡️ CORA Rate Limiting Test")
    print("=" * 60)
    
    # Check if server is running
    import requests
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=2)
        if response.status_code != 200:
            print(f"⚠️  Server returned status: {response.status_code}")
    except Exception as e:
        print("❌ Server is not running! Start it with: python app.py")
        print(f"   Error: {e}")
        return
    
    # Run tests
    asyncio.run(test_rate_limit())
    
    # Ask if user wants to test recovery
    response = input("\n🔄 Test rate limit recovery (takes 65 seconds)? (y/n): ")
    if response.lower() == 'y':
        asyncio.run(test_rate_limit_recovery())
    
    print("\n✨ Rate limiting test complete!")
    print("\nIf rate limiting is working, you should see:")
    print("- Some requests allowed (up to limit)")
    print("- Some requests blocked with 429 status")
    print("- Rate limit headers in responses")

if __name__ == "__main__":
    main()