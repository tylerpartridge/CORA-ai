#!/usr/bin/env python3
"""
Intelligent Import Cleaner for CORA
Safely removes unused imports while preserving type hints and special cases
Created: 2025-08-10 by Claude (Phase 17)
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Set, Tuple, Dict
import shutil
from datetime import datetime

class ImportCleaner:
    def __init__(self, backup_dir: str = "archived_imports"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "imports_removed": 0,
            "errors": 0,
            "skipped_files": []
        }
        
        # Special imports that should never be removed
        self.protected_imports = {
            'typing',  # Often used in type hints that AST doesn't catch
            '__future__',  # Future imports affect parsing
            'annotations',  # Used for forward references
        }
        
        # Imports that may have side effects
        self.side_effect_imports = {
            'matplotlib',  # Sets backend on import
            'dotenv',  # load_dotenv() often called
            'uvloop',  # Changes event loop
            'eventlet',  # Monkey patches
        }
    
    def backup_file(self, filepath: Path) -> Path:
        """Create a backup of the file before modification"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{filepath.stem}_{timestamp}.py"
        shutil.copy2(filepath, backup_path)
        return backup_path
    
    def get_all_names_in_code(self, content: str) -> Set[str]:
        """Get all names used in the code (not just AST names)"""
        names = set()
        
        # Remove comments and strings to avoid false positives
        content_cleaned = re.sub(r'#.*$', '', content, flags=re.MULTILINE)
        content_cleaned = re.sub(r'""".*?"""', '', content_cleaned, flags=re.DOTALL)
        content_cleaned = re.sub(r"'''.*?'''", '', content_cleaned, flags=re.DOTALL)
        content_cleaned = re.sub(r'".*?"', '', content_cleaned)
        content_cleaned = re.sub(r"'.*?'", '', content_cleaned)
        
        # Find all word-like tokens
        tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', content_cleaned)
        names.update(tokens)
        
        # Also check for names in type hints (string form)
        type_hints = re.findall(r':\s*["\']([^"\']+)["\']', content)
        for hint in type_hints:
            names.update(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', hint))
        
        return names
    
    def analyze_imports(self, filepath: Path) -> Tuple[List[str], List[str]]:
        """Analyze a file and return (used_imports, unused_imports)"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST
            tree = ast.parse(content)
            
            # Collect all imports
            imports = {}  # name -> (module, line_number, is_from_import)
            
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.asname or alias.name
                        base_name = name.split('.')[0]
                        imports[base_name] = (alias.name, node.lineno, False)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for alias in node.names:
                            name = alias.asname or alias.name
                            if name == '*':
                                # Skip star imports - too risky to remove
                                continue
                            imports[name] = (node.module, node.lineno, True)
            
            # Get all names used in the code
            all_names = self.get_all_names_in_code(content)
            
            # Check which imports are unused
            unused = []
            used = []
            
            for import_name, (module, line, is_from) in imports.items():
                # Check if it's protected
                if import_name in self.protected_imports or module in self.protected_imports:
                    used.append(import_name)
                    continue
                
                # Check for side effects
                if import_name in self.side_effect_imports or module in self.side_effect_imports:
                    used.append(import_name)
                    continue
                
                # Check if it's used anywhere in the file
                # We need to be careful with module imports vs from imports
                if import_name in all_names:
                    # Check if it appears outside the import line
                    import_line_content = content.split('\n')[line - 1] if line <= len(content.split('\n')) else ""
                    
                    # Count occurrences excluding the import line
                    content_without_import = content.replace(import_line_content, '')
                    
                    if import_name in content_without_import:
                        used.append(import_name)
                    else:
                        unused.append(import_name)
                else:
                    unused.append(import_name)
            
            return used, unused
            
        except Exception as e:
            print(f"Error analyzing {filepath}: {e}")
            return [], []
    
    def clean_imports(self, filepath: Path, dry_run: bool = False) -> bool:
        """Remove unused imports from a file"""
        try:
            used, unused = self.analyze_imports(filepath)
            
            if not unused:
                return False
            
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if dry_run:
                print(f"\n{filepath.name}: Would remove {len(unused)} imports: {', '.join(unused)}")
                return False
            
            # Backup the file
            backup_path = self.backup_file(filepath)
            
            # Process lines and remove unused imports
            new_lines = []
            removed_count = 0
            
            for line in lines:
                should_keep = True
                
                # Check if this line contains an unused import
                for unused_import in unused:
                    # Check various import patterns
                    patterns = [
                        f'import {unused_import}\\b',  # import unused
                        f'import .* as {unused_import}\\b',  # import x as unused
                        f'from .* import .* {unused_import}',  # from x import unused
                        f'from .* import {unused_import}\\b',  # from x import unused
                        f'\\b{unused_import}\\s*,',  # unused,
                        f',\\s*{unused_import}\\b',  # , unused
                        f'\\b{unused_import}\\s*$',  # unused (end of line)
                    ]
                    
                    for pattern in patterns:
                        if re.search(pattern, line):
                            # For multi-import lines, just remove the specific import
                            if ',' in line and ('from' in line or 'import' in line):
                                # Remove just this import from the line
                                new_line = re.sub(f'\\b{unused_import}\\s*,\\s*', '', line)
                                new_line = re.sub(f',\\s*{unused_import}\\b', '', new_line)
                                new_line = re.sub(f'\\b{unused_import}\\b', '', new_line)
                                
                                # Clean up any double commas or trailing commas
                                new_line = re.sub(r',\s*,', ',', new_line)
                                new_line = re.sub(r',\s*\)', ')', new_line)
                                
                                # Check if the line is now empty (only had this import)
                                if re.match(r'^(from\s+\S+\s+)?import\s*$', new_line.strip()):
                                    should_keep = False
                                else:
                                    line = new_line
                                    removed_count += 1
                            else:
                                # Single import line - remove entire line
                                should_keep = False
                                removed_count += 1
                            break
                
                if should_keep:
                    new_lines.append(line)
            
            # Write the cleaned content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            self.stats["imports_removed"] += removed_count
            self.stats["files_modified"] += 1
            
            print(f"[OK] {filepath.name}: Removed {removed_count} imports (backup: {backup_path.name})")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error cleaning {filepath}: {e}")
            self.stats["errors"] += 1
            self.stats["skipped_files"].append(str(filepath))
            return False
    
    def clean_directory(self, directory: Path, pattern: str = "*.py", dry_run: bool = False) -> None:
        """Clean all Python files in a directory"""
        print(f"\nCleaning {directory}...")
        
        for filepath in directory.glob(pattern):
            # Skip test files and other special files
            if any(skip in filepath.name for skip in ['__pycache__', 'test_', '_test.py']):
                continue
            
            self.stats["files_processed"] += 1
            self.clean_imports(filepath, dry_run)
    
    def clean_project(self, project_root: Path, dry_run: bool = False, directories: List[str] = None) -> None:
        """Clean the entire project"""
        if directories is None:
            directories = ['routes', 'models', 'services', 'utils', 'features/safe_refactoring/claude']
        
        print("=" * 60)
        print("IMPORT CLEANUP TOOL")
        print("=" * 60)
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE CLEANUP'}")
        print(f"Backup directory: {self.backup_dir}")
        print("")
        
        for dir_name in directories:
            dir_path = project_root / dir_name
            if dir_path.exists():
                self.clean_directory(dir_path, dry_run=dry_run)
        
        # Print summary
        print("\n" + "=" * 60)
        print("CLEANUP SUMMARY")
        print("=" * 60)
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Files modified: {self.stats['files_modified']}")
        print(f"Imports removed: {self.stats['imports_removed']}")
        print(f"Errors: {self.stats['errors']}")
        
        if self.stats['skipped_files']:
            print(f"\nSkipped files due to errors:")
            for file in self.stats['skipped_files']:
                print(f"  - {file}")
    
    def verify_file(self, filepath: Path) -> bool:
        """Verify a file still has valid syntax after cleaning"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse it
            ast.parse(content)
            return True
        except SyntaxError as e:
            print(f"[ERROR] Syntax error in {filepath}: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] Error verifying {filepath}: {e}")
            return False
    
    def restore_file(self, filepath: Path, backup_path: Path) -> None:
        """Restore a file from backup if something went wrong"""
        shutil.copy2(backup_path, filepath)
        print(f"Restored {filepath} from backup")


if __name__ == "__main__":
    import sys
    
    # Check for dry run mode
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    
    # Create cleaner
    cleaner = ImportCleaner(backup_dir="features/safe_refactoring/claude/archived_imports")
    
    # Run cleanup
    project_root = Path(".")
    
    if dry_run:
        print("Running in DRY RUN mode - no files will be modified\n")
        cleaner.clean_project(project_root, dry_run=True)
    else:
        print("Running in LIVE mode - files will be modified\n")
        print("Auto-proceeding with cleanup...")
        cleaner.clean_project(project_root, dry_run=False)