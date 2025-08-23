#!/usr/bin/env python3
"""
CORA Bootup Engine - Phase 2 Implementation
Generates atomic cards and map→reduce snapshot from indexed files
"""

import argparse
import datetime
import hashlib
import json
import pathlib
import re
import sys
import textwrap
from typing import List, Dict, Optional, Tuple

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


class BootupEngine:
    def __init__(self, repo_root: pathlib.Path):
        self.root = repo_root
        self.index_path = repo_root / "docs/bootup/_index.yml"
        self.cards_dir = repo_root / "docs/awareness/cards"
        self.snapshot_path = repo_root / "docs/awareness/SNAPSHOT.md"
        self.report_path = repo_root / "docs/awareness/BOOTUP_REPORT.json"
        
    def load_index(self) -> dict:
        """Load the bootup index configuration"""
        if not self.index_path.exists():
            raise FileNotFoundError(f"Index not found: {self.index_path}")
        
        with open(self.index_path) as f:
            return yaml.safe_load(f)
    
    def expand_paths(self, allow_list: List[str], limits: dict) -> List[pathlib.Path]:
        """Expand index paths to actual files with glob support"""
        files = []
        max_files = limits.get('max_files', 150)
        max_mb = limits.get('max_file_mb', 2)
        max_bytes = max_mb * 1024 * 1024
        
        for pattern in allow_list:
            # Check if pattern contains glob characters
            if '*' in pattern or '?' in pattern or '[' in pattern:
                # Use glob to expand pattern
                for match in self.root.glob(pattern):
                    if match.is_file() and match.stat().st_size <= max_bytes:
                        files.append(match)
                    elif match.is_dir():
                        for subfile in match.rglob("*"):
                            if subfile.is_file() and subfile.stat().st_size <= max_bytes:
                                files.append(subfile)
                                if len(files) >= max_files:
                                    break
            else:
                # Treat as direct path
                path = self.root / pattern
                
                if path.is_file():
                    if path.stat().st_size <= max_bytes:
                        files.append(path)
                elif path.is_dir():
                    # Recursively add files from directory
                    for subfile in path.rglob("*"):
                        if subfile.is_file() and subfile.stat().st_size <= max_bytes:
                            files.append(subfile)
                            if len(files) >= max_files:
                                break
            
            if len(files) >= max_files:
                break
        
        return files[:max_files]
    
    def categorize_file(self, file_path: pathlib.Path) -> str:
        """Determine which category a file belongs to"""
        path_str = str(file_path.relative_to(self.root))
        
        # Check explicit categories
        if 'awareness' in path_str and 'identity' in path_str:
            return 'identity'
        elif any(state in path_str.lower() for state in ['now.md', 'status.md', 'next.md', 'state']):
            return 'state'
        elif any(tech in path_str for tech in ['routes', 'models', 'utils', 'technical']):
            return 'technical'
        elif any(hist in path_str for hist in ['history', 'decision', 'adr']):
            return 'history'
        elif any(trig in path_str for trig in ['trigger', 'runbook', 'workflow', 'rules']):
            return 'triggers'
        
        # Default categorization by file type
        if file_path.suffix in ['.py', '.js', '.ts']:
            return 'technical'
        elif file_path.suffix in ['.md', '.txt']:
            return 'state'
        
        return 'general'
    
    def create_card(self, file_path: pathlib.Path, max_words: int = 500) -> str:
        """Create an atomic card from a file"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return f"# Card: {file_path.name}\n\nError reading file: {e}\n"
        
        # Extract key information
        lines = content.splitlines()
        
        # For code files, extract structure
        if file_path.suffix in ['.py', '.js', '.ts']:
            card = f"# Card: {file_path.name}\n\n"
            card += f"> Source: `{file_path.relative_to(self.root)}`\n\n"
            card += "## Structure:\n"
            
            # Extract functions/classes
            for line in lines[:100]:  # Scan first 100 lines
                if file_path.suffix == '.py':
                    if line.strip().startswith('def ') or line.strip().startswith('class '):
                        card += f"- {line.strip()}\n"
                elif file_path.suffix in ['.js', '.ts']:
                    if 'function ' in line or 'class ' in line or 'const ' in line:
                        card += f"- {line.strip()[:80]}\n"
            
            # Add summary
            card += f"\n## Summary:\n"
            card += f"File contains {len(lines)} lines of {file_path.suffix[1:]} code.\n"
            
        # For markdown/text files, extract headers and key content
        else:
            card = f"# Card: {file_path.name}\n\n"
            card += f"> Source: `{file_path.relative_to(self.root)}`\n\n"
            
            # Extract headers
            headers = [line for line in lines if line.startswith('#')][:5]
            if headers:
                card += "## Headers:\n"
                for header in headers:
                    card += f"- {header}\n"
            
            # Extract key content (first meaningful paragraph)
            content_lines = []
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    content_lines.append(line)
                    if len(' '.join(content_lines).split()) > 100:
                        break
            
            if content_lines:
                card += "\n## Content:\n"
                card += ' '.join(content_lines[:10]) + "...\n"
        
        # Ensure card doesn't exceed word limit
        words = card.split()
        if len(words) > max_words:
            card = ' '.join(words[:max_words]) + "\n\n[Card truncated at word limit]"
        
        return card
    
    def generate_cards(self, files: List[pathlib.Path], max_words: int) -> Dict[str, List[pathlib.Path]]:
        """Generate atomic cards for all files"""
        cards_by_category = {}
        
        for file_path in files:
            # Determine category
            category = self.categorize_file(file_path)
            
            # Create card
            card_content = self.create_card(file_path, max_words)
            
            # Generate card filename
            file_hash = hashlib.sha256(str(file_path).encode()).hexdigest()[:8]
            card_name = f"{file_path.stem}.{file_hash}.md"
            
            # Write card
            category_dir = self.cards_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            card_path = category_dir / card_name
            card_path.write_text(card_content, encoding='utf-8')
            
            # Track for snapshot
            if category not in cards_by_category:
                cards_by_category[category] = []
            cards_by_category[category].append(card_path)
        
        return cards_by_category
    
    def generate_snapshot(self, cards_by_category: Dict[str, List[pathlib.Path]]) -> str:
        """Generate map→reduce snapshot from cards"""
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        
        snapshot = f"""# CORA System Snapshot

**Generated**: {timestamp}
**Total Cards**: {sum(len(cards) for cards in cards_by_category.values())}

## System Overview

CORA is an AI-powered expense tracking system designed for construction workers.
This snapshot provides compressed awareness of the entire system state.

## Categories

"""
        
        # Summarize each category
        for category in ['identity', 'state', 'technical', 'history', 'triggers']:
            if category in cards_by_category:
                cards = cards_by_category[category]
                snapshot += f"### {category.title()} ({len(cards)} cards)\n\n"
                
                # List first few cards
                for card_path in cards[:3]:
                    card_name = card_path.stem.split('.')[0]
                    snapshot += f"- {card_name}\n"
                
                if len(cards) > 3:
                    snapshot += f"- ... and {len(cards) - 3} more\n"
                
                snapshot += "\n"
        
        # Add current state summary (read MVP progress from file)
        mvp_progress = "Unknown"
        mvp_path = self.root / "MVP_REQUIREMENTS.md"
        if mvp_path.exists():
            try:
                mvp_content = mvp_path.read_text(encoding='utf-8')
                # Look for completion stats in the file
                for line in mvp_content.splitlines():
                    if "Items Complete:" in line and "/" in line:
                        # Extract pattern like "53/65 (81.5%)" from line like "**Items Complete:** 53/65 (81.5%)"
                        import re
                        match = re.search(r'(\d+)/(\d+)', line)
                        if match:
                            completed, total = match.groups()
                            percentage = (int(completed) / int(total)) * 100
                            mvp_progress = f"{percentage:.1f}% complete ({completed}/{total} items)"
                            break
            except:
                pass
        
        snapshot += f"""## Current State

**MVP Progress**: {mvp_progress}
**Focus**: Bulletproof awareness and backup systems
**Priority**: Complete remaining MVP items before launch

## Key Files

- `MVP_REQUIREMENTS.md` - Launch checklist
- `NOW.md` - Current work in progress
- `STATUS.md` - System health
- `NEXT.md` - Upcoming tasks
- `BOOTUP.md` - Session initialization

## Recent Updates

See `AI_WORK_LOG.md` for detailed session history and checkpoints.

---

*This snapshot was generated from indexed files and atomic cards.*
*For detailed information, explore the cards in `/docs/awareness/cards/`*
"""
        
        return snapshot
    
    def generate_report(self, cards_by_category: Dict[str, List[pathlib.Path]], files_processed: int) -> dict:
        """Generate bootup report"""
        report = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "phase": "2",
            "files_processed": files_processed,
            "cards_generated": sum(len(cards) for cards in cards_by_category.values()),
            "categories": {
                category: len(cards) 
                for category, cards in cards_by_category.items()
            },
            "snapshot_path": str(self.snapshot_path.relative_to(self.root)),
            "cards_path": str(self.cards_dir.relative_to(self.root))
        }
        
        return report
    
    def run(self) -> Tuple[bool, str]:
        """Execute bootup indexing and card generation"""
        try:
            # Load index
            index = self.load_index()
            allow = index.get('allow', [])
            limits = index.get('limits', {})
            max_words = limits.get('max_card_words', 500)
            
            # Expand paths
            files = self.expand_paths(allow, limits)
            
            # Generate cards
            cards_by_category = self.generate_cards(files, max_words)
            
            # Generate snapshot
            snapshot_content = self.generate_snapshot(cards_by_category)
            self.snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            self.snapshot_path.write_text(snapshot_content, encoding='utf-8')
            
            # Generate report
            report = self.generate_report(cards_by_category, len(files))
            self.report_path.write_text(json.dumps(report, indent=2))
            
            # Update AI_WORK_LOG
            log_path = self.root / "AI_WORK_LOG.md"
            if log_path.exists():
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n{report['timestamp']}  bootup: {report['cards_generated']} cards → {self.snapshot_path.relative_to(self.root)}\n")
            
            message = f"BOOTUP: {len(files)} files → {report['cards_generated']} cards\n"
            message += f"Snapshot: {self.snapshot_path.relative_to(self.root)}\n"
            message += f"Report: {self.report_path.relative_to(self.root)}"
            
            return True, message
            
        except Exception as e:
            return False, f"Bootup failed: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description="CORA Bootup Engine")
    parser.add_argument("--repo", default=".", help="Repository root")
    args = parser.parse_args()
    
    repo_root = pathlib.Path(args.repo).resolve()
    engine = BootupEngine(repo_root)
    
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