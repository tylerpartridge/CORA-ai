# 🚫 NO TOOL BACKUPS POLICY

**Effective Immediately: All backup creation by tools is PROHIBITED**

## The Problem We're Solving
- Tool-created backups caused 26,000+ files in .mind/backups/
- Every "safety" backup became permanent clutter
- Git already provides version control - backups are redundant

## The Policy

### ❌ FORBIDDEN Patterns
```python
# NO backup file creation
backup_path = f"{file}_backup_{timestamp}"  # FORBIDDEN
shutil.copy2(file, backup_path)            # FORBIDDEN
os.rename(file, f"{file}.old")             # FORBIDDEN

# NO backup directories
os.makedirs(".mind/backups/feature_x")     # FORBIDDEN
create_backup(file_path)                   # FORBIDDEN
```

### ✅ CORRECT Patterns
```python
# Use Git for safety
subprocess.run(["git", "add", file_path])
subprocess.run(["git", "commit", "-m", "Before optimization"])

# Or use Git stash
subprocess.run(["git", "stash", "push", "-m", "Before risky operation"])

# Or work on a branch
subprocess.run(["git", "checkout", "-b", "experimental_change"])
```

## Enforcement

### Pre-commit Hook
The following patterns will BLOCK commits:
- `backup_path`
- `create_backup`
- `shutil.copy.*backup`
- `.backup`, `.bak`, `_backup_`, `_old`

### Code Review Checklist
- [ ] No backup file creation
- [ ] No "safety copies"
- [ ] No temporary duplicates
- [ ] Git used for version control

## Alternatives to Backups

| If you want to... | Instead of backups... | Use this... |
|-------------------|----------------------|-------------|
| Save before risky change | Creating .bak file | `git commit` or `git stash` |
| Try experimental code | Copying to _old file | `git branch` |
| Preserve working version | Making backup/ folder | `git tag working-version` |
| Rollback if failed | Keeping original copy | `git reset` or `git revert` |

## Why This Works
1. **Git is designed for this** - Version control is its job
2. **Backups accumulate** - They never get cleaned up
3. **Disk space** - Backups waste storage
4. **Confusion** - Which is the "real" file?
5. **Performance** - Fewer files = faster operations

## Exception Process
There are NO exceptions. If you think you need an exception:
1. You don't
2. Use Git branches
3. If still unsure, ask the team
4. The answer will be "use Git"

## Migration
All existing backups in .mind/backups/ will be:
1. Moved to /tmp/ temporarily
2. Deleted after 24 hours
3. Never created again

---

**Remember: Git is your backup system. Trust it.**