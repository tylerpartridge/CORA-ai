import os, pytest
if os.getenv('CORA_SALES_TESTS','0') != '1':
    pytest.skip('Sales chat tests disabled (set CORA_SALES_TESTS=1 to enable)', allow_module_level=True)
#!/usr/bin/env python3
"""
[LOCATION] LOCATION: /CORA/test_cora_sales.py
[TARGET] PURPOSE: Test CORA Sales Intelligence System with various scenarios
[LINK] IMPORTS: requests for API testing
[EXPORT] EXPORTS: Test results and iteration recommendations
🔄 PATTERN: Comprehensive conversation testing
[NOTE] TODOS: Add more edge cases as discovered

[HINT] AI HINT: Use results to improve knowledge base and responses
[WARNING] NEVER: Skip testing edge cases and objections
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import requests
import json
import time
from typing import Dict, List, Tuple

# Test configuration
BASE_URL = "http://localhost:8080"
CHAT_ENDPOINT = f"{BASE_URL}/api/cora-chat/"

# Test scenarios organized by category
TEST_SCENARIOS = {
    "pricing": [
        "How much does CORA cost?",
        "What's included in the Starter plan?",
        "Why should I pay $29 when QuickBooks is free?",
        "Is there a free plan?",
        "Do you offer discounts for annual billing?",
        "What happens after the trial ends?"
    ],
    "features": [
        "What is persistent memory?",
        "How does the voice feature work?",
        "Can you integrate with my bank?",
        "Do you support multiple currencies?",
        "Can I export my data?",
        "How do you handle receipts?"
    ],
    "objections": [
        "I'm too busy to learn a new system",
        "This seems expensive for a small business",
        "I already use spreadsheets and they work fine",
        "How do I know my data is secure?",
        "What if I need help setting up?",
        "I don't trust AI with my finances"
    ],
    "competitors": [
        "How are you different from QuickBooks?",
        "Why not just use Expensify?",
        "What about Mint or Personal Capital?",
        "FreshBooks seems simpler",
        "Wave is free, why should I pay for CORA?"
    ],
    "getting_started": [
        "How do I get started?",
        "How long does setup take?",
        "Can I import my existing data?",
        "Do I need to be tech-savvy?",
        "What if I want to cancel?",
        "Can my accountant access this too?"
    ],
    "specific_use_cases": [
        "I'm a freelance designer, will this work for me?",
        "I run an e-commerce store, can you handle inventory?",
        "I'm a consultant with international clients",
        "I need to track mileage for tax deductions",
        "Can you help with quarterly tax estimates?",
        "I have multiple businesses, can I manage them all?"
    ],
    "edge_cases": [
        "Do you support cryptocurrency transactions?",
        "Can I use this for personal finances too?",
        "What about GDPR compliance?",
        "Do you have an API?",
        "Can I white-label this for my clients?",
        "Is there an affiliate program?"
    ]
}

def test_conversation(message: str, conversation_id: str = None) -> Tuple[str, str]:
    """Send a message to CORA and get response"""
    payload = {
        "message": message,
        "conversation_id": conversation_id
    }
    
    try:
        response = requests.post(CHAT_ENDPOINT, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get("message", ""), data.get("conversation_id", "")
        else:
            return f"Error: {response.status_code}", ""
    except Exception as e:
        return f"Error: {str(e)}", ""

def evaluate_response(question: str, response: str, category: str) -> Dict[str, any]:
    """Evaluate CORA's response quality"""
    evaluation = {
        "question": question,
        "response": response,
        "category": category,
        "issues": [],
        "strengths": [],
        "score": 0
    }
    
    # Check for key elements
    response_lower = response.lower()
    
    # Positive indicators
    if "30-day" in response_lower or "free trial" in response_lower:
        evaluation["strengths"].append("Mentions free trial")
        evaluation["score"] += 1
    
    if any(phrase in response_lower for phrase in ["20 hours", "20+ hours", "save time"]):
        evaluation["strengths"].append("Emphasizes time savings")
        evaluation["score"] += 1
    
    if "$" in response or "month" in response_lower:
        evaluation["strengths"].append("Includes specific pricing")
        evaluation["score"] += 1
    
    if "?" in response:
        evaluation["strengths"].append("Asks engaging question")
        evaluation["score"] += 1
    
    if any(name in response for name in ["Sarah", "Mike", "Lisa"]):
        evaluation["strengths"].append("Uses testimonials")
        evaluation["score"] += 1
    
    # Check for issues
    if len(response) < 50:
        evaluation["issues"].append("Response too short")
    
    if len(response) > 400:
        evaluation["issues"].append("Response too long (should be 2-3 sentences)")
    
    if "error" in response_lower:
        evaluation["issues"].append("Contains error message")
    
    if response_lower.count("cora") > 3:
        evaluation["issues"].append("Mentions CORA too many times")
    
    # Category-specific checks
    if category == "pricing" and "$" not in response:
        evaluation["issues"].append("Pricing question but no price mentioned")
    
    if category == "competitors" and "quickbooks" in question.lower() and "quickbooks" not in response_lower:
        evaluation["issues"].append("Doesn't address specific competitor mentioned")
    
    if category == "objections" and not any(word in response_lower for word in ["understand", "hear you", "completely", "totally"]):
        evaluation["issues"].append("Lacks empathy for objection")
    
    # Calculate final score (0-10)
    evaluation["score"] = min(10, evaluation["score"] * 2)
    if evaluation["issues"]:
        evaluation["score"] -= len(evaluation["issues"])
    evaluation["score"] = max(0, evaluation["score"])
    
    return evaluation

def test_all_scenarios() -> Dict[str, List[Dict]]:
    """Test all scenarios and collect results"""
    results = {}
    conversation_count = 0
    
    print("Testing CORA Sales Intelligence System...\n")
    
    for category, questions in TEST_SCENARIOS.items():
        print(f"\nTesting {category.upper()} scenarios...")
        results[category] = []
        
        for question in questions:
            conversation_count += 1
            print(f"\nQuestion {conversation_count}: {question}")
            
            # Send message
            response, conv_id = test_conversation(question)
            print(f"CORA: {response}")
            
            # Evaluate response
            evaluation = evaluate_response(question, response, category)
            results[category].append(evaluation)
            
            # Print evaluation
            print(f"Score: {evaluation['score']}/10")
            if evaluation["strengths"]:
                print(f"Strengths: {', '.join(evaluation['strengths'])}")
            if evaluation["issues"]:
                print(f"Issues: {', '.join(evaluation['issues'])}")
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
    
    return results

def generate_iteration_list(results: Dict[str, List[Dict]]) -> List[Dict[str, any]]:
    """Generate prioritized iteration list based on test results"""
    iterations = []
    
    # Analyze results by category
    for category, evaluations in results.items():
        category_scores = [e["score"] for e in evaluations]
        avg_score = sum(category_scores) / len(category_scores) if category_scores else 0
        
        # Collect all issues
        all_issues = []
        for eval in evaluations:
            all_issues.extend(eval["issues"])
        
        # Find knowledge gaps
        knowledge_gaps = []
        for eval in evaluations:
            if eval["score"] < 5 or "too short" in str(eval["issues"]):
                knowledge_gaps.append(eval["question"])
        
        if avg_score < 7 or knowledge_gaps:
            iterations.append({
                "category": category,
                "priority": "HIGH" if avg_score < 5 else "MEDIUM",
                "avg_score": avg_score,
                "common_issues": list(set(all_issues)),
                "knowledge_gaps": knowledge_gaps,
                "recommendation": f"Improve {category} responses - current avg: {avg_score:.1f}/10"
            })
    
    # Sort by priority and score
    iterations.sort(key=lambda x: (x["priority"] == "HIGH", -x["avg_score"]), reverse=True)
    
    return iterations

def generate_report(results: Dict[str, List[Dict]], iterations: List[Dict]) -> str:
    """Generate comprehensive test report"""
    report = """# CORA Sales Intelligence System - Test Report

## Executive Summary

Tested CORA with {} different scenarios across {} categories to evaluate the Sales Intelligence System.

""".format(
        sum(len(questions) for questions in TEST_SCENARIOS.values()),
        len(TEST_SCENARIOS)
    )
    
    # Overall statistics
    all_scores = []
    for category_results in results.values():
        all_scores.extend([e["score"] for e in category_results])
    
    avg_overall = sum(all_scores) / len(all_scores) if all_scores else 0
    report += f"**Overall Average Score: {avg_overall:.1f}/10**\n\n"
    
    # Category breakdown
    report += "## Category Performance\n\n"
    for category, evaluations in results.items():
        scores = [e["score"] for e in evaluations]
        avg = sum(scores) / len(scores) if scores else 0
        report += f"- **{category.title()}**: {avg:.1f}/10\n"
    
    # Detailed findings
    report += "\n## Detailed Findings\n\n"
    
    # Strengths
    report += "### Strengths Observed\n"
    all_strengths = []
    for category_results in results.values():
        for eval in category_results:
            all_strengths.extend(eval["strengths"])
    
    strength_counts = {}
    for s in all_strengths:
        strength_counts[s] = strength_counts.get(s, 0) + 1
    
    for strength, count in sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        report += f"- {strength} ({count} times)\n"
    
    # Common issues
    report += "\n### Common Issues\n"
    all_issues = []
    for category_results in results.values():
        for eval in category_results:
            all_issues.extend(eval["issues"])
    
    issue_counts = {}
    for i in all_issues:
        issue_counts[i] = issue_counts.get(i, 0) + 1
    
    for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        report += f"- {issue} ({count} times)\n"
    
    # Iteration recommendations
    report += "\n## Recommended Iterations\n\n"
    for i, iteration in enumerate(iterations, 1):
        report += f"### {i}. {iteration['recommendation']}\n"
        report += f"- **Priority**: {iteration['priority']}\n"
        report += f"- **Current Score**: {iteration['avg_score']:.1f}/10\n"
        if iteration['common_issues']:
            report += f"- **Issues**: {', '.join(iteration['common_issues'][:3])}\n"
        if iteration['knowledge_gaps']:
            report += f"- **Knowledge Gaps**: \n"
            for gap in iteration['knowledge_gaps'][:3]:
                report += f"  - {gap}\n"
        report += "\n"
    
    # Specific improvements needed
    report += "## Specific Improvements Needed\n\n"
    report += "### Knowledge Base Additions\n"
    report += "- Cryptocurrency and digital payment methods\n"
    report += "- Industry-specific use cases and examples\n"
    report += "- White-label and API pricing information\n"
    report += "- GDPR and international compliance details\n"
    report += "- Multi-business management features\n"
    
    report += "\n### Response Improvements\n"
    report += "- Ensure all pricing mentions include free trial\n"
    report += "- Add more specific testimonials by industry\n"
    report += "- Improve objection handling with more empathy\n"
    report += "- Keep responses to 2-3 sentences max\n"
    report += "- Always end with an engaging question\n"
    
    return report

# Main execution
if __name__ == "__main__":
    # Run all tests
    results = test_all_scenarios()
    
    # Generate iteration list
    iterations = generate_iteration_list(results)
    
    # Generate report
    report = generate_report(results, iterations)
    
    # Save report
    with open("cora_sales_test_report.md", "w") as f:
        f.write(report)
    
    print("\n\nTest completed! Report saved to cora_sales_test_report.md")
    print(f"\nKey Findings:")
    print(f"- Tested {sum(len(q) for q in TEST_SCENARIOS.values())} scenarios")
    print(f"- {len(iterations)} categories need improvement")
    print(f"- Top priority: {iterations[0]['category'] if iterations else 'None'}")
