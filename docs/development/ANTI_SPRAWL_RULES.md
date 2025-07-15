# ANTI-SPRAWL RULES
**Simple rules to prevent repository bloat**

> ⚠️ **CRITICAL**: Never break working code to follow these rules! A 400-line working file is better than broken imports across 10 files.

## 🚫 NEVER DO THESE
- **Break working code to follow size rules**
- Add directories with >50 files without .gitignore
- Create "utility" or "helper" files
- Add files to root directory
- Create new directories without clear purpose

## ✅ ALWAYS DO THESE
- Run health check before commits: `python tools/repo_health_check.py`
- Use existing files over creating new ones
- **Keep files as small as practical without breaking functionality**
- If a file needs to be 400 lines to work properly, that's OK
- Only split files when it makes logical sense, not just for size
- Add new file types to .gitignore immediately

## 📁 DIRECTORY RULES
- `/tools` - Scripts only
- `/web` - UI files only  
- `/data` - Config files only
- Root - 6 files maximum

## 🔍 HEALTH CHECK
Before any commit, run:
```bash
python tools/repo_health_check.py
```
If it fails, fix the issue before committing.

## 🧹 CLEANUP TRIGGERS
- >100 untracked files
- Any directory with >50 files
- Files over 500 lines (investigate why it's so large)
- New directories not in .gitignore

## ✅ REVIEW CHECKLIST
- [ ] Did you run the health check?
- [ ] Are files reasonably sized for their purpose?
- [ ] Did you avoid breaking working code for arbitrary size limits?
- [ ] Is every new directory in .gitignore?
- [ ] Are you reusing existing files where possible?
- [ ] Did you avoid adding new "helper" scripts?

## ⏰ WEEKLY REMINDER
Once a week, run:
```sh
git status
find . -type f | wc -l
```
If the file count is creeping up, investigate and clean up!

**Remember: Every new file is a liability. Use existing solutions.** 