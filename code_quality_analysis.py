#!/usr/bin/env python3
"""
Code Quality Analysis Tool
Analyzes Python files for quality and consistency improvements
"""
import os
import ast
import sys
sys.path.append('/mnt/host/c/CORA')

def analyze_code_quality():
    """Analyze code quality across Python files"""
    print("Code Quality Analysis")
    print("=" * 25)
    
    issues = []
    suggestions = []
    stats = {
        'files_analyzed': 0,
        'total_lines': 0,
        'import_issues': 0,
        'docstring_missing': 0,
        'long_functions': 0,
        'unused_imports': 0
    }
    
    # Key directories to analyze
    directories = [
        'routes',
        'models',
        'services',
        'middleware',
        'utils',
        'dependencies'
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            analyze_directory(directory, stats, issues, suggestions)
    
    # Analyze root Python files
    root_files = [f for f in os.listdir('.') if f.endswith('.py') and not f.startswith('test_')]
    for file in root_files:
        if os.path.isfile(file):
            analyze_file(file, stats, issues, suggestions)
    
    # Print results
    print(f"\nAnalysis Results:")
    print(f"  Files analyzed: {stats['files_analyzed']}")
    print(f"  Total lines: {stats['total_lines']:,}")
    print(f"  Import issues: {stats['import_issues']}")
    print(f"  Missing docstrings: {stats['docstring_missing']}")
    print(f"  Long functions: {stats['long_functions']}")
    
    if issues:
        print(f"\nIssues Found ({len(issues)}):")
        for issue in issues[:10]:  # Show first 10
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more issues")
    
    if suggestions:
        print(f"\nImprovement Suggestions ({len(suggestions)}):")
        for suggestion in suggestions[:5]:  # Show first 5
            print(f"  + {suggestion}")
        if len(suggestions) > 5:
            print(f"  ... and {len(suggestions) - 5} more suggestions")
    
    return stats, issues, suggestions

def analyze_directory(directory, stats, issues, suggestions):
    """Analyze all Python files in a directory"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('test_'):
                file_path = os.path.join(root, file)
                analyze_file(file_path, stats, issues, suggestions)

def analyze_file(file_path, stats, issues, suggestions):
    """Analyze a single Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        stats['files_analyzed'] += 1
        stats['total_lines'] += len(lines)
        
        # Parse AST for deeper analysis
        try:
            tree = ast.parse(content, filename=file_path)
            analyze_ast(tree, file_path, stats, issues, suggestions)
        except SyntaxError as e:
            issues.append(f"Syntax error in {file_path}: {e}")
        
        # Check imports organization
        import_lines = [line.strip() for line in lines if line.strip().startswith(('import ', 'from '))]
        if len(import_lines) > 10:
            stats['import_issues'] += 1
            suggestions.append(f"{file_path}: Consider organizing imports (found {len(import_lines)})")
        
        # Check for very long files
        if len(lines) > 1000:
            suggestions.append(f"{file_path}: Large file ({len(lines)} lines) - consider splitting")
            
    except Exception as e:
        issues.append(f"Error analyzing {file_path}: {e}")

def analyze_ast(tree, file_path, stats, issues, suggestions):
    """Analyze the AST of a Python file"""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check function length
            if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                func_length = node.end_lineno - node.lineno
                if func_length > 50:
                    stats['long_functions'] += 1
                    suggestions.append(f"{file_path}:{node.lineno} - Long function '{node.name}' ({func_length} lines)")
            
            # Check for missing docstrings
            if not ast.get_docstring(node):
                if not node.name.startswith('_'):  # Ignore private functions
                    stats['docstring_missing'] += 1
                    issues.append(f"{file_path}:{node.lineno} - Missing docstring for function '{node.name}'")
        
        elif isinstance(node, ast.ClassDef):
            # Check for missing class docstrings
            if not ast.get_docstring(node):
                stats['docstring_missing'] += 1
                issues.append(f"{file_path}:{node.lineno} - Missing docstring for class '{node.name}'")

if __name__ == "__main__":
    analyze_code_quality()