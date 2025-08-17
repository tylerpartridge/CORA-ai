#!/usr/bin/env python3
"""
CORA Safe Cleanup Script - Phase 1
Purpose: Safely organize files without breaking functionality
Author: Claude (Opus 4.1)
Date: 2025-08-10
WARNING: Run with DRY_RUN=True first to preview changes

This script will:
1. Organize markdown files from root into /docs
2. Consolidate archive directories
3. Remove known orphaned files
4. Create proper directory structure
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import json

# SAFETY FIRST - Set to False to actually execute
DRY_RUN = False

# Files to keep in root (DO NOT MOVE)
KEEP_IN_ROOT = {
    'bootup.md',
    'PRIORITY.md', 
    'HOW_WE_WORK.md',
    'SYSTEM_RULES.md',
    'QUICK_REFERENCE.md',
    'HANDOFF.md',  # Current handoff stays in root
    'README.md',
    'CLAUDE.md'
}

class SafeCleanup:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.changes = []
        self.errors = []
        self.base_path = Path.cwd()
        
    def log_change(self, action, source, destination=None):
        """Log all changes for review"""
        change = {
            'action': action,
            'source': str(source),
            'destination': str(destination) if destination else None,
            'timestamp': datetime.now().isoformat()
        }
        self.changes.append(change)
        print(f"{'[DRY RUN] ' if self.dry_run else ''}[{action}] {source} → {destination if destination else 'removed'}")
        
    def create_directory_structure(self):
        """Create organized directory structure"""
        directories = [
            'docs/handoffs',
            'docs/ai-logs', 
            'docs/system',
            'docs/archive',
            'docs/features',
            'docs/reports',
            'features/system_optimization/claude'
        ]
        
        for dir_path in directories:
            full_path = self.base_path / dir_path
            if not full_path.exists():
                if not self.dry_run:
                    full_path.mkdir(parents=True, exist_ok=True)
                self.log_change('CREATE_DIR', dir_path)
                
    def organize_root_markdown(self):
        """Move markdown files from root to appropriate directories"""
        root_files = list(self.base_path.glob('*.md'))
        
        for file_path in root_files:
            filename = file_path.name
            
            # Skip protected files
            if filename in KEEP_IN_ROOT:
                print(f"[KEEP] {filename} - protected file")
                continue
                
            # Determine destination based on filename patterns
            if 'HANDOFF' in filename and filename != 'HANDOFF.md':
                dest_dir = 'docs/handoffs'
            elif filename.startswith('AI_'):
                dest_dir = 'docs/ai-logs'
            elif filename.startswith('SYSTEM_') or filename.startswith('CORA_'):
                dest_dir = 'docs/system'
            elif 'ARCHIVE' in filename:
                dest_dir = 'docs/archive'
            elif 'REPORT' in filename or 'ANALYSIS' in filename:
                dest_dir = 'docs/reports'
            elif filename.startswith('FEATURE_') or filename.startswith('CAPABILITY'):
                dest_dir = 'docs/features'
            else:
                dest_dir = 'docs/system'  # Default location
                
            dest_path = self.base_path / dest_dir / filename
            
            if not self.dry_run:
                # Create destination directory if needed
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                # Copy first (safer than move)
                shutil.copy2(file_path, dest_path)
                # Verify copy succeeded before removing
                if dest_path.exists():
                    file_path.unlink()
                    
            self.log_change('MOVE', file_path, dest_path)
            
    def consolidate_archives(self):
        """Consolidate multiple archive directories"""
        archive_dirs = ['archive', 'archives', '_archived', 'archived']
        consolidated_path = self.base_path / 'archives' / 'consolidated'
        
        for dir_name in archive_dirs:
            dir_path = self.base_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                if not self.dry_run:
                    consolidated_path.mkdir(parents=True, exist_ok=True)
                    # Copy contents
                    for item in dir_path.iterdir():
                        dest = consolidated_path / item.name
                        if item.is_dir():
                            shutil.copytree(item, dest, dirs_exist_ok=True)
                        else:
                            shutil.copy2(item, dest)
                            
                self.log_change('CONSOLIDATE', dir_path, consolidated_path)
                
    def remove_orphaned_static(self):
        """Remove known orphaned static files"""
        orphaned_paths = [
            'web/static/_archived',
            'web/static/css/_archived',
            'web/static/js/_archived'
        ]
        
        for path_str in orphaned_paths:
            path = self.base_path / path_str
            if path.exists():
                if not self.dry_run:
                    shutil.rmtree(path)
                self.log_change('REMOVE', path)
                
    def cleanup_duplicate_requirements(self):
        """Find and report duplicate requirements files"""
        req_files = list(self.base_path.rglob('requirements*.txt'))
        
        if len(req_files) > 1:
            print(f"\n[WARNING] Found {len(req_files)} requirements files:")
            for req_file in req_files:
                rel_path = req_file.relative_to(self.base_path)
                print(f"  - {rel_path}")
            print("  Recommendation: Keep only root requirements.txt")
            
    def generate_report(self):
        """Generate cleanup report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'dry_run': self.dry_run,
            'total_changes': len(self.changes),
            'changes': self.changes,
            'errors': self.errors
        }
        
        report_path = self.base_path / 'features' / 'system_optimization' / 'claude' / 'cleanup_report.json'
        
        if not self.dry_run:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
                
        print(f"\n{'='*60}")
        print(f"CLEANUP {'PREVIEW' if self.dry_run else 'COMPLETE'}")
        print(f"{'='*60}")
        print(f"Total changes: {len(self.changes)}")
        print(f"Errors: {len(self.errors)}")
        
        if self.dry_run:
            print("\n[INFO] This was a DRY RUN. No files were actually modified.")
            print("Set DRY_RUN=False to execute these changes.")
            
    def run(self):
        """Execute safe cleanup"""
        print(f"{'='*60}")
        print(f"CORA SAFE CLEANUP - {'DRY RUN' if self.dry_run else 'EXECUTING'}")
        print(f"{'='*60}\n")
        
        try:
            # Phase 1: Create structure
            print("[Phase 1] Creating directory structure...")
            self.create_directory_structure()
            
            # Phase 2: Organize markdown
            print("\n[Phase 2] Organizing root markdown files...")
            self.organize_root_markdown()
            
            # Phase 3: Consolidate archives
            print("\n[Phase 3] Consolidating archive directories...")
            self.consolidate_archives()
            
            # Phase 4: Remove orphaned files
            print("\n[Phase 4] Removing orphaned static files...")
            self.remove_orphaned_static()
            
            # Phase 5: Check for duplicates
            print("\n[Phase 5] Checking for duplicate files...")
            self.cleanup_duplicate_requirements()
            
        except Exception as e:
            self.errors.append(str(e))
            print(f"[ERROR] {e}")
            
        # Generate report
        self.generate_report()


if __name__ == "__main__":
    # IMPORTANT: Review changes in DRY_RUN mode first!
    cleanup = SafeCleanup(dry_run=DRY_RUN)
    
    if DRY_RUN:
        print("[SAFETY] Running in DRY RUN mode - no files will be modified\n")
        response = input("Continue with preview? (y/n): ")
    else:
        print("[WARNING] This will modify files!")
        response = input("Are you sure you want to proceed? Type 'yes' to continue: ")
        
    if response.lower() in ['y', 'yes']:
        cleanup.run()
    else:
        print("Cleanup cancelled.")