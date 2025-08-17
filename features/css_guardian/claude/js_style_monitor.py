#!/usr/bin/env python3
"""
JavaScript Style Monitor
Detects JS files that modify styles, especially root font-size
"""

import os
import re
from pathlib import Path
from typing import List, Dict

class JSStyleMonitor:
    def __init__(self):
        self.dangerous_patterns = [
            # Root font-size modifications (the navbar killer)
            (r'document\.documentElement\.style\.fontSize', 'CRITICAL: Modifies root font-size (affects all rem units)'),
            (r'document\.body\.style\.fontSize', 'HIGH: Modifies body font-size'),
            
            # Direct style modifications
            (r'\.style\.fontSize\s*=', 'MEDIUM: Direct font-size modification'),
            (r'\.style\.font\s*=', 'MEDIUM: Direct font modification'),
            
            # Navigation specific
            (r'\.navbar.*\.style', 'HIGH: Modifies navbar styles'),
            (r'\.nav-link.*\.style', 'HIGH: Modifies nav-link styles'),
            
            # Global style changes
            (r'document\.styleSheets', 'MEDIUM: Accesses stylesheets directly'),
            (r'insertRule|addRule', 'MEDIUM: Adds CSS rules dynamically'),
            
            # jQuery style changes
            (r'\.css\(["\']fontSize', 'MEDIUM: jQuery font-size change'),
        ]
        
        self.findings = []
    
    def scan_js_files(self, js_dir="web/static/js"):
        """Scan all JS files for style modifications"""
        js_files = list(Path(js_dir).rglob("*.js"))
        
        for js_file in js_files:
            self._scan_file(js_file)
        
        return self._generate_report()
    
    def _scan_file(self, js_file: Path):
        """Scan a single JS file for dangerous patterns"""
        try:
            content = js_file.read_text(encoding='utf-8', errors='ignore')
            
            for pattern, severity in self.dangerous_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    context = self._get_context(content, match.start())
                    
                    self.findings.append({
                        'file': str(js_file),
                        'line': line_num,
                        'severity': severity,
                        'pattern': pattern,
                        'context': context
                    })
        except Exception as e:
            print(f"Error scanning {js_file}: {e}")
    
    def _get_context(self, content: str, position: int, context_chars: int = 50) -> str:
        """Get surrounding context for a match"""
        start = max(0, position - context_chars)
        end = min(len(content), position + context_chars)
        context = content[start:end].replace('\n', ' ')
        return f"...{context}..."
    
    def _generate_report(self) -> Dict:
        """Generate monitoring report"""
        # Group by severity
        critical = [f for f in self.findings if 'CRITICAL' in f['severity']]
        high = [f for f in self.findings if 'HIGH' in f['severity']]
        medium = [f for f in self.findings if 'MEDIUM' in f['severity']]
        
        return {
            'summary': {
                'total_issues': len(self.findings),
                'critical': len(critical),
                'high': len(high),
                'medium': len(medium)
            },
            'critical': critical,
            'high': high,
            'medium': medium
        }
    
    def print_report(self, report: Dict):
        """Print human-readable report"""
        print("\n" + "="*60)
        print("JAVASCRIPT STYLE MODIFICATION REPORT")
        print("="*60)
        
        summary = report['summary']
        print(f"\nTotal Issues: {summary['total_issues']}")
        print(f"  Critical: {summary['critical']} (affects all rem units)")
        print(f"  High: {summary['high']} (affects navigation)")
        print(f"  Medium: {summary['medium']} (other style changes)")
        
        if report['critical']:
            print("\n[CRITICAL] ISSUES (These caused the navbar incident!):")
            for finding in report['critical']:
                print(f"\n  File: {finding['file']}:{finding['line']}")
                print(f"  Issue: {finding['severity']}")
                print(f"  Context: {finding['context']}")
        
        if report['high']:
            print("\n[HIGH] PRIORITY ISSUES:")
            for finding in report['high'][:3]:  # Show first 3
                print(f"\n  File: {finding['file']}:{finding['line']}")
                print(f"  Issue: {finding['severity']}")
        
        if report['medium']:
            print(f"\n[MEDIUM] PRIORITY: {len(report['medium'])} style modifications found")
        
        print("\n" + "="*60)
        
        if report['critical']:
            print("\n[ACTION] CRITICAL RESOLUTION REQUIRED:")
            print("1. Files modifying root font-size affect ALL rem units")
            print("2. Consider using scoped modifications instead")
            print("3. Or switch critical UI to px units (navbar, footer)")
        
        return summary['critical'] == 0


def main():
    monitor = JSStyleMonitor()
    report = monitor.scan_js_files()
    monitor.print_report(report)
    
    # Exit with error if critical issues found
    exit(0 if report['summary']['critical'] == 0 else 1)


if __name__ == "__main__":
    main()