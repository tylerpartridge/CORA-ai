# 🧪 System Test Plan - Fresh Cursor Session

## Test Objectives
1. Verify Cursor can find coding conventions without .ai/ folder
2. Ensure bootup prompt gives right context quickly
3. Check if system is intuitive for daily use
4. Identify any context gaps or confusion points

## Test Steps
1. Close current Cursor chat
2. Open fresh Cursor session
3. Copy Cursor prompt from BOOTUP.md
4. Ask Cursor to:
   - Help create a new file following conventions
   - Check file size limits
   - Explain the navigation header format

## Success Criteria
- Cursor knows the rules without searching
- Can guide file creation properly
- Understands size limits
- No references to old .ai/ structure

## What to Watch For
- Confusion about file locations
- Missing critical information
- Too much/too little context
- Any friction in the workflow