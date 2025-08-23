#!/usr/bin/env python3
"""
CORA Save Engine - Phase 2 Implementation
Smart progress tracking with diff detection, classification, and routing
"""

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import shutil
from typing import Dict, List, Tuple, Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

class SaveEngine:
    def __init__(self, repo_root: pathlib.Path):
        self.root = repo_root
        self.policy_path = repo_root / "tools/save_policy.yml"
        self.tracker_path = repo_root / "docs/progress/tracker.yml"
        # Use proper Unix path even on Windows
        if sys.platform.startswith('win'):
            self.bundle_root = pathlib.Path("C:/var/backups/cora/progress")
        else:
            self.bundle_root = pathlib.Path("/var/backups/cora/progress")
        self.lock_file = pathlib.Path("/var/lock/cora-save.lock")
        
        # Load policies
        self.policy = self._load_policy()
        self.tracker = self._load_tracker()
        
    def _load_policy(self) -> dict:
        """Load save policy configuration"""
        if self.policy_path.exists():
            with open(self.policy_path) as f:
                return yaml.safe_load(f)
        return {
            "rotation": {"ai_work_log": {"mode": "monthly", "soft_lines": 10000}},
            "importance": {"keywords": ["launch", "incident", "security"], "min_score": 3}
        }
    
    def _load_tracker(self) -> dict:
        """Load last checkpoint info"""
        if self.tracker_path.exists():
            with open(self.tracker_path) as f:
                return yaml.safe_load(f) or {}
        return {"last_checkpoint": None, "last_sha": None, "last_ts": None}
    
    def _save_tracker(self):
        """Save checkpoint info"""
        self.tracker_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tracker_path, 'w') as f:
            yaml.dump(self.tracker, f)
    
    def get_changed_files(self) -> List[Tuple[str, str]]:
        """Get list of changed files using git diff"""
        changes = []
        
        # Get unstaged changes
        try:
            result = subprocess.run(
                ["git", "diff", "--name-status"],
                cwd=self.root,
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        changes.append((parts[0], parts[1]))
        except subprocess.CalledProcessError:
            pass
        
        # Get staged changes
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-status"],
                cwd=self.root,
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        changes.append((parts[0], parts[1]))
        except subprocess.CalledProcessError:
            pass
        
        return changes
    
    def get_untracked_files(self) -> List[str]:
        """Get list of untracked files"""
        try:
            result = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                cwd=self.root,
                capture_output=True,
                text=True,
                check=True
            )
            return [line for line in result.stdout.strip().split("\n") if line]
        except subprocess.CalledProcessError:
            return []
    
    def classify_content(self, file_path: str, content: str = None) -> str:
        """Classify content type based on file and content analysis"""
        path = pathlib.Path(file_path)
        
        # File-based classification
        if path.suffix in ['.py', '.js', '.ts', '.jsx', '.tsx']:
            return 'code'
        elif path.suffix in ['.md', '.txt', '.doc']:
            # Check content for better classification
            if content is None and (self.root / path).exists():
                content = (self.root / path).read_text(errors='ignore')
            
            if content:
                content_lower = content.lower()
                if any(word in content_lower for word in ['strategy', 'plan', 'market', 'user', 'launch']):
                    return 'strategy'
                elif any(word in content_lower for word in ['decided', 'decision', 'chose', 'selected']):
                    return 'decision'
                elif any(word in content_lower for word in ['idea', 'think', 'consider', 'maybe']):
                    return 'discussion'
        
        # Path-based classification
        if 'routes' in str(path) or 'models' in str(path):
            return 'code'
        elif 'docs' in str(path):
            return 'documentation'
        
        return 'general'
    
    def calculate_importance(self, changes: List[Tuple[str, str]]) -> int:
        """Calculate importance score for changes"""
        score = 0
        keywords = self.policy.get('importance', {}).get('keywords', [])
        
        for status, file_path in changes:
            # Check filename
            for keyword in keywords:
                if keyword.lower() in file_path.lower():
                    score += 2
            
            # Check if critical file
            if any(critical in file_path for critical in ['MVP', 'REQUIREMENTS', 'BOOTUP']):
                score += 3
            
            # Status scoring
            if status == 'A':  # Added
                score += 1
            elif status == 'D':  # Deleted
                score += 2
            elif status == 'M':  # Modified
                score += 1
        
        return score
    
    def create_bundle(self, checkpoint_id: str) -> pathlib.Path:
        """Create progress bundle with all artifacts"""
        timestamp = datetime.datetime.utcnow()
        date_parts = timestamp.strftime("%Y/%m/%d").split('/')
        
        # Create bundle directory
        bundle_dir = self.bundle_root / date_parts[0] / date_parts[1] / date_parts[2] / checkpoint_id
        bundle_dir.mkdir(parents=True, exist_ok=True)
        artifacts_dir = bundle_dir / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)
        
        # Get changes and untracked files
        changes = self.get_changed_files()
        untracked = self.get_untracked_files()
        importance = self.calculate_importance(changes)
        
        # Copy actual file contents to artifacts
        files_to_save = set()
        for status, file_path in changes:
            if status != 'D':  # Don't save deleted files
                files_to_save.add(file_path)
        files_to_save.update(untracked)
        
        # Copy files to artifacts directory
        for file_path in files_to_save:
            src_path = self.root / file_path
            if src_path.exists() and src_path.is_file():
                try:
                    dst_path = artifacts_dir / file_path
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dst_path)
                except Exception as e:
                    print(f"Warning: Could not copy {file_path}: {e}", file=sys.stderr)
        
        # Create patch.diff for modified files
        try:
            diff_result = subprocess.run(
                ["git", "diff", "HEAD"],
                cwd=self.root,
                capture_output=True,
                text=True,
                check=False
            )
            if diff_result.stdout:
                (bundle_dir / "patch.diff").write_text(diff_result.stdout, encoding='utf-8')
        except Exception as e:
            print(f"Warning: Could not create patch.diff: {e}", file=sys.stderr)
        
        # Create PROGRESS.md
        progress_content = f"""# Progress Checkpoint: {checkpoint_id}

**Timestamp**: {timestamp.isoformat()}Z
**Changes**: {len(changes)} files
**Untracked**: {len(untracked)} files
**Importance Score**: {importance}

## Changed Files:
"""
        for status, file_path in changes[:20]:  # Limit to 20 for readability
            status_map = {'M': 'Modified', 'A': 'Added', 'D': 'Deleted'}
            progress_content += f"- {status_map.get(status, status)}: {file_path}\n"
        
        if len(changes) > 20:
            progress_content += f"\n... and {len(changes) - 20} more files\n"
        
        if untracked:
            progress_content += "\n## Untracked Files:\n"
            for file_path in untracked[:10]:
                progress_content += f"- {file_path}\n"
            if len(untracked) > 10:
                progress_content += f"\n... and {len(untracked) - 10} more files\n"
        
        # Classification summary
        classifications = {}
        for _, file_path in changes:
            cls = self.classify_content(file_path)
            classifications[cls] = classifications.get(cls, 0) + 1
        
        progress_content += "\n## Classification:\n"
        for cls, count in sorted(classifications.items()):
            progress_content += f"- {cls}: {count} files\n"
        
        (bundle_dir / "PROGRESS.md").write_text(progress_content, encoding='utf-8')
        
        # Create MANIFEST.json
        manifest = {
            "checkpoint": checkpoint_id,
            "timestamp": timestamp.isoformat() + "Z",
            "phase": "2",
            "changes": len(changes),
            "importance": importance,
            "classifications": classifications,
            "sha256": {}
        }
        
        # Calculate checksums
        for file_path in bundle_dir.glob("*"):
            if file_path.is_file() and file_path.name != "MANIFEST.json":
                with open(file_path, 'rb') as f:
                    manifest["sha256"][file_path.name] = hashlib.sha256(f.read()).hexdigest()
        
        (bundle_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        
        # Create CHANGES.txt with detailed diff
        changes_content = f"Changes for checkpoint {checkpoint_id}\n" + "=" * 50 + "\n\n"
        for status, file_path in changes:
            changes_content += f"{status}\t{file_path}\n"
        
        (bundle_dir / "CHANGES.txt").write_text(changes_content, encoding='utf-8')
        
        return bundle_dir
    
    def update_logs(self, checkpoint_id: str, bundle_path: pathlib.Path):
        """Update AI_WORK_LOG and HANDOFF atomically"""
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        
        # Update AI_WORK_LOG.md (append-only)
        log_path = self.root / "AI_WORK_LOG.md"
        if log_path.exists():
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{timestamp}  {checkpoint_id}  saved bundle → {bundle_path}\n")
        
        # Update HANDOFF.md (atomic)
        handoff_path = self.root / "HANDOFF.md"
        if handoff_path.exists():
            temp_path = handoff_path.with_suffix('.tmp')
            shutil.copy2(handoff_path, temp_path)
            with open(temp_path, 'a') as f:
                f.write(f"\n\n---\n**Latest checkpoint**: {checkpoint_id} at {timestamp}\n")
            temp_path.replace(handoff_path)
        
        # Update tracker
        self.tracker['last_checkpoint'] = checkpoint_id
        self.tracker['last_ts'] = timestamp
        try:
            git_sha = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.root,
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()[:8]
            self.tracker['last_sha'] = git_sha
        except:
            pass
        
        self._save_tracker()
    
    def run(self) -> Tuple[bool, str]:
        """Execute save progress workflow"""
        # Check and acquire lock
        if self.lock_file.exists():
            # Check if lock is stale (older than 10 minutes)
            try:
                lock_age = datetime.datetime.now().timestamp() - self.lock_file.stat().st_mtime
                if lock_age > 600:  # 10 minutes
                    self.lock_file.unlink()  # Remove stale lock
                else:
                    return False, f"Save already in progress (lock file exists)"
            except:
                return False, f"Could not check lock file"
        
        try:
            # Create lock file
            self.lock_file.parent.mkdir(parents=True, exist_ok=True)
            self.lock_file.touch()
            
            # Generate checkpoint ID
            timestamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            checkpoint_id = f"ckpt-{timestamp}"
            
            # Create bundle
            bundle_path = self.create_bundle(checkpoint_id)
            
            # Update logs
            self.update_logs(checkpoint_id, bundle_path)
            
            # Calculate importance for reporting
            changes = self.get_changed_files()
            untracked = self.get_untracked_files()
            importance = self.calculate_importance(changes)
            
            message = f"SAVE: {checkpoint_id} complete (Phase-2)\n"
            message += f"Bundle: {bundle_path}\n"
            message += f"Changes: {len(changes)} files, Untracked: {len(untracked)} files\n"
            message += f"Importance: {importance}"
            
            if importance >= self.policy.get('importance', {}).get('min_score', 3):
                message += " ⚠️ HIGH IMPORTANCE"
            
            return True, message
            
        except Exception as e:
            return False, f"Save failed: {str(e)}"
        finally:
            # Always remove lock file
            if self.lock_file.exists():
                try:
                    self.lock_file.unlink()
                except:
                    pass


def main():
    parser = argparse.ArgumentParser(description="CORA Save Engine")
    parser.add_argument("--repo", default=".", help="Repository root")
    args = parser.parse_args()
    
    repo_root = pathlib.Path(args.repo).resolve()
    engine = SaveEngine(repo_root)
    
    success, message = engine.run()
    # Handle Unicode output properly on Windows
    try:
        print(message)
    except UnicodeEncodeError:
        # Fallback: encode to UTF-8 and write to stdout
        sys.stdout.buffer.write(message.encode('utf-8'))
        sys.stdout.buffer.write(b'\n')
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()