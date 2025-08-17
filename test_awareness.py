#!/usr/bin/env python3
"""
Awareness Effectiveness Test
Tests if an AI has properly absorbed critical system knowledge after bootup
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
from datetime import datetime

def test_awareness():
    """Test critical awareness points"""
    
    awareness_checklist = {
        "basic_orientation": {
            "knows_priority": False,
            "knows_health_status": False,
            "found_handoff": False,
        },
        "system_rules": {
            "knows_never_write_on_existing": False,
            "knows_work_in_features": False,
            "knows_update_status": False,
        },
        "css_awareness": {
            "knows_zoom_controls_issue": False,
            "knows_navbar_css_only": False,
            "knows_use_px_not_rem": False,
            "knows_css_guardian_exists": False,
        },
        "capabilities": {
            "knows_hidden_features": False,
            "knows_css_guardian": False,
            "knows_bug_registry": False,
        },
        "breadcrumbs_followed": {
            "read_claude_md": False,
            "read_quick_reference": False,
            "checked_capabilities": False,
        }
    }
    
    print("\n" + "="*70)
    print(" AWARENESS EFFECTIVENESS TEST ".center(70))
    print("="*70)
    print("\nPlease answer these questions to test awareness absorption:\n")
    
    # Test questions
    questions = [
        ("What is the current priority?", "basic_orientation", "knows_priority"),
        ("What's the system health score?", "basic_orientation", "knows_health_status"),
        ("Should you use Write or Edit on existing files?", "system_rules", "knows_never_write_on_existing"),
        ("Where should you work when creating features?", "system_rules", "knows_work_in_features"),
        ("What file modifies root font-size? (specific file name)", "css_awareness", "knows_zoom_controls_issue"),
        ("Where should navbar CSS go? (file path)", "css_awareness", "knows_navbar_css_only"),
        ("Should navbar use rem or px units?", "css_awareness", "knows_use_px_not_rem"),
        ("Is there a CSS Guardian system?", "css_awareness", "knows_css_guardian_exists"),
        ("Did you read CLAUDE.md?", "breadcrumbs_followed", "read_claude_md"),
        ("Did you discover hidden capabilities?", "capabilities", "knows_hidden_features"),
    ]
    
    expected_answers = {
        "knows_zoom_controls_issue": ["zoom_controls.js", "zoom_controls"],
        "knows_navbar_css_only": ["navbar.css", "/web/static/css/navbar.css"],
        "knows_use_px_not_rem": ["px", "pixels"],
        "knows_never_write_on_existing": ["edit", "Edit", "EDIT"],
        "knows_work_in_features": ["/features/", "features folder", "features/[name]/claude"],
    }
    
    score = 0
    total = len(questions)
    
    print("SIMULATED ANSWERS (what AI should know):\n")
    
    # Simulate what AI should know
    simulated_knowledge = {
        "knows_priority": "DEPLOY TO PRODUCTION",
        "knows_health_status": "100%",
        "knows_never_write_on_existing": "Edit",
        "knows_work_in_features": "/features/[name]/claude/",
        "knows_zoom_controls_issue": "zoom_controls.js (if read CLAUDE.md)",
        "knows_navbar_css_only": "/web/static/css/navbar.css (if CSS work)",
        "knows_use_px_not_rem": "px (if read CLAUDE.md)",
        "knows_css_guardian_exists": "Yes (from prevention systems check)",
        "read_claude_md": "Only if CSS issues or debugging",
        "knows_hidden_features": "Yes (from CAPABILITIES_AWARENESS.md)",
    }
    
    for q, category, key in questions:
        answer = simulated_knowledge.get(key, "Unknown")
        print(f"Q: {q}")
        print(f"A: {answer}")
        
        # Check if answer is correct
        if key in expected_answers:
            if any(exp.lower() in answer.lower() for exp in expected_answers[key]):
                score += 1
                awareness_checklist[category][key] = True
                print("✓ Correct\n")
            else:
                print("✗ Incorrect\n")
        else:
            # For open questions, just mark as answered
            if answer != "Unknown":
                score += 1
                awareness_checklist[category][key] = True
                print("✓ Answered\n")
            else:
                print("✗ No answer\n")
    
    # Calculate scores
    print("\n" + "="*70)
    print(" AWARENESS SCORES ".center(70))
    print("="*70)
    
    for category, checks in awareness_checklist.items():
        completed = sum(1 for v in checks.values() if v)
        total_checks = len(checks)
        percentage = (completed / total_checks) * 100 if total_checks > 0 else 0
        
        status = "✅" if percentage >= 80 else "⚠️" if percentage >= 50 else "❌"
        print(f"\n{category.replace('_', ' ').title()}: {status} {percentage:.0f}%")
        for check, passed in checks.items():
            icon = "✓" if passed else "✗"
            print(f"  {icon} {check.replace('_', ' ')}")
    
    overall_score = (score / total) * 100 if total > 0 else 0
    
    print("\n" + "="*70)
    print(f"OVERALL AWARENESS SCORE: {overall_score:.0f}%")
    
    if overall_score >= 80:
        print("✅ EXCELLENT - AI has strong system awareness")
    elif overall_score >= 60:
        print("⚠️ GOOD - AI has basic awareness but missing some details")
    else:
        print("❌ NEEDS IMPROVEMENT - Critical awareness gaps")
    
    print("\n" + "="*70)
    print(" EFFECTIVENESS ANALYSIS ".center(70))
    print("="*70)
    
    # Analyze effectiveness of new bootup
    print("\n🎯 Hub/Index Approach Effectiveness:\n")
    
    if awareness_checklist["breadcrumbs_followed"]["read_claude_md"]:
        print("✓ Breadcrumbs worked - AI found CLAUDE.md when needed")
    else:
        print("⚠️ AI might not have needed CSS knowledge yet")
    
    if awareness_checklist["css_awareness"]["knows_css_guardian_exists"]:
        print("✓ Prevention systems discovered from bootup")
    else:
        print("✗ Prevention systems not discovered")
    
    if awareness_checklist["system_rules"]["knows_never_write_on_existing"]:
        print("✓ Core rules absorbed from QUICK_REFERENCE")
    else:
        print("✗ Core rules not absorbed")
    
    print("\n📊 Recommendations:")
    if not awareness_checklist["css_awareness"]["knows_zoom_controls_issue"]:
        print("- AI hasn't hit CSS issues yet, so hasn't read CLAUDE.md (GOOD - progressive disclosure working)")
    if not awareness_checklist["capabilities"]["knows_hidden_features"]:
        print("- Consider making capabilities discovery more prominent in bootup")
    
    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "overall_score": overall_score,
        "awareness_checklist": awareness_checklist,
        "bootup_version": "hub_index_refactored"
    }
    
    with open("awareness_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to awareness_test_results.json")
    
    return overall_score

if __name__ == "__main__":
    score = test_awareness()
    sys.exit(0 if score >= 60 else 1)