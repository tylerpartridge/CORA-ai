# 🚀 Cursor Beta Launch Execution Plan

*Generated: 2025-07-15*
*Purpose: Clear, actionable execution steps for Cursor to complete beta launch preparation*
*Status: Tasks 1-6 completed, Tasks 7-15 ready for execution*

## 📊 Progress Overview

### ✅ Completed Tasks (1-6)
1. **Production 502 Error** - Fixed with virtual environment setup
2. **Database Connection** - SQLite operational, PostgreSQL ready
3. **API Endpoints** - All verified and functional
4. **Environment Variables** - Production config complete
5. **Monitoring Setup** - Sentry and uptime checks active
6. **User Registration** - Full auth flow operational

### 🎯 Remaining Tasks (7-15)

---

## 🎯 Task 7: Create Dashboard UI (PRIORITY: HIGH)

**Context**: Users login successfully but have no dashboard to land on. The API endpoints exist but no UI.

**Execution Steps**:
1. Create `/web/templates/dashboard.html` using existing Bootstrap 5 pattern
2. Copy the layout from `login.html` or `index.html` as base
3. Include these sections:
   - Welcome message with user email (from JWT)
   - Expense summary cards (total spent, number of expenses, average)
   - Recent expenses table (last 10)
   - Quick add expense form
   - Navigation to categories, settings, logout
4. Add route in `/routes/pages.py`:
   ```python
   @router.get("/dashboard")
   async def dashboard(request: Request, current_user=Depends(get_current_user)):
       return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user})
   ```
5. Use the existing purple theme (#9B6EC8) and Bootstrap components

---

## 🎯 Task 8: Build Onboarding Checklist UI

**Context**: API endpoints exist at `/api/onboarding/` but no UI implementation.

**Execution Steps**:
1. Add onboarding section to the dashboard.html created above
2. Create a Bootstrap progress component showing:
   - Connect bank account (link to `/integrations/plaid`)
   - Add first expense
   - Set up categories
   - Configure notifications
3. Use JavaScript to fetch `/api/onboarding/checklist` and update progress
4. Show/hide based on onboarding completion status

---

## 🎯 Task 9: Add Feedback Widget

**Context**: Need user feedback mechanism for beta testing.

**Execution Steps**:
1. Create `/routes/feedback.py` with endpoint:
   ```python
   @router.post("/api/feedback")
   async def submit_feedback(feedback: dict, current_user=Depends(get_current_user))
   ```
2. Add floating feedback button to dashboard.html (bottom-right corner)
3. Create modal with feedback form (rating 1-5, text comment)
4. Store feedback in a new simple JSON file or database table

---

## 🎯 Task 10: Create Admin Dashboard UI

**Context**: Admin API endpoints exist but no UI to view the data.

**Execution Steps**:
1. Create `/web/templates/admin/dashboard.html`
2. Add admin route with authentication check (verify user is admin)
3. Display data from existing admin endpoints:
   - Total users, active users, new signups
   - System health status
   - User list with activity metrics
4. Use Bootstrap tables and cards for layout

---

## 🎯 Task 11: Implement User Activity Tracking

**Context**: Only basic timestamp tracking exists. Need better activity monitoring.

**Execution Steps**:
1. Create new model in `/models/` (add to existing file per CORA rules):
   ```python
   class UserActivity(Base):
       __tablename__ = "user_activity"
       id = Column(Integer, primary_key=True)
       user_email = Column(String, ForeignKey("users.email"))
       action = Column(String)  # login, add_expense, etc.
       timestamp = Column(DateTime, default=datetime.utcnow)
   ```
2. Add tracking calls to key endpoints (login, expense CRUD)
3. Update admin endpoints to include activity data

---

## 🎯 Task 12: Apply Security Middleware (CRITICAL)

**Context**: Security middleware exists but isn't connected to the app!

**Execution Steps**:
1. Open `/app.py`
2. Import the middleware:
   ```python
   from middleware.rate_limit import limiter
   from middleware.security_headers import SecurityHeadersMiddleware
   ```
3. Add after app initialization:
   ```python
   app.add_middleware(SecurityHeadersMiddleware)
   app.state.limiter = limiter
   ```
4. Test that headers appear in responses

---

## 🎯 Task 13: Configure CORS

**Context**: No CORS configuration exists, needed for API security.

**Execution Steps**:
1. In `/app.py`, add:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://coraai.tech"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
2. For development, add "http://localhost:8000" to allow_origins

---

## 🎯 Task 14: Create Database Backup Script

**Context**: No backup system exists.

**Execution Steps**:
1. Create `/tools/backup_database.py`:
   - For SQLite: Copy the .db file with timestamp
   - For PostgreSQL: Use pg_dump command
2. Add to cron on production server for daily backups
3. Store backups in `/backups/` directory with 7-day retention

---

## 🎯 Task 15: Enable 2FA on DigitalOcean

**Context**: Security best practice, requires manual action.

**Execution Steps**:
1. Login to DigitalOcean account
2. Go to Account Settings → Security
3. Enable Two-Factor Authentication
4. Save backup codes securely

---

## 📝 Implementation Notes

### Key Principles:
- **Edit First**: Always prefer editing existing files over creating new ones (CORA philosophy)
- **Use Existing Patterns**: Follow Bootstrap 5, purple theme (#9B6EC8), Jinja2 templates
- **Test Each Step**: Verify functionality before moving to next task
- **Security First**: Tasks 12-14 are critical for production safety

### File Organization:
- **Templates**: `/web/templates/` for all HTML files
- **Routes**: Add to existing route files when possible
- **Static Assets**: `/web/static/` for CSS, JS, images
- **Tools**: `/tools/` for utility scripts like backups

### Testing Commands:
```bash
# Local testing
python -m uvicorn app:app --reload

# Test endpoints
curl http://localhost:8000/api/expenses/categories
curl http://localhost:8000/health

# Deploy to production
ssh root@coraai.tech
cd /root/cora && git pull && pm2 restart cora
```

---

## 🎯 Success Criteria

Each task is complete when:
- Task 7: Users can see and interact with dashboard after login
- Task 8: Onboarding progress is visible and updates automatically
- Task 9: Beta users can submit feedback easily
- Task 10: Admins can view system and user statistics
- Task 11: User actions are tracked in the database
- Task 12: Security headers appear in all responses
- Task 13: CORS is properly configured for production domain
- Task 14: Database backups run automatically daily
- Task 15: 2FA is enabled on DigitalOcean account

---

*This document should be updated as tasks are completed. Each task has been designed to be self-contained and executable without additional planning.*