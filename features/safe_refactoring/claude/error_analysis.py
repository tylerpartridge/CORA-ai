#!/usr/bin/env python3
"""
Analyze error messages across the codebase
Find inconsistencies and patterns
"""

import re
from pathlib import Path
from collections import Counter, defaultdict

def analyze_error_messages(directory="routes"):
    """Find all HTTPException error messages"""
    error_patterns = defaultdict(list)
    status_codes = Counter()
    
    pattern = re.compile(r'HTTPException\([^)]*status_code=(\d+)[^)]*detail="([^"]*)"')
    
    for file_path in Path(directory).glob("*.py"):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            matches = pattern.findall(content)
            for status_code, message in matches:
                status_codes[status_code] += 1
                error_patterns[status_code].append({
                    'file': file_path.name,
                    'message': message
                })
    
    return error_patterns, status_codes

def find_similar_messages(error_patterns):
    """Find similar error messages that could be standardized"""
    similar_groups = []
    
    # Group by status code
    for status_code, errors in error_patterns.items():
        messages = [e['message'] for e in errors]
        
        # Find variations
        if status_code == '404':
            not_found_variations = [m for m in messages if 'not found' in m.lower()]
            if len(not_found_variations) > 1:
                similar_groups.append({
                    'type': '404 Not Found',
                    'variations': not_found_variations,
                    'count': len(not_found_variations)
                })
        
        if status_code == '500':
            failed_variations = [m for m in messages if 'failed' in m.lower()]
            if len(failed_variations) > 1:
                similar_groups.append({
                    'type': '500 Server Error',
                    'variations': failed_variations,
                    'count': len(failed_variations)
                })
    
    return similar_groups

def generate_report():
    """Generate error message analysis report"""
    error_patterns, status_codes = analyze_error_messages()
    similar = find_similar_messages(error_patterns)
    
    report = """# Error Message Analysis Report

## Status Code Distribution
"""
    for code, count in sorted(status_codes.items()):
        report += f"- {code}: {count} occurrences\n"
    
    report += "\n## Error Messages by Status Code\n"
    
    for status_code in ['400', '401', '403', '404', '500']:
        if status_code in error_patterns:
            report += f"\n### {status_code} Errors\n"
            seen = set()
            for error in error_patterns[status_code]:
                msg = error['message']
                if msg not in seen:
                    report += f"- \"{msg}\" ({error['file']})\n"
                    seen.add(msg)
    
    report += "\n## Standardization Opportunities\n"
    if similar:
        for group in similar:
            report += f"\n### {group['type']} ({group['count']} variations)\n"
            for variation in set(group['variations']):
                report += f"- \"{variation}\"\n"
    else:
        report += "All error messages appear consistent.\n"
    
    return report

if __name__ == "__main__":
    print(generate_report())