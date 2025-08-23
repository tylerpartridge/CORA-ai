#!/usr/bin/env python3
"""
CORA Log Rotation - Monthly rotation for awareness logs
Prevents unbounded growth and maintains history
"""

import argparse
import datetime
import gzip
import pathlib
import shutil
import subprocess
import sys
from typing import List, Tuple

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


class LogRotator:
    def __init__(self, repo_root: pathlib.Path):
        self.root = repo_root
        self.policy_path = repo_root / "tools/save_policy.yml"
        self.policy = self._load_policy()
        
    def _load_policy(self) -> dict:
        """Load rotation policy"""
        if self.policy_path.exists():
            with open(self.policy_path) as f:
                return yaml.safe_load(f)
        return {
            "rotation": {
                "ai_work_log": {"mode": "monthly", "soft_lines": 10000},
                "discussion_space": {"mode": "monthly", "soft_lines": 8000}
            }
        }
    
    def count_lines(self, file_path: pathlib.Path) -> int:
        """Count lines in a file"""
        if not file_path.exists():
            return 0
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    
    def should_rotate(self, file_name: str, file_path: pathlib.Path) -> bool:
        """Check if file needs rotation"""
        policy = self.policy.get('rotation', {}).get(file_name, {})
        
        if not policy:
            return False
        
        soft_lines = policy.get('soft_lines', 10000)
        current_lines = self.count_lines(file_path)
        
        return current_lines > soft_lines
    
    def rotate_file(self, file_path: pathlib.Path) -> Tuple[bool, str]:
        """Rotate a single file"""
        if not file_path.exists():
            return False, f"File not found: {file_path}"
        
        try:
            # Check for and temporarily remove append-only attribute if on Linux
            had_append_only = False
            if sys.platform.startswith('linux'):
                try:
                    # Check if file has append-only attribute
                    result = subprocess.run(
                        ["lsattr", str(file_path)],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    if result.returncode == 0 and 'a' in result.stdout[:20]:
                        had_append_only = True
                        # Temporarily remove append-only
                        subprocess.run(
                            ["sudo", "chattr", "-a", str(file_path)],
                            check=False
                        )
                except:
                    pass  # Not critical if this fails
            
            # Generate archive name
            timestamp = datetime.datetime.utcnow()
            year_month = timestamp.strftime("%Y-%m")
            archive_name = f"{file_path.stem}-{year_month}{file_path.suffix}"
            archive_path = file_path.parent / "archive" / archive_name
            
            # Create archive directory
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move current file to archive
            shutil.move(str(file_path), str(archive_path))
            
            # Compress the archive
            gz_path = archive_path.with_suffix(archive_path.suffix + '.gz')
            with open(archive_path, 'rb') as f_in:
                with gzip.open(gz_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed archive
            archive_path.unlink()
            
            # Create new file with header
            header = f"""# {file_path.name}

**Rotated**: {timestamp.isoformat()}Z
**Previous archive**: {gz_path.relative_to(self.root)}

---

"""
            file_path.write_text(header, encoding='utf-8')
            
            # Restore append-only attribute if it was set
            if had_append_only and sys.platform.startswith('linux'):
                try:
                    subprocess.run(
                        ["sudo", "chattr", "+a", str(file_path)],
                        check=False
                    )
                except:
                    pass
            
            return True, f"Rotated to {gz_path.name}"
            
        except Exception as e:
            return False, f"Rotation failed: {str(e)}"
    
    def check_and_rotate(self) -> List[Tuple[str, bool, str]]:
        """Check all files and rotate as needed"""
        results = []
        
        # Define files to check
        files_to_check = {
            "ai_work_log": self.root / "AI_WORK_LOG.md",
            "discussion_space": self.root / "AI_DISCUSSION_SPACE.md",
        }
        
        for file_name, file_path in files_to_check.items():
            if self.should_rotate(file_name, file_path):
                success, message = self.rotate_file(file_path)
                results.append((file_path.name, success, message))
            else:
                lines = self.count_lines(file_path)
                policy = self.policy.get('rotation', {}).get(file_name, {})
                soft_lines = policy.get('soft_lines', 10000)
                results.append((
                    file_path.name, 
                    False, 
                    f"No rotation needed ({lines}/{soft_lines} lines)"
                ))
        
        return results
    
    def run(self) -> Tuple[bool, str]:
        """Execute rotation check and process"""
        try:
            results = self.check_and_rotate()
            
            # Build summary message
            message = "Log Rotation Report:\n"
            rotated_count = 0
            
            for file_name, success, detail in results:
                if success:
                    rotated_count += 1
                    message += f"✓ {file_name}: {detail}\n"
                else:
                    message += f"- {file_name}: {detail}\n"
            
            if rotated_count > 0:
                message += f"\nRotated {rotated_count} file(s) successfully."
                
                # Log rotation event
                log_path = self.root / "AI_WORK_LOG.md"
                if log_path.exists():
                    with open(log_path, 'a') as f:
                        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
                        f.write(f"\n{timestamp}  log-rotation: {rotated_count} files rotated\n")
            else:
                message += "\nNo files needed rotation."
            
            return True, message
            
        except Exception as e:
            return False, f"Rotation check failed: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description="CORA Log Rotation")
    parser.add_argument("--repo", default=".", help="Repository root")
    parser.add_argument("--force", action="store_true", help="Force rotation regardless of size")
    args = parser.parse_args()
    
    repo_root = pathlib.Path(args.repo).resolve()
    rotator = LogRotator(repo_root)
    
    if args.force:
        # Override policy for forced rotation
        for key in rotator.policy.get('rotation', {}):
            rotator.policy['rotation'][key]['soft_lines'] = 0
    
    success, message = rotator.run()
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