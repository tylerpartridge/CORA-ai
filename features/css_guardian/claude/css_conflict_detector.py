#!/usr/bin/env python3
"""
CSS Conflict Detector
Prevents the navbar font incident from ever happening again
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class CSSConflictDetector:
    def __init__(self, ownership_file="css_ownership.json"):
        # Load ownership rules
        ownership_path = Path(__file__).parent / ownership_file
        with open(ownership_path) as f:
            self.ownership = json.load(f)
        
        self.violations = []
        self.conflicts = []
        self.rem_issues = []
        
    def scan_css_files(self, css_dir="/mnt/host/c/CORA/web/static/css"):
        """Scan all CSS files for conflicts and violations"""
        css_files = list(Path(css_dir).rglob("*.css"))
        
        # Build selector map
        selector_map = defaultdict(list)  # selector -> [(file, line_num)]
        
        for css_file in css_files:
            if self._is_deprecated(str(css_file)):
                continue
                
            self._scan_file(css_file, selector_map)
        
        # Check for conflicts
        self._detect_conflicts(selector_map)
        
        # Check ownership violations
        self._check_ownership_violations(selector_map)
        
        # Check rem usage in critical components
        self._check_rem_usage(css_files)
        
        return self._generate_report()
    
    def _scan_file(self, css_file: Path, selector_map: Dict):
        """Scan a single CSS file for selectors"""
        try:
            content = css_file.read_text()
            
            # Find all CSS selectors (simplified regex)
            selector_pattern = r'([.#]?[\w-]+(?:\s*[.#]?[\w-]+)*)\s*\{'
            
            for match in re.finditer(selector_pattern, content):
                selector = match.group(1).strip()
                line_num = content[:match.start()].count('\n') + 1
                selector_map[selector].append((str(css_file), line_num))
                
        except Exception as e:
            print(f"Error scanning {css_file}: {e}")
    
    def _detect_conflicts(self, selector_map: Dict):
        """Find selectors defined in multiple files"""
        for selector, locations in selector_map.items():
            if len(locations) > 1:
                # Check if this is a protected selector
                for component, rules in self.ownership["ownership_rules"].items():
                    if selector in rules["selectors"]:
                        # This is a protected selector with multiple definitions!
                        self.conflicts.append({
                            "selector": selector,
                            "component": component,
                            "authoritative": rules["authoritative_file"],
                            "found_in": locations
                        })
                        break
    
    def _check_ownership_violations(self, selector_map: Dict):
        """Check if protected selectors appear in wrong files"""
        for component, rules in self.ownership["ownership_rules"].items():
            auth_file = rules["authoritative_file"]
            
            for selector in rules["selectors"]:
                if selector in selector_map:
                    for file_path, line_num in selector_map[selector]:
                        # Normalize paths for comparison
                        if not file_path.endswith(auth_file.split('/')[-1]):
                            self.violations.append({
                                "component": component,
                                "selector": selector,
                                "should_be_in": auth_file,
                                "found_in": file_path,
                                "line": line_num
                            })
    
    def _check_rem_usage(self, css_files: List[Path]):
        """Check for rem units in critical components"""
        critical_components = self.ownership["global_rules"]["require_px_units"]
        
        for css_file in css_files:
            try:
                content = css_file.read_text()
                filename = css_file.name
                
                # Check if this is a critical component file
                for component in critical_components:
                    if component in filename:
                        # Look for rem units
                        rem_pattern = r'(\d+(?:\.\d+)?rem)'
                        for match in re.finditer(rem_pattern, content):
                            line_num = content[:match.start()].count('\n') + 1
                            self.rem_issues.append({
                                "file": str(css_file),
                                "component": component,
                                "value": match.group(1),
                                "line": line_num
                            })
            except Exception as e:
                print(f"Error checking rem usage in {css_file}: {e}")
    
    def _is_deprecated(self, file_path: str) -> bool:
        """Check if file is deprecated"""
        deprecated = self.ownership["global_rules"]["deprecated_files"]
        return any(dep in file_path for dep in deprecated)
    
    def _generate_report(self) -> Dict:
        """Generate conflict report"""
        report = {
            "summary": {
                "conflicts": len(self.conflicts),
                "violations": len(self.violations),
                "rem_issues": len(self.rem_issues),
                "status": "PASS" if not (self.conflicts or self.violations or self.rem_issues) else "FAIL"
            },
            "conflicts": self.conflicts,
            "violations": self.violations,
            "rem_issues": self.rem_issues
        }
        
        return report
    
    def print_report(self, report: Dict):
        """Print human-readable report"""
        print("\n" + "="*60)
        print("CSS CONFLICT DETECTION REPORT")
        print("="*60)
        
        status = report["summary"]["status"]
        if status == "PASS":
            print("✅ NO CSS CONFLICTS DETECTED")
        else:
            print("❌ CSS ISSUES FOUND")
        
        print(f"\nSummary:")
        print(f"  Conflicts: {report['summary']['conflicts']}")
        print(f"  Violations: {report['summary']['violations']}")
        print(f"  REM Issues: {report['summary']['rem_issues']}")
        
        if report["conflicts"]:
            print("\n🔴 CONFLICTS (same selector in multiple files):")
            for conflict in report["conflicts"]:
                print(f"\n  Selector: {conflict['selector']}")
                print(f"  Component: {conflict['component']}")
                print(f"  Should be in: {conflict['authoritative']}")
                print(f"  Found in:")
                for file_path, line in conflict["found_in"]:
                    print(f"    - {file_path}:{line}")
        
        if report["violations"]:
            print("\n🟡 OWNERSHIP VIOLATIONS:")
            for violation in report["violations"]:
                print(f"\n  Component: {violation['component']}")
                print(f"  Selector: {violation['selector']}")
                print(f"  Should be in: {violation['should_be_in']}")
                print(f"  Found in: {violation['found_in']}:{violation['line']}")
        
        if report["rem_issues"]:
            print("\n⚠️ REM UNITS IN CRITICAL COMPONENTS:")
            for issue in report["rem_issues"]:
                print(f"\n  Component: {issue['component']}")
                print(f"  File: {issue['file']}:{issue['line']}")
                print(f"  Value: {issue['value']} (should be px)")
        
        print("\n" + "="*60)
        
        if status == "FAIL":
            print("\n📋 RESOLUTION STEPS:")
            print("1. Move selectors to their authoritative files")
            print("2. Convert rem to px in critical components")
            print("3. Remove duplicate selector definitions")
            print("4. Run this script again to verify")
        
        return status == "PASS"


def main():
    """Run CSS conflict detection"""
    detector = CSSConflictDetector()
    report = detector.scan_css_files()
    
    # Save report
    report_path = Path(__file__).parent / "css_conflict_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print report
    success = detector.print_report(report)
    
    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == "__main__":
    main()