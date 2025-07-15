# 🚀 CORA Production Launch Plan

*Created: 2025-07-15*  
*Status: READY FOR EXECUTION*  
*System State: BETA READY - All core features tested and working*

## 📊 Current Situation

### ✅ What's Complete
- **Full CRUD API System**: All endpoints operational
- **Authentication System**: Register, login, password reset working
- **Admin Dashboard**: Complete UI with analytics
- **Onboarding System**: Progress tracking and feedback collection
- **Database**: 15 expense categories, all tables created
- **Security Features**: Configured but disabled for stability
- **Testing**: Comprehensive test suite passing

### 🚨 Critical Blockers
1. **No Git Repository**: Code needs version control before deployment
2. **Production Server**: Running old code, needs update
3. **Security Middleware**: Disabled, needs activation post-deployment
4. **Monitoring**: Sentry configured but no DSN set

## 🎯 Immediate Action Plan (Next 24-48 Hours)

### Phase 1: Version Control & Deployment (Day 1)

#### Step 1: Initialize Git Repository
```bash
cd /mnt/host/c/CORA
git init
git add .
git commit -m "Initial commit: CORA Beta Ready System v4.0"

# Create GitHub repository first, then:
git remote add origin https://github.com/[username]/cora-ai.git
git push -u origin main
```

#### Step 2: Deploy to Production
Since git isn't set up yet, use the direct deployment script:

```bash
# From local machine
python tools/deploy_simple.py

# Or manually via SCP
scp -r * root@159.203.183.48:/var/www/cora/
```

#### Step 3: Update Production Server
```bash
ssh root@159.203.183.48
cd /var/www/cora

# Install/update dependencies
pip install -r requirements.txt

# Run database migrations
python init_db.py

# Restart application
pm2 restart cora
pm2 save
```

#### Step 4: Verify Deployment
- Test: https://coraai.tech/health
- Test: https://coraai.tech/api/status
- Test: https://coraai.tech/admin (with auth)

### Phase 2: Security & Monitoring (Day 1-2)

#### Step 5: Set Up Sentry
1. Create account at sentry.io
2. Create new project for CORA
3. Get DSN from project settings
4. Add to production environment:
   ```bash
   export SENTRY_DSN="https://[key]@sentry.io/[project]"
   ```
5. Restart PM2

#### Step 6: Enable Security Middleware
After confirming basic deployment works:

1. SSH to production server
2. Edit `/var/www/cora/app.py`
3. Uncomment these lines:
   ```python
   # === SECURITY & LOGGING MIDDLEWARE ===
   setup_rate_limiting(app)
   setup_security_headers(app)
   setup_request_logging(app)
   setup_error_handlers(app)
   setup_user_activity(app)
   ```
4. Restart: `pm2 restart cora`

#### Step 7: Configure Automated Backups
```bash
# On production server
crontab -e

# Add this line for daily 2am backups:
0 2 * * * /usr/bin/python3 /var/www/cora/tools/backup_db.py

# Test backup script manually first:
python3 /var/www/cora/tools/backup_db.py
```

### Phase 3: Production Hardening (Day 2)

#### Step 8: Create PM2 Ecosystem Config
Create `/var/www/cora/ecosystem.config.js`:

```javascript
module.exports = {
  apps: [{
    name: 'cora',
    script: 'app.py',
    interpreter: 'python3',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      ENVIRONMENT: 'production',
      DATABASE_URL: 'sqlite:///data/cora.db'
    },
    error_file: 'logs/pm2-error.log',
    out_file: 'logs/pm2-out.log',
    log_file: 'logs/pm2-combined.log',
    time: true
  }]
}
```

Then: `pm2 start ecosystem.config.js`

#### Step 9: Set Up External Monitoring
1. Sign up for UptimeRobot (free)
2. Add monitor for https://coraai.tech/health
3. Set check interval: 5 minutes
4. Add email/SMS alerts

#### Step 10: Enable 2FA on DigitalOcean
- Login to DigitalOcean
- Settings → Security → Two-Factor Authentication
- Enable and save backup codes

## 📈 Beta Launch Plan (Week 1)

### User Acquisition Strategy

#### Week 1 Goals
- **Target**: 20-30 beta users
- **Sources**: Existing beta recruitment list
- **Messaging**: "AI bookkeeper for introverted founders"

#### Immediate Actions
1. **Email Existing Beta List** (20 users tracked)
   - Send access credentials
   - Include beta user guide
   - Request feedback within 48 hours

2. **Activate Landing Page**
   - Ensure email capture works
   - Test lead generation form
   - Monitor captured_emails.json

3. **Content Marketing**
   - Post on Twitter/LinkedIn about beta launch
   - Share in relevant Discord/Slack communities
   - Focus on "no meetings required" angle

### Beta User Onboarding

#### Automated Flow
1. User registers → Welcome email (needs SendGrid verification)
2. First login → Onboarding checklist appears
3. Complete profile → Add first expense
4. Explore dashboard → Submit feedback

#### Manual Support
- Monitor admin dashboard daily
- Respond to feedback within 24 hours
- Track onboarding completion rates

## 📊 Success Metrics (First Week)

### Technical Metrics
- [ ] Zero 500 errors
- [ ] < 200ms average response time
- [ ] 99.9% uptime
- [ ] All security middleware active

### User Metrics
- [ ] 20+ beta users registered
- [ ] 50%+ onboarding completion
- [ ] 3+ average feedback rating
- [ ] 5+ user feedback submissions

### Business Metrics
- [ ] 10+ expenses tracked
- [ ] 3+ power users (>5 expenses)
- [ ] 1+ integration connected
- [ ] 5+ email captures for waitlist

## 🚨 Rollback Plan

If critical issues arise:

1. **Quick Rollback**:
   ```bash
   ssh root@159.203.183.48
   cd /var/www/cora
   git checkout HEAD~1  # (once git is set up)
   pm2 restart cora
   ```

2. **Database Backup Restore**:
   ```bash
   cp backups/cora_[timestamp].db data/cora.db
   pm2 restart cora
   ```

3. **Disable Problematic Features**:
   - Comment out middleware if causing issues
   - Disable specific endpoints if needed
   - Switch to maintenance mode if critical

## 📋 Daily Checklist (First Week)

### Morning (9 AM)
- [ ] Check uptime monitoring
- [ ] Review PM2 logs for errors
- [ ] Check Sentry for new issues
- [ ] Review admin dashboard metrics

### Afternoon (2 PM)
- [ ] Respond to user feedback
- [ ] Monitor onboarding completion
- [ ] Check database backup success
- [ ] Review security logs

### Evening (6 PM)
- [ ] Daily metrics summary
- [ ] Plan next day priorities
- [ ] Update team on progress
- [ ] Backup critical data

## 🎯 Week 2 Goals

Once stable with 20+ beta users:

1. **Scale to 50 users**
   - Broader marketing push
   - Referral incentives
   - Community building

2. **Feature Refinement**
   - Based on user feedback
   - Fix top 3 pain points
   - Add most requested feature

3. **Infrastructure Scaling**
   - Consider PostgreSQL migration
   - Add Redis for caching
   - Implement CDN for assets

## 📞 Emergency Contacts

- **Server Issues**: DigitalOcean support
- **Domain Issues**: Cloudflare support
- **Code Issues**: Check Sentry errors first
- **User Issues**: Monitor feedback endpoint

---

**Remember**: The system is FULLY TESTED and WORKING. Focus on smooth deployment and monitoring. Don't rush - stability over speed for beta launch.