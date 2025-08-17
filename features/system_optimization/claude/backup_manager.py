#!/usr/bin/env python3
"""
Automated Backup Management Script
Purpose: Intelligently manage backup files to save space
Author: Claude (Opus 4.1)
Date: 2025-08-10
Safety: Keeps important backups, removes redundant ones
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

class BackupManager:
    def __init__(self, backup_dir='backups', dry_run=True):
        self.backup_dir = Path(backup_dir)
        self.dry_run = dry_run
        self.stats = {
            'total_files': 0,
            'total_size': 0,
            'kept_files': 0,
            'kept_size': 0,
            'removed_files': 0,
            'removed_size': 0
        }
        
    def analyze_backups(self) -> Dict:
        """Analyze backup files and determine what to keep/remove"""
        if not self.backup_dir.exists():
            print(f"Backup directory {self.backup_dir} not found")
            return {}
            
        backups = []
        
        # Scan all backup files
        for file_path in self.backup_dir.glob('*.zip.enc'):
            stat = file_path.stat()
            backups.append({
                'path': file_path,
                'name': file_path.name,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'age_days': (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
            })
        
        # Also check for other backup types
        for pattern in ['*.db', '*.html', '*.json', '*.zip']:
            for file_path in self.backup_dir.glob(pattern):
                stat = file_path.stat()
                backups.append({
                    'path': file_path,
                    'name': file_path.name,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'age_days': (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
                })
        
        # Sort by date
        backups.sort(key=lambda x: x['modified'], reverse=True)
        
        return self.apply_retention_policy(backups)
    
    def apply_retention_policy(self, backups: List[Dict]) -> Dict:
        """
        Apply intelligent retention policy:
        - Keep all backups from last 7 days
        - Keep daily backups for last 30 days
        - Keep weekly backups for last 90 days
        - Keep monthly backups for last year
        - Keep yearly backups forever
        """
        keep = []
        remove = []
        
        # Track which dates we've kept backups for
        kept_daily = set()
        kept_weekly = set()
        kept_monthly = set()
        kept_yearly = set()
        
        for backup in backups:
            age = backup['age_days']
            date = backup['modified'].date()
            week = date.isocalendar()[1]
            month = (date.year, date.month)
            year = date.year
            
            should_keep = False
            reason = ""
            
            # Always keep last 7 days
            if age <= 7:
                should_keep = True
                reason = "Recent (< 7 days)"
                
            # Keep one per day for last 30 days
            elif age <= 30 and date not in kept_daily:
                should_keep = True
                kept_daily.add(date)
                reason = "Daily backup (< 30 days)"
                
            # Keep one per week for last 90 days
            elif age <= 90 and week not in kept_weekly:
                should_keep = True
                kept_weekly.add(week)
                reason = "Weekly backup (< 90 days)"
                
            # Keep one per month for last year
            elif age <= 365 and month not in kept_monthly:
                should_keep = True
                kept_monthly.add(month)
                reason = "Monthly backup (< 1 year)"
                
            # Keep one per year forever
            elif year not in kept_yearly:
                should_keep = True
                kept_yearly.add(year)
                reason = "Yearly backup"
            
            # Special cases - always keep
            if 'pre_cleanup' in backup['name'] or 'before' in backup['name']:
                should_keep = True
                reason = "Important snapshot"
            
            backup['keep'] = should_keep
            backup['reason'] = reason
            
            if should_keep:
                keep.append(backup)
                self.stats['kept_files'] += 1
                self.stats['kept_size'] += backup['size']
            else:
                remove.append(backup)
                self.stats['removed_files'] += 1
                self.stats['removed_size'] += backup['size']
            
            self.stats['total_files'] += 1
            self.stats['total_size'] += backup['size']
        
        return {'keep': keep, 'remove': remove}
    
    def execute_cleanup(self, analysis: Dict) -> bool:
        """Execute the cleanup based on analysis"""
        
        if not analysis:
            print("No backups to process")
            return False
        
        print("\n" + "="*60)
        print("BACKUP CLEANUP PLAN")
        print("="*60)
        
        # Show what will be kept
        print(f"\n[KEEP] Files to KEEP: {len(analysis['keep'])}")
        for backup in analysis['keep'][:5]:  # Show first 5
            size_mb = backup['size'] / (1024 * 1024)
            print(f"  [OK] {backup['name']} ({size_mb:.1f} MB) - {backup['reason']}")
        if len(analysis['keep']) > 5:
            print(f"  ... and {len(analysis['keep']) - 5} more")
        
        # Show what will be removed
        print(f"\n[REMOVE] Files to REMOVE: {len(analysis['remove'])}")
        if analysis['remove']:
            for backup in analysis['remove'][:10]:  # Show first 10
                size_mb = backup['size'] / (1024 * 1024)
                age = backup['age_days']
                print(f"  [X] {backup['name']} ({size_mb:.1f} MB, {age} days old)")
            if len(analysis['remove']) > 10:
                print(f"  ... and {len(analysis['remove']) - 10} more")
        
        # Show space savings
        space_saved_mb = self.stats['removed_size'] / (1024 * 1024)
        space_kept_mb = self.stats['kept_size'] / (1024 * 1024)
        
        print(f"\n[SPACE] Space Summary:")
        print(f"  Current usage: {(self.stats['total_size'] / (1024 * 1024)):.1f} MB")
        print(f"  After cleanup: {space_kept_mb:.1f} MB")
        print(f"  Space saved: {space_saved_mb:.1f} MB")
        
        if self.dry_run:
            print("\n[DRY RUN] No files were actually removed")
            print("Set dry_run=False to execute cleanup")
        else:
            # Actually remove files
            removed_count = 0
            for backup in analysis['remove']:
                try:
                    backup['path'].unlink()
                    removed_count += 1
                except Exception as e:
                    print(f"Error removing {backup['name']}: {e}")
            
            print(f"\n[OK] Removed {removed_count} backup files")
            print(f"[SPACE] Freed {space_saved_mb:.1f} MB of disk space")
        
        return True
    
    def generate_report(self, analysis: Dict):
        """Generate detailed report"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = {
            'timestamp': timestamp,
            'dry_run': self.dry_run,
            'statistics': self.stats,
            'policy': {
                'keep_recent': '7 days',
                'keep_daily': '30 days',
                'keep_weekly': '90 days',
                'keep_monthly': '1 year',
                'keep_yearly': 'forever'
            },
            'files_kept': len(analysis.get('keep', [])),
            'files_removed': len(analysis.get('remove', [])),
            'space_saved_mb': self.stats['removed_size'] / (1024 * 1024)
        }
        
        # Save report
        report_path = Path('features/system_optimization/claude/backup_cleanup_report.json')
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n[REPORT] Report saved to: {report_path}")
        
        return report


def main():
    """Main execution"""
    print("[BACKUP] CORA Backup Management System")
    print("="*60)
    
    # Set dry_run=False to actually remove files
    manager = BackupManager(backup_dir='backups', dry_run=True)
    
    # Analyze backups
    print("Analyzing backup files...")
    analysis = manager.analyze_backups()
    
    if not analysis:
        print("No backup files found")
        return
    
    # Execute cleanup
    manager.execute_cleanup(analysis)
    
    # Generate report
    manager.generate_report(analysis)
    
    print("\n[COMPLETE] Backup management complete!")
    
    if manager.dry_run:
        print("\nTo actually remove files, edit script and set: dry_run=False")


if __name__ == "__main__":
    main()