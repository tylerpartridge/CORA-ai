# 🧹 CORA Workspace Health Action Plan

Based on both audits, here's what needs immediate attention:

## 🚨 Critical Issues Found

### 1. Root Directory Violations (Currently ~40+ files, should be 6)
**Found in root that shouldn't be there:**
- Multiple test files (test_*.py) - 11 files
- Status/report files (.md) - 12+ temporary files  
- Utility scripts (setup_test_user.py, verify_system.py, etc.)
- Broken backup (app_backup_broken.py)

### 2. Duplicate Route Files
- `routes/expenses.py` vs `routes/expenses_simple.py` vs `routes/expense_routes.py`
- `routes/payments.py` vs `routes/payment_routes.py`

### 3. Orphaned Test/Status Files
- 45.5KB of old status reports
- 22.3KB of phase1 reports in data/
- Multiple test files not in tests/ directory

## ✅ Safe Cleanup Commands

```bash
# 1. Move test files to proper location
mkdir -p tests
mv test_*.py tests/

# 2. Archive old reports
mkdir -p docs/archive/cleanup_2025_07_14
mv CLAUDE_AUDIT_FINDINGS.md docs/archive/cleanup_2025_07_14/
mv FINAL_AUDIT_REPORT.md docs/archive/cleanup_2025_07_14/
mv FINAL_STATUS.md docs/archive/cleanup_2025_07_14/
mv FUNCTIONAL_AUDIT_REPORT.md docs/archive/cleanup_2025_07_14/
mv STATUS.md docs/archive/cleanup_2025_07_14/
mv SYSTEM_STATUS.md docs/archive/cleanup_2025_07_14/
mv SYSTEM_AUDIT_*.md docs/archive/cleanup_2025_07_14/
mv IMMEDIATE_FIX.md docs/archive/cleanup_2025_07_14/
mv EMERGENCY_RESTORE.md docs/archive/cleanup_2025_07_14/
mv NOW.md docs/archive/cleanup_2025_07_14/
mv NEXT.md docs/archive/cleanup_2025_07_14/

# 3. Remove broken/duplicate files
rm app_backup_broken.py
rm routes/expenses_simple.py
rm routes/expense_routes.py
rm routes/payment_routes.py

# 4. Clean up old logs
rm server.log server2.log

# 5. Archive old phase reports
mkdir -p data/archive
mv data/phase1_report_*.json data/archive/
```

## 🛡️ What We're Keeping

### Essential Root Files (Target: 6)
1. `app.py` - Main application
2. `README.md` - Project documentation
3. `requirements.txt` - Dependencies (create if missing)
4. `.env` - Environment config
5. `.gitignore` - Git config
6. `BUILDING_RULES.md` - Development standards

### Critical Directories
- `/models/` - All database models
- `/routes/` - API routes (minus duplicates)
- `/services/` - Business logic
- `/middleware/` - App middleware
- `/data/*.db` - Database files
- `/web/` - Frontend assets
- `/docs/` - Active documentation

## 📊 Expected Results

**Before Cleanup:**
- Root files: ~40+
- Duplicate routes: 5 files
- Orphaned reports: ~113KB

**After Cleanup:**
- Root files: 6 (compliant)
- No duplicates
- Archived reports accessible if needed
- ~113KB space saved

## ⚠️ Safety Notes

1. All cleanup commands above are SAFE - they only move/remove clearly identified duplicates and temporary files
2. Database files are NOT touched
3. Core application files are preserved
4. Old reports are archived, not deleted
5. Test files are moved, not removed

## 🚀 Execute Cleanup?

Run the commands above to bring CORA into full compliance with BUILDING_RULES.md. The system will remain 100% functional while becoming much cleaner and more maintainable.