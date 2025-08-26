#!/usr/bin/env python3
"""
Import Optimization Tool
Identifies unused imports and organizes import statements
"""
import os
import ast
import sys
sys.path.append('/mnt/host/c/CORA')

def find_unused_imports():
    """Find unused imports across Python files"""
    print("Import Analysis")
    print("=" * 20)
    
    unused_imports = []
    duplicate_imports = []
    files_analyzed = 0
    
    # Key directories to analyze
    directories = ['routes', 'models', 'services', 'middleware', 'utils']
    
    for directory in directories:
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py') and not file.startswith('test_'):
                        file_path = os.path.join(root, file)
                        analyze_imports(file_path, unused_imports, duplicate_imports)
                        files_analyzed += 1
    
    # Print results
    print(f"\nFiles analyzed: {files_analyzed}")
    
    if unused_imports:
        print(f"\nPotentially Unused Imports ({len(unused_imports)}):")
        for item in unused_imports[:10]:
            print(f"  - {item}")
        if len(unused_imports) > 10:
            print(f"  ... and {len(unused_imports) - 10} more")
    
    if duplicate_imports:
        print(f"\nDuplicate/Similar Imports ({len(duplicate_imports)}):")
        for item in duplicate_imports[:5]:
            print(f"  - {item}")
    
    return unused_imports, duplicate_imports

def analyze_imports(file_path, unused_imports, duplicate_imports):
    """Analyze imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST
        tree = ast.parse(content, filename=file_path)
        
        imports = []
        names_used = set()
        
        # Collect all imports and names used
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_name = alias.asname or alias.name
                    imports.append((file_path, alias.name, import_name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    import_name = alias.asname or alias.name
                    full_name = f"{node.module}.{alias.name}" if node.module else alias.name
                    imports.append((file_path, full_name, import_name, node.lineno))
            elif isinstance(node, ast.Name):
                names_used.add(node.id)
            elif isinstance(node, ast.Attribute):
                names_used.add(node.attr)
        
        # Check for unused imports (basic check)
        for file_path_imp, full_name, import_name, lineno in imports:
            # Skip certain imports that might be used implicitly
            if import_name in ['logging', 'os', 're', 'sys', 'json']:
                continue
                
            # Simple check - if import name not found in names_used
            if import_name not in names_used and not any(name.startswith(import_name + '.') for name in names_used):
                # Double check by looking at the actual content
                if import_name not in content:
                    unused_imports.append(f"{file_path}:{lineno} - {full_name}")
        
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")

if __name__ == "__main__":
    find_unused_imports()