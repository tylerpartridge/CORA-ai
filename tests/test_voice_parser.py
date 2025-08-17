#!/usr/bin/env python3

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

"""Test the voice parser locally without server"""

import sys
sys.path.append('/mnt/host/c/CORA')

from routes.expenses import parse_voice_expense

# Test phrases
test_phrases = [
    "Home Depot receipt Johnson bathroom three forty seven",
    "Lowes purchase for Smith kitchen project forty two dollars",
    "Gas station fifty bucks for the downtown office job",
    "Lumber yard receipt Johnson deck project one twenty five",
    "bought some wire at electrical supply for the Miller house rewire sixty eight dollars",
    "lunch for the crew twenty three fifty",
]

print("Testing Voice Parser with Construction Phrases\n")
print("=" * 60)

for phrase in test_phrases:
    print(f"\nPhrase: \"{phrase}\"")
    result = parse_voice_expense(phrase)
    
    print(f"Parsed:")
    print(f"  Amount: ${result['amount']:.2f}" if result['amount'] else "  Amount: NOT DETECTED")
    print(f"  Vendor: {result['vendor']}")
    print(f"  Category: {result['category']}")
    print(f"  Job: {result['job_name']}" if result['job_name'] else "  Job: None")
    print(f"  Confidence: Amount={result['confidence']['amount']:.1f}, Vendor={result['confidence']['vendor']:.1f}, Job={result['confidence']['job']:.1f}")
    print("-" * 40)

print("\nParser test complete!")