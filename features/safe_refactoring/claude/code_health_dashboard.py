#!/usr/bin/env python3
"""
Code Health Dashboard for CORA
Provides comprehensive metrics on code quality, consistency, and maintainability
Created: 2025-08-10 by Claude (Phase 16)
"""

import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import json

class CodeHealthAnalyzer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.metrics = {
            "files": {"total": 0, "python": 0, "javascript": 0, "html": 0, "css": 0},
            "lines": {"total": 0, "code": 0, "comments": 0, "blank": 0},
            "functions": {"total": 0, "documented": 0, "undocumented": 0},
            "imports": {"total": 0, "unused": 0, "duplicate": 0},
            "errors": {"hardcoded": 0, "standardized": 0, "inconsistent": 0},
            "todos": {"total": 0, "high_priority": 0, "low_priority": 0},
            "complexity": {"high": 0, "medium": 0, "low": 0},
            "test_coverage": {"files_with_tests": 0, "files_without_tests": 0},
            "documentation": {"readme_exists": False, "api_docs": False, "inline_comments_ratio": 0},
            "security": {"hardcoded_secrets": 0, "sql_injection_risks": 0, "unsafe_eval": 0}
        }
        self.issues = []
        self.recommendations = []
        
    def analyze_file(self, filepath: Path) -> Dict:
        """Analyze a single Python file for various metrics"""
        if not filepath.suffix == '.py':
            return {}
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        metrics = {
            "lines": len(lines),
            "blank_lines": sum(1 for line in lines if not line.strip()),
            "comment_lines": sum(1 for line in lines if line.strip().startswith('#')),
            "todos": len(re.findall(r'#\s*TODO', content, re.IGNORECASE)),
            "fixmes": len(re.findall(r'#\s*FIXME', content, re.IGNORECASE)),
            "imports": {"total": 0, "unused": []},
            "functions": {"total": 0, "documented": 0},
            "classes": {"total": 0, "documented": 0},
            "complexity": {"cyclomatic": 0, "nesting_depth": 0},
            "issues": []
        }
        
        try:
            tree = ast.parse(content)
            
            # Count imports and check usage
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.asname or alias.name.split('.')[0]
                        imports.add(name)
                        metrics["imports"]["total"] += 1
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        name = alias.asname or alias.name
                        imports.add(name)
                        metrics["imports"]["total"] += 1
            
            # Check for unused imports
            for imp in imports:
                if content.count(imp) <= 1:  # Only in import statement
                    metrics["imports"]["unused"].append(imp)
            
            # Count functions and check documentation
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics["functions"]["total"] += 1
                    if ast.get_docstring(node):
                        metrics["functions"]["documented"] += 1
                elif isinstance(node, ast.ClassDef):
                    metrics["classes"]["total"] += 1
                    if ast.get_docstring(node):
                        metrics["classes"]["documented"] += 1
            
            # Calculate cyclomatic complexity (simplified)
            complexity = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                    complexity += 1
            metrics["complexity"]["cyclomatic"] = complexity
            
            # Check for security issues
            if 'eval(' in content or 'exec(' in content:
                metrics["issues"].append("Unsafe eval/exec usage")
            if re.search(r'["\'].*password.*["\'].*=.*["\'][^"\']+["\']', content, re.IGNORECASE):
                metrics["issues"].append("Possible hardcoded password")
            if 'sql' in filepath.name.lower() and '%s' in content:
                metrics["issues"].append("Possible SQL injection risk")
                
        except SyntaxError:
            metrics["issues"].append("Syntax error in file")
            
        return metrics
    
    def analyze_directory(self, directory: Path) -> None:
        """Recursively analyze all Python files in directory"""
        for filepath in directory.rglob('*.py'):
            # Skip virtual environments and cache
            if any(skip in str(filepath) for skip in ['venv', '__pycache__', '.git', 'node_modules']):
                continue
                
            self.metrics["files"]["python"] += 1
            self.metrics["files"]["total"] += 1
            
            file_metrics = self.analyze_file(filepath)
            if file_metrics:
                self.metrics["lines"]["total"] += file_metrics["lines"]
                self.metrics["lines"]["blank"] += file_metrics["blank_lines"]
                self.metrics["lines"]["comments"] += file_metrics["comment_lines"]
                self.metrics["lines"]["code"] += (file_metrics["lines"] - 
                                                  file_metrics["blank_lines"] - 
                                                  file_metrics["comment_lines"])
                
                self.metrics["todos"]["total"] += file_metrics["todos"]
                self.metrics["todos"]["total"] += file_metrics["fixmes"]
                
                self.metrics["functions"]["total"] += file_metrics["functions"]["total"]
                self.metrics["functions"]["documented"] += file_metrics["functions"]["documented"]
                self.metrics["functions"]["undocumented"] += (file_metrics["functions"]["total"] - 
                                                              file_metrics["functions"]["documented"])
                
                self.metrics["imports"]["total"] += file_metrics["imports"]["total"]
                self.metrics["imports"]["unused"] += len(file_metrics["imports"]["unused"])
                
                # Categorize complexity
                if file_metrics["complexity"]["cyclomatic"] > 10:
                    self.metrics["complexity"]["high"] += 1
                elif file_metrics["complexity"]["cyclomatic"] > 5:
                    self.metrics["complexity"]["medium"] += 1
                else:
                    self.metrics["complexity"]["low"] += 1
                
                # Record issues
                for issue in file_metrics["issues"]:
                    self.issues.append(f"{filepath}: {issue}")
    
    def check_error_standardization(self) -> None:
        """Check how many errors are using standardized constants"""
        routes_dir = self.project_root / "routes"
        if not routes_dir.exists():
            return
            
        for filepath in routes_dir.glob("*.py"):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Count HTTPExceptions
            total_exceptions = len(re.findall(r'HTTPException\(', content))
            
            # Count standardized (using STATUS_ constants)
            standardized = len(re.findall(r'status_code=STATUS_', content))
            
            # Count hardcoded status codes
            hardcoded = len(re.findall(r'status_code=\d{3}', content))
            
            self.metrics["errors"]["hardcoded"] += hardcoded
            self.metrics["errors"]["standardized"] += standardized
            self.metrics["errors"]["inconsistent"] += max(0, total_exceptions - standardized - hardcoded)
    
    def check_test_coverage(self) -> None:
        """Check which files have corresponding test files"""
        test_dirs = ["tests", "test"]
        
        for test_dir_name in test_dirs:
            test_dir = self.project_root / test_dir_name
            if test_dir.exists():
                test_files = set(f.stem.replace('test_', '') for f in test_dir.glob('test_*.py'))
                
                for filepath in self.project_root.rglob('*.py'):
                    if any(skip in str(filepath) for skip in ['test', 'venv', '__pycache__']):
                        continue
                    
                    if filepath.stem in test_files or f"test_{filepath.stem}" in test_files:
                        self.metrics["test_coverage"]["files_with_tests"] += 1
                    else:
                        self.metrics["test_coverage"]["files_without_tests"] += 1
    
    def generate_recommendations(self) -> None:
        """Generate recommendations based on metrics"""
        # Documentation recommendations
        if self.metrics["functions"]["total"] > 0:
            doc_ratio = self.metrics["functions"]["documented"] / self.metrics["functions"]["total"]
            if doc_ratio < 0.5:
                self.recommendations.append({
                    "priority": "HIGH",
                    "category": "Documentation",
                    "issue": f"Only {doc_ratio*100:.1f}% of functions are documented",
                    "action": "Add docstrings to undocumented functions"
                })
        
        # Import hygiene
        if self.metrics["imports"]["unused"] > 20:
            self.recommendations.append({
                "priority": "MEDIUM",
                "category": "Code Cleanliness",
                "issue": f"{self.metrics['imports']['unused']} unused imports found",
                "action": "Remove unused imports to improve code clarity"
            })
        
        # Error standardization
        total_errors = (self.metrics["errors"]["hardcoded"] + 
                       self.metrics["errors"]["standardized"] + 
                       self.metrics["errors"]["inconsistent"])
        if total_errors > 0:
            standardized_ratio = self.metrics["errors"]["standardized"] / total_errors
            if standardized_ratio < 0.8:
                self.recommendations.append({
                    "priority": "MEDIUM",
                    "category": "Consistency",
                    "issue": f"Only {standardized_ratio*100:.1f}% of errors use standard constants",
                    "action": "Migrate remaining errors to use error_constants.py"
                })
        
        # TODO management
        if self.metrics["todos"]["total"] > 10:
            self.recommendations.append({
                "priority": "LOW",
                "category": "Technical Debt",
                "issue": f"{self.metrics['todos']['total']} TODOs/FIXMEs in codebase",
                "action": "Create tickets for TODOs and address them systematically"
            })
        
        # Complexity
        if self.metrics["complexity"]["high"] > 5:
            self.recommendations.append({
                "priority": "MEDIUM",
                "category": "Maintainability",
                "issue": f"{self.metrics['complexity']['high']} files have high complexity",
                "action": "Refactor complex functions to improve readability"
            })
        
        # Test coverage
        if self.metrics["test_coverage"]["files_with_tests"] > 0:
            test_ratio = (self.metrics["test_coverage"]["files_with_tests"] / 
                         (self.metrics["test_coverage"]["files_with_tests"] + 
                          self.metrics["test_coverage"]["files_without_tests"]))
            if test_ratio < 0.5:
                self.recommendations.append({
                    "priority": "HIGH",
                    "category": "Testing",
                    "issue": f"Only {test_ratio*100:.1f}% of files have tests",
                    "action": "Add tests for untested modules"
                })
    
    def generate_report(self) -> str:
        """Generate a comprehensive health report"""
        report = []
        report.append("=" * 60)
        report.append("       CORA CODE HEALTH DASHBOARD")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall Health Score
        health_score = self.calculate_health_score()
        report.append(f"OVERALL HEALTH SCORE: {health_score}/100")
        report.append(self.get_health_text(health_score))
        report.append("")
        
        # File Statistics
        report.append("FILE STATISTICS")
        report.append("-" * 40)
        report.append(f"Total Files: {self.metrics['files']['total']}")
        report.append(f"Python Files: {self.metrics['files']['python']}")
        report.append("")
        
        # Code Statistics
        report.append("CODE STATISTICS")
        report.append("-" * 40)
        report.append(f"Total Lines: {self.metrics['lines']['total']:,}")
        report.append(f"Code Lines: {self.metrics['lines']['code']:,}")
        report.append(f"Comment Lines: {self.metrics['lines']['comments']:,}")
        report.append(f"Blank Lines: {self.metrics['lines']['blank']:,}")
        if self.metrics['lines']['code'] > 0:
            comment_ratio = self.metrics['lines']['comments'] / self.metrics['lines']['code'] * 100
            report.append(f"Comment Ratio: {comment_ratio:.1f}%")
        report.append("")
        
        # Documentation
        report.append("DOCUMENTATION")
        report.append("-" * 40)
        report.append(f"Total Functions: {self.metrics['functions']['total']}")
        report.append(f"Documented: {self.metrics['functions']['documented']}")
        report.append(f"Undocumented: {self.metrics['functions']['undocumented']}")
        if self.metrics['functions']['total'] > 0:
            doc_coverage = self.metrics['functions']['documented'] / self.metrics['functions']['total'] * 100
            report.append(f"Documentation Coverage: {doc_coverage:.1f}%")
        report.append("")
        
        # Code Quality
        report.append("CODE QUALITY")
        report.append("-" * 40)
        report.append(f"Unused Imports: {self.metrics['imports']['unused']}")
        report.append(f"TODOs/FIXMEs: {self.metrics['todos']['total']}")
        report.append(f"High Complexity Files: {self.metrics['complexity']['high']}")
        report.append(f"Medium Complexity Files: {self.metrics['complexity']['medium']}")
        report.append(f"Low Complexity Files: {self.metrics['complexity']['low']}")
        report.append("")
        
        # Error Standardization
        report.append("ERROR HANDLING")
        report.append("-" * 40)
        report.append(f"Standardized Errors: {self.metrics['errors']['standardized']}")
        report.append(f"Hardcoded Status Codes: {self.metrics['errors']['hardcoded']}")
        report.append(f"Inconsistent Errors: {self.metrics['errors']['inconsistent']}")
        report.append("")
        
        # Test Coverage
        report.append("TEST COVERAGE")
        report.append("-" * 40)
        report.append(f"Files with Tests: {self.metrics['test_coverage']['files_with_tests']}")
        report.append(f"Files without Tests: {self.metrics['test_coverage']['files_without_tests']}")
        report.append("")
        
        # Top Issues
        if self.issues:
            report.append("TOP ISSUES")
            report.append("-" * 40)
            for issue in self.issues[:5]:
                report.append(f"- {issue}")
            if len(self.issues) > 5:
                report.append(f"  ... and {len(self.issues) - 5} more")
            report.append("")
        
        # Recommendations
        if self.recommendations:
            report.append("RECOMMENDATIONS")
            report.append("-" * 40)
            for rec in sorted(self.recommendations, key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[x["priority"]]):
                report.append(f"[{rec['priority']}] {rec['category']}")
                report.append(f"  Issue: {rec['issue']}")
                report.append(f"  Action: {rec['action']}")
                report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def calculate_health_score(self) -> int:
        """Calculate overall health score (0-100)"""
        score = 100
        
        # Documentation penalty (max -20)
        if self.metrics['functions']['total'] > 0:
            doc_ratio = self.metrics['functions']['documented'] / self.metrics['functions']['total']
            score -= int((1 - doc_ratio) * 20)
        
        # Unused imports penalty (max -10)
        if self.metrics['imports']['total'] > 0:
            unused_ratio = self.metrics['imports']['unused'] / self.metrics['imports']['total']
            score -= int(unused_ratio * 10)
        
        # TODOs penalty (max -10)
        todo_penalty = min(self.metrics['todos']['total'], 10)
        score -= todo_penalty
        
        # Complexity penalty (max -15)
        complexity_penalty = min(self.metrics['complexity']['high'] * 3, 15)
        score -= complexity_penalty
        
        # Error standardization bonus (max +10)
        total_errors = (self.metrics["errors"]["hardcoded"] + 
                       self.metrics["errors"]["standardized"] + 
                       self.metrics["errors"]["inconsistent"])
        if total_errors > 0:
            standardized_ratio = self.metrics["errors"]["standardized"] / total_errors
            score += int(standardized_ratio * 10)
        
        return max(0, min(100, score))
    
    def get_health_text(self, score: int) -> str:
        """Get text representation of health score"""
        if score >= 90:
            return "[EXCELLENT] Code is in great shape!"
        elif score >= 75:
            return "[GOOD] Some improvements recommended"
        elif score >= 60:
            return "[FAIR] Significant improvements needed"
        else:
            return "[POOR] Major refactoring recommended"
    
    def run_analysis(self) -> str:
        """Run complete analysis and return report"""
        print("Analyzing codebase...")
        
        # Analyze main directories
        for directory in ['routes', 'models', 'services', 'utils', 'features']:
            dir_path = self.project_root / directory
            if dir_path.exists():
                print(f"  Analyzing {directory}/...")
                self.analyze_directory(dir_path)
        
        # Additional checks
        print("  Checking error standardization...")
        self.check_error_standardization()
        
        print("  Checking test coverage...")
        self.check_test_coverage()
        
        print("  Generating recommendations...")
        self.generate_recommendations()
        
        return self.generate_report()
    
    def save_metrics(self, filepath: str = "code_health_metrics.json") -> None:
        """Save metrics to JSON file for tracking over time"""
        metrics_with_timestamp = {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics,
            "health_score": self.calculate_health_score(),
            "issues_count": len(self.issues),
            "recommendations_count": len(self.recommendations)
        }
        
        # Load existing metrics if file exists
        metrics_history = []
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                metrics_history = json.load(f)
        
        # Add new metrics
        metrics_history.append(metrics_with_timestamp)
        
        # Keep only last 30 entries
        metrics_history = metrics_history[-30:]
        
        # Save updated metrics
        with open(filepath, 'w') as f:
            json.dump(metrics_history, f, indent=2)
        
        print(f"Metrics saved to {filepath}")


if __name__ == "__main__":
    # Run analysis from CORA root
    analyzer = CodeHealthAnalyzer(".")
    report = analyzer.run_analysis()
    print(report)
    
    # Save metrics for tracking
    analyzer.save_metrics("features/safe_refactoring/claude/health_metrics.json")
    
    # Save report to file
    with open("features/safe_refactoring/claude/health_report.txt", "w") as f:
        f.write(report)
    print("\nReport saved to health_report.txt")