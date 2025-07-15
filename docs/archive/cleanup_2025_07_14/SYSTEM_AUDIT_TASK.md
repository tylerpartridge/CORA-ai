# 🔍 DEEP SYSTEM AUDIT - Collaborative Task

## Mission
Tyler needs a complete picture of what's working vs what's broken in CORA V4. No fixing, no new tools - just intelligence gathering.

## Division of Labor

### Claude will audit:
1. **Core Application**
   - app.py functionality
   - Web interface status  
   - API endpoints
   - Database connections
   
2. **Missing Dependencies**
   - Broken imports
   - Missing route files
   - Dead references

3. **Data Flow**
   - What data exists
   - Where it's stored
   - If it's accessible

### Cursor will audit:
1. **Tools & Scripts**
   - Which tools actually work
   - Which have missing dependencies
   - Which are useful vs overhead
   
2. **Configuration & Setup**
   - Environment setup
   - Required packages
   - Configuration files
   
3. **Testing & Quality**
   - What tests exist
   - Health check functionality
   - Monitoring capabilities

## Audit Method
- Test each component individually
- Document: Works ✓ / Broken ✗ / Partial ⚠️
- Note dependencies and connections
- No fixing during audit - just document

## Output Format
Create ONE file: `SYSTEM_AUDIT_RESULTS.md` with:
- Executive summary (what % is working)
- Critical breaks that block progress
- Working components we can build on
- Detailed findings from both assistants

## Status
- [ ] Claude begins audit
- [ ] Cursor begins audit  
- [ ] Results combined
- [ ] Summary delivered

---
Start now. Work in parallel. Report findings.