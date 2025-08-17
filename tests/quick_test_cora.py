import requests
import json

# Test CORA Sales Intelligence
url = "http://localhost:8000/api/cora-chat/"

test_cases = [
    ("How much does CORA cost?", "pricing"),
    ("How are you different from QuickBooks?", "competitor"),
    ("I'm too busy to learn new software", "objection"),
    ("Is my data safe with you?", "security"),
    ("Can you help me track mileage?", "feature")
]

print("=== CORA Sales Intelligence Test ===\n")

results = []

for question, category in test_cases:
    print(f"[{category.upper()}] Q: {question}")
    
    try:
        response = requests.post(url, json={"message": question}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            answer = data.get('message', 'No response')
            print(f"A: {answer}\n")
            
            # Quick evaluation
            evaluation = {
                "category": category,
                "has_trial": "30-day" in answer or "free trial" in answer,
                "has_price": "$" in answer,
                "asks_question": "?" in answer,
                "length": len(answer),
                "good_length": 100 < len(answer) < 300
            }
            results.append(evaluation)
        else:
            print(f"Error: {response.status_code}\n")
    except Exception as e:
        print(f"Connection error: {e}\n")
        break

# Summary
if results:
    print("\n=== Evaluation Summary ===")
    print(f"Tests completed: {len(results)}")
    print(f"Mentions trial: {sum(1 for r in results if r['has_trial'])}/{len(results)}")
    print(f"Includes pricing: {sum(1 for r in results if r['has_price'])}/{len(results)}")
    print(f"Asks questions: {sum(1 for r in results if r['asks_question'])}/{len(results)}")
    print(f"Good length: {sum(1 for r in results if r['good_length'])}/{len(results)}")
    
    print("\n=== Iterations Needed ===")
    iterations = []
    
    if sum(1 for r in results if r['has_trial']) < len(results) * 0.8:
        iterations.append("- Always mention 30-day free trial in responses")
    
    if sum(1 for r in results if r['asks_question']) < len(results) * 0.8:
        iterations.append("- End more responses with engaging questions")
        
    if any(r['length'] > 300 for r in results):
        iterations.append("- Keep responses shorter (2-3 sentences)")
        
    if not all(r['has_price'] for r in results if r['category'] == 'pricing'):
        iterations.append("- Include specific pricing in pricing questions")
    
    if iterations:
        for item in iterations:
            print(item)
    else:
        print("All tests passed!")