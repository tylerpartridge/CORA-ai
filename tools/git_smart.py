#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/git_smart.py
🎯 PURPOSE: Smart git operations with context preservation
🔗 IMPORTS: subprocess, datetime, json
📤 EXPORTS: smart_commit(), prepare_deploy()
🔄 PATTERN: Git with context
📝 TODOS: Add automatic branch management

Preserves AI context in commit messages!
"""

import subprocess
import datetime
import json
import os

def get_changed_files():
    """Get list of changed files"""
    result = subprocess.run(['git', 'status', '--porcelain'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        return []
    
    changes = []
    for line in result.stdout.strip().split('\n'):
        if line:
            status, filename = line[:2], line[3:]
            changes.append((status.strip(), filename))
    
    return changes

def read_current_focus():
    """Get current focus for commit context"""
    if os.path.exists('.ai/CURRENT_FOCUS.md'):
        with open('.ai/CURRENT_FOCUS.md', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('## What'):
                    return lines[lines.index(line) + 1].strip()
    return "General updates"

def smart_commit(message=None):
    """Create a commit with rich context"""
    changes = get_changed_files()
    if not changes:
        print("✅ No changes to commit")
        return
    
    # Show changes
    print("📝 Changes to commit:")
    for status, filename in changes[:10]:
        print(f"   {status} {filename}")
    if len(changes) > 10:
        print(f"   ... and {len(changes) - 10} more")
    
    # Generate commit message
    if not message:
        focus = read_current_focus()
        message = f"{focus}"
    
    # Add context
    context_lines = [
        f"\n\nContext:",
        f"- Phase: Landing Page Development",
        f"- Files changed: {len(changes)}",
        f"- Timestamp: {datetime.datetime.now().isoformat()}"
    ]
    
    # Add file categories
    py_files = [f for s, f in changes if f.endswith('.py')]
    md_files = [f for s, f in changes if f.endswith('.md')]
    if py_files:
        context_lines.append(f"- Python files: {len(py_files)}")
    if md_files:
        context_lines.append(f"- Documentation: {len(md_files)}")
    
    full_message = message + "\n".join(context_lines)
    
    # Show and confirm
    print(f"\n📋 Commit message:")
    print("---")
    print(full_message)
    print("---")
    
    confirm = input("\n✅ Commit with this message? (y/n): ")
    if confirm.lower() != 'y':
        print("❌ Commit cancelled")
        return
    
    # Stage all changes
    subprocess.run(['git', 'add', '-A'])
    
    # Commit
    result = subprocess.run(['git', 'commit', '-m', full_message])
    if result.returncode == 0:
        print("✅ Committed successfully!")
        
        # Update checkpoint
        with open('.ai/CHECKPOINT.md', 'a') as f:
            f.write(f"\n\n## Git Commit - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"- Message: {message}\n")
            f.write(f"- Files: {len(changes)}\n")
    else:
        print("❌ Commit failed")

def prepare_deploy():
    """Prepare for deployment with checks"""
    print("🚀 Preparing for deployment...\n")
    
    # Check for uncommitted changes
    changes = get_changed_files()
    if changes:
        print("⚠️  You have uncommitted changes!")
        smart_commit("Pre-deployment checkpoint")
    
    # Run health check
    from health_check import check_health
    if not check_health():
        print("❌ Fix health issues before deploying!")
        return False
    
    # Create deployment checklist
    checklist = [
        "Update requirements.txt",
        "Test locally one more time",
        "Update .env.example",
        "Create deployment branch",
        "Push to GitHub",
        "Deploy to DigitalOcean",
        "Update DNS records",
        "Test production site",
        "Monitor for errors"
    ]
    
    print("\n📋 Deployment Checklist:")
    for item in checklist:
        print(f"   [ ] {item}")
    
    # Save deployment snapshot
    snapshot = {
        'timestamp': datetime.datetime.now().isoformat(),
        'commit': subprocess.run(['git', 'rev-parse', 'HEAD'], 
                               capture_output=True, text=True).stdout.strip(),
        'files': len(changes),
        'checklist': checklist
    }
    
    os.makedirs('.ai/deployments', exist_ok=True)
    deploy_file = f".ai/deployments/deploy_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(deploy_file, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    print(f"\n💾 Deployment snapshot saved to {deploy_file}")
    print("✅ Ready to deploy! Follow the checklist above.")
    
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'deploy':
            prepare_deploy()
        else:
            # Use remaining args as commit message
            smart_commit(" ".join(sys.argv[1:]))
    else:
        smart_commit()