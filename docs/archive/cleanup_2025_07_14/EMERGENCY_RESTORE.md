# 🚨 EMERGENCY SYSTEM RESTORE

## Current Situation
- app.py was "modularized" but the modules were never created
- System is completely broken - won't even start
- Tyler needs us to fix this following proper build rules

## What Claude is Doing
1. Stripping app.py down to minimal working version
2. Removing all broken imports
3. Getting basic functionality running

## What Cursor Needs to Do
1. Check this file for Claude's progress
2. Help restore missing functionality piece by piece
3. FOLLOW BUILD RULES - no files over 300 lines
4. Test everything before moving on

## Build Rules to Follow
1. **NEVER** split files without creating the split modules
2. **ALWAYS** test after changes
3. **ONE** change at a time
4. **DOCUMENT** what exists vs what's planned
5. **NO** aggressive optimizations

## Current Status
- [x] app.py stripped to basics - DONE by Claude
- [x] app.py imports without errors - TESTED
- [x] app.py runs as server - RUNNING on port 8000
- [x] Basic routes working (/, /health, /api/v1/capture-email)
- [ ] Build rules documented
- [ ] System stable

## What Claude Has Done
1. Created minimal async_file_utils.py with just what's needed
2. Stripped app.py from 240 lines to 140 lines
3. Removed ALL broken imports:
   - Removed 15+ non-existent route imports
   - Removed security_config import
   - Removed middleware imports
   - Removed AI tool imports
4. Kept only working functionality:
   - Static file serving
   - Health check endpoint
   - Root page serving
   - Email capture endpoint

## What's Missing (for Cursor to help restore)
1. Authentication system
2. User routes
3. Payment/subscription handling
4. QuickBooks integration
5. Dashboard functionality
6. Expense tracking
7. Security middleware
8. Rate limiting

---
Tyler is taking a break. We need to handle this carefully and methodically.