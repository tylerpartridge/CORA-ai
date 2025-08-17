
import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

"""Test improved CORA responses to verify iterations"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.cora_chat import generate_mock_response

test_cases = [
    ("How much does CORA cost?", "pricing"),
    ("How are you different from QuickBooks?", "competitor"),
    ("I'm too busy to learn new software", "objection"),
    ("Is my data safe with you?", "security"),
    ("Can you help me track mileage?", "feature"),
    ("I'm stressed about taxes", "tax"),
    ("How do I get started?", "start")
]

print("=== Testing Improved CORA Responses ===\n")

results = []
for i, (question, category) in enumerate(test_cases):
    print(f"[{category.upper()}] Q: {question}")
    response = generate_mock_response(question, i)
    print(f"A: {response}")
    
    # Evaluate improvements
    has_trial = "30-day" in response or "free trial" in response or "try free" in response.lower()
    has_testimonial = any(name in response for name in ["Sarah", "Mike", "Lisa", "$1,847", "$2,134", "$3,291"])
    word_count = len(response.split())
    sentence_count = response.count('.') + response.count('!') + response.count('?')
    
    print(f"  Trial mentioned: {'YES' if has_trial else 'NO'}")
    print(f"  Testimonial: {'YES' if has_testimonial else 'NO'}")  
    print(f"  Length: {word_count} words, {sentence_count} sentences")
    print(f"  Good length: {'YES' if sentence_count <= 3 else 'NO (too long)'}\n")
    
    results.append({
        "category": category,
        "has_trial": has_trial,
        "has_testimonial": has_testimonial,
        "good_length": sentence_count <= 3
    })

# Summary
print("\n=== IMPROVEMENT SUMMARY ===")
print(f"Tests: {len(results)}")
print(f"Trial mentioned: {sum(1 for r in results if r['has_trial'])}/{len(results)} ({100*sum(1 for r in results if r['has_trial'])/len(results):.0f}%)")
print(f"Testimonials used: {sum(1 for r in results if r['has_testimonial'])}/{len(results)} ({100*sum(1 for r in results if r['has_testimonial'])/len(results):.0f}%)")
print(f"Good length (<=3 sentences): {sum(1 for r in results if r['good_length'])}/{len(results)} ({100*sum(1 for r in results if r['good_length'])/len(results):.0f}%)")

if all(r['has_trial'] for r in results) and all(r['good_length'] for r in results):
    print("\nALL IMPROVEMENTS IMPLEMENTED SUCCESSFULLY!")
else:
    print("\nSome improvements still needed")