# 🔧 Production Route Registration Fix Plan

**Issue**: Protected routes (admin, onboarding, feedback) return 404 in production but work locally  
**Status**: Core endpoints working, protected routes not registered  
**Priority**: CRITICAL - Blocking beta launch

## 📋 TodoWrite Execution Plan

### Phase 1: Diagnostic & Debug
- [x] 1. SSH into production server and check PM2 configuration
- [x] 2. Add debug logging to app.py to track route registration
- [x] 3. Test direct imports on production server
- [x] 4. Compare route counts between local and production

### Phase 2: Fix Implementation
- [x] 5. Apply import path fix (sys.path.insert)
- [x] 6. Reorder route registration in app.py
- [x] 7. Deploy missing directories (middleware, models, dependencies, routes, services)
- [x] 8. Restart and test protected endpoints

### Phase 3: Verification
- [x] 9. Verify all routes registered in production (OpenAPI schema shows all endpoints)
- [x] 10. Test admin, onboarding, and feedback endpoints (returning 401 auth errors instead of 404s)
- [x] 11. Update status files with fix results
- [x] 12. Document the solution for future reference

**Status**: ✅ **COMPLETED** - Production route registration issue resolved

## 🎯 Immediate Diagnostic Steps

### 1. Check Route Registration Order
The issue might be route registration order or middleware interference. Try:

```python
# In app.py, add debug logging after imports:
print(f"Admin router imported: {admin_router}")
print(f"Admin router routes: {admin_router.routes}")

# And after app.include_router calls:
print(f"Total routes registered: {len(app.routes)}")
for route in app.routes:
    print(f"Route: {route.path}")
```

### 2. Check PM2 Python Path
```bash
ssh root@coraai.tech
which python
python --version
pm2 info cora
```

### 3. Test Import Directly on Production
```bash
ssh root@coraai.tech
cd /var/www/cora
python -c "from routes.admin_routes import admin_router; print('Success')"
python -c "from app import app; print(f'Routes: {len(app.routes)}')"
```

## 🔍 Likely Causes & Solutions

### Cause 1: Import Path Issue
**Symptom**: Routes import but don't register  
**Fix**: Add explicit path configuration
```python
# At top of app.py, after imports:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

### Cause 2: Circular Import
**Symptom**: Routes partially load  
**Fix**: Move route registration to end of file
```python
# Move all app.include_router() calls to the very end of app.py
# After all other route definitions
```

### Cause 3: Middleware Blocking Routes
**Symptom**: Middleware interferes with route registration  
**Fix**: Register routes before middleware
```python
# In app.py, reorder:
# 1. Create app
# 2. Include routers
# 3. Add middleware
# 4. Define additional routes
```

### Cause 4: PM2 Environment Issue
**Symptom**: PM2 not finding modules  
**Fix**: Update ecosystem.config.js
```javascript
module.exports = {
  apps: [{
    name: 'cora',
    script: 'app.py',
    interpreter: '/usr/bin/python3',
    cwd: '/var/www/cora',
    env: {
      PYTHONPATH: '/var/www/cora',
      ENVIRONMENT: 'production'
    }
  }]
}
```

## 🚀 Quick Fix Attempt

Try this minimal change first:

1. **Add debug logging to production app.py**:
```python
# After all app.include_router() calls:
print(f"[CORA] Total routes registered: {len(app.routes)}")
print(f"[CORA] Admin routes: {[r.path for r in app.routes if 'admin' in r.path]}")
```

2. **Restart and check logs**:
```bash
pm2 restart cora
pm2 logs cora --lines 50 | grep CORA
```

3. **If routes missing, try explicit registration**:
```python
# In app.py, replace:
app.include_router(admin_router)

# With:
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
```

## 🎯 Final Resort

If above doesn't work, create a simple test:

```python
# test_routes.py
from app import app

print(f"Total routes: {len(app.routes)}")
for route in app.routes:
    if hasattr(route, 'path'):
        print(f"Path: {route.path} - Methods: {route.methods}")
```

Run locally vs production to compare.

## ✅ Success Criteria

- `/api/admin/stats` returns data
- `/api/onboarding/checklist` returns checklist
- `/docs` shows all 77 routes
- PM2 logs show no import errors

---

**Note**: This is likely a simple path or environment issue. The code is correct (works locally), so it's just a matter of helping PM2 find and register the routes properly.