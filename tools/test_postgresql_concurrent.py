#!/usr/bin/env python3
"""
Test PostgreSQL with concurrent connections
This simulates the load that was crashing SQLite
"""

import asyncio
import aiohttp
import time
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def make_request(session, url, request_num):
    """Make a single request to the API"""
    try:
        start = time.time()
        async with session.get(url) as response:
            status = response.status
            duration = time.time() - start
            return {
                'request_num': request_num,
                'status': status,
                'duration': duration,
                'success': status == 200
            }
    except Exception as e:
        return {
            'request_num': request_num,
            'status': 0,
            'duration': 0,
            'success': False,
            'error': str(e)
        }

async def test_concurrent_load(num_users=50, endpoint="http://localhost:8000/api/health"):
    """Test with concurrent users"""
    print(f"\n🚀 Testing PostgreSQL with {num_users} concurrent users...")
    print(f"📍 Endpoint: {endpoint}")
    print("-" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Create concurrent requests
        tasks = []
        for i in range(num_users):
            task = make_request(session, endpoint, i + 1)
            tasks.append(task)
        
        # Execute all requests concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Analyze results
        successful = sum(1 for r in results if r['success'])
        failed = num_users - successful
        avg_duration = sum(r['duration'] for r in results) / num_users
        
        print(f"\n📊 Results:")
        print(f"✅ Successful requests: {successful}/{num_users} ({successful/num_users*100:.1f}%)")
        print(f"❌ Failed requests: {failed}/{num_users} ({failed/num_users*100:.1f}%)")
        print(f"⏱️  Total time: {total_time:.2f}s")
        print(f"⚡ Average response time: {avg_duration:.3f}s")
        
        # Show errors if any
        errors = [r for r in results if not r['success']]
        if errors:
            print(f"\n⚠️  Errors encountered:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"   Request {error['request_num']}: {error.get('error', 'Unknown error')}")
            if len(errors) > 5:
                print(f"   ... and {len(errors) - 5} more errors")
        
        return successful == num_users

async def progressive_load_test():
    """Test with progressively increasing load"""
    test_levels = [10, 25, 50, 100, 200]
    
    print("\n🔥 Progressive Load Testing with PostgreSQL")
    print("=" * 60)
    
    for num_users in test_levels:
        success = await test_concurrent_load(num_users)
        
        if not success:
            print(f"\n⚠️  System showed stress at {num_users} concurrent users")
            print("Consider optimizing connection pooling or scaling horizontally")
            break
        else:
            print(f"\n✅ System handled {num_users} concurrent users perfectly!")
        
        # Brief pause between tests
        if num_users < test_levels[-1]:
            print("\nWaiting 2 seconds before next test...")
            await asyncio.sleep(2)

def main():
    """Main function"""
    print("🐘 PostgreSQL Concurrent Connection Test")
    print("=" * 60)
    print("Make sure:")
    print("1. PostgreSQL is running")
    print("2. CORA is running with PostgreSQL configuration")
    print("3. You've run the migration script")
    print("")
    
    # Check if server is running
    import requests
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=2)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("⚠️  Server returned status:", response.status_code)
    except Exception as e:
        print("❌ Server is not running! Start it with: python app.py")
        print(f"   Error: {e}")
        return
    
    # Run the tests
    asyncio.run(progressive_load_test())
    
    print("\n" + "=" * 60)
    print("✨ Test complete!")
    print("\nNext steps:")
    print("1. If all tests passed: PostgreSQL is ready for production!")
    print("2. If tests failed at high load: Consider connection pool tuning")
    print("3. Monitor your PostgreSQL logs for any warnings")

if __name__ == "__main__":
    main()