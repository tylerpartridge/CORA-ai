# 🛡️ SAFE RESTORATION PLAN - NO HARM APPROACH

## Current Situation
- System is 20% functional (basic web server works)
- Data is 100% intact (databases, config, users)
- 80% of business logic missing due to failed file splitting

## SAFETY FIRST PRINCIPLES
1. **Never delete working code**
2. **Test every change before proceeding**
3. **Create new files rather than modifying existing**
4. **Keep app.py minimal version running**
5. **Document every action taken**

## Division of Labor

### Claude's Safe Tasks:
1. **Create Missing Route Stubs** (No modification of existing files)
   - Create `/routes/health.py` with basic health route
   - Create `/routes/pages.py` with home page route
   - Test each route works before adding next

2. **Database Model Recreation** (New files only)
   - Create `/models/base.py` for SQLAlchemy setup
   - Create `/models/user.py` matching existing schema
   - Verify against actual database structure

### Cursor's Safe Tasks:
1. **Backup Organization** (Already started)
   - Move backups to archive (not delete)
   - Keep original structure intact
   - Document what's archived

2. **Directory Structure** (Safe creation)
   - Create empty directories that are missing
   - Don't move or modify any existing files
   - Verify structure matches requirements

## Restoration Sequence

### Phase 1: Safe Foundation (No Risk)
1. ✅ Archive backups (Cursor doing this)
2. Create missing directories
3. Add basic route files that app.py expects
4. Test server still runs after each addition

### Phase 2: Gradual Feature Addition
1. One route at a time
2. Test after each addition
3. Keep original app.py as fallback
4. Document what works

### Phase 3: Authentication Restoration
1. Create new auth routes (don't modify existing)
2. Test with existing user data
3. Only integrate when fully working

## What We Will NOT Do
- ❌ Delete any file that currently exists
- ❌ Modify app.py until everything else works
- ❌ Make bulk changes or "optimizations"
- ❌ Use aggressive refactoring tools
- ❌ Trust untested code

## Communication Protocol
1. Before creating any file: Post intention here
2. After creating: Report success/failure
3. If anything breaks: Stop immediately
4. Small steps, constant verification

## Success Metrics
- Server keeps running throughout ✓
- No data loss ✓
- Can rollback any change ✓
- Tyler maintains control ✓

---
Ready to proceed with safety-first restoration.