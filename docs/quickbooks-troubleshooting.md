# QuickBooks Integration Troubleshooting Guide

## 🔍 Overview
This guide helps diagnose and resolve common issues with the CORA QuickBooks integration.

## 🚨 Common Issues & Solutions

### 1. OAuth Authentication Issues

#### Problem: "Invalid redirect URI" error
**Symptoms:**
- Error during OAuth flow
- User redirected to error page
- Message: "The redirect_uri does not match"

**Solution:**
1. Verify redirect URI in QuickBooks app matches exactly:
   ```
   Development: http://localhost:8000/api/integrations/quickbooks/callback
   Production: https://your-app.railway.app/api/integrations/quickbooks/callback
   ```
2. Check for trailing slashes (they matter!)
3. Ensure HTTPS in production
4. Update `.env` file:
   ```env
   QUICKBOOKS_REDIRECT_URI=<exact_uri_from_quickbooks_app>
   ```

#### Problem: "Invalid client" error
**Symptoms:**
- OAuth flow fails immediately
- Error: "client_id is invalid"

**Solution:**
1. Verify CLIENT_ID in `.env` matches QuickBooks app
2. Check you're using correct environment (sandbox vs production)
3. Regenerate credentials if needed:
   ```bash
   echo -n "CLIENT_ID:CLIENT_SECRET" | base64
   ```

### 2. Token Management Issues

#### Problem: Token expired
**Symptoms:**
- API calls return 401 Unauthorized
- Sync operations fail
- Last sync error: "Invalid auth token"

**Solution:**
1. Check token expiration:
   ```python
   python tools/quickbooks_sync_monitor.py --health
   ```
2. Force token refresh:
   ```sql
   UPDATE quickbooks_integrations 
   SET token_expires_at = NOW() 
   WHERE user_id = <user_id>;
   ```
3. Monitor automatic refresh in logs

#### Problem: Refresh token expired
**Symptoms:**
- Token refresh fails
- User needs to re-authenticate
- Error: "Refresh token is invalid"

**Solution:**
1. Refresh tokens expire after 100 days of inactivity
2. User must re-authenticate through OAuth flow
3. Set up monitoring alerts for tokens expiring soon

### 3. Sync Operation Failures

#### Problem: Expenses not syncing
**Symptoms:**
- Expenses remain unsynced
- No QuickBooks ID assigned
- Sync history shows failures

**Diagnosis:**
```bash
# Check sync status
python tools/quickbooks_sync_monitor.py

# View specific errors
SELECT error_message, COUNT(*) 
FROM quickbooks_sync_history 
WHERE quickbooks_status = 'error' 
GROUP BY error_message;
```

**Common Causes & Solutions:**

**a) Invalid category mapping**
- Error: "Account not found"
- Solution: Verify category mappings in `quickbooks_service.py`
- Check QuickBooks Chart of Accounts

**b) Missing vendor**
- Error: "Failed to create vendor"
- Solution: Check vendor name length (<= 100 chars)
- Remove special characters from vendor names

**c) Rate limiting**
- Error: "Too many requests"
- Solution: Implement exponential backoff
- Reduce batch size
- Check rate limit headers

### 4. Data Mapping Issues

#### Problem: Wrong account assignments
**Symptoms:**
- Expenses in wrong QuickBooks categories
- Accounting discrepancies

**Solution:**
1. Review category mappings:
   ```python
   # In services/quickbooks_service.py
   CATEGORY_MAPPING = {
       "CORA Category": "QuickBooks Account"
   }
   ```
2. Update mappings based on Chart of Accounts
3. Re-sync affected expenses

#### Problem: Duplicate expenses
**Symptoms:**
- Same expense appears multiple times in QuickBooks
- Inflated expense totals

**Solution:**
1. Check for duplicate sync attempts
2. Implement idempotency:
   ```sql
   SELECT expense_id, COUNT(*) 
   FROM quickbooks_sync_history 
   WHERE quickbooks_status = 'success' 
   GROUP BY expense_id 
   HAVING COUNT(*) > 1;
   ```
3. Add unique constraint on expense_id in sync tracking

### 5. Performance Issues

#### Problem: Slow sync operations
**Symptoms:**
- Sync takes > 5 seconds per expense
- Timeouts during batch sync
- Poor user experience

**Diagnosis:**
```bash
# Check average sync duration
SELECT AVG(sync_duration) as avg_ms 
FROM quickbooks_sync_history 
WHERE created_at > NOW() - INTERVAL '24 hours';
```

**Solutions:**
1. **Optimize API calls:**
   - Batch vendor lookups
   - Cache frequently used data
   - Use parallel requests where possible

2. **Database optimization:**
   - Add indexes on frequently queried columns
   - Vacuum and analyze tables regularly

3. **Implement queuing:**
   - Use background jobs for sync
   - Process in smaller batches
   - Add progress tracking

### 6. Connection Issues

#### Problem: Cannot connect to QuickBooks
**Symptoms:**
- Test connection fails
- All API calls timeout
- Network errors

**Testing:**
```bash
# Test QuickBooks API connectivity
curl -H "Accept: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     https://sandbox-quickbooks.api.intuit.com/v3/company/REALM_ID/companyinfo/1

# Test from Python
python tests/test_quickbooks_oauth.py
```

**Solutions:**
1. Check network connectivity
2. Verify API URLs (sandbox vs production)
3. Check firewall/proxy settings
4. Validate SSL certificates

### 7. Webhook Issues

#### Problem: Webhooks not received
**Symptoms:**
- Real-time sync not working
- Changes in QuickBooks not reflected

**Solution:**
1. Verify webhook URL is publicly accessible
2. Check webhook signature validation
3. Monitor webhook endpoint logs
4. Test with webhook tester:
   ```bash
   curl -X POST https://your-app.com/api/integrations/quickbooks/webhook \
        -H "Content-Type: application/json" \
        -d '{"test": "payload"}'
   ```

## 🛠️ Diagnostic Tools

### 1. QuickBooks Sync Monitor
```bash
# Full dashboard
python tools/quickbooks_sync_monitor.py

# Health check only
python tools/quickbooks_sync_monitor.py --health

# Export metrics
python tools/quickbooks_sync_monitor.py --export

# Continuous monitoring
python tools/quickbooks_sync_monitor.py --continuous
```

### 2. OAuth Test Script
```bash
# Validate OAuth configuration
python tests/test_quickbooks_oauth.py

# Run integration tests
pytest tests/test_quickbooks_integration.py -v
```

### 3. Database Queries
```sql
-- Check integration status
SELECT * FROM quickbooks_integrations WHERE user_id = ?;

-- Recent sync errors
SELECT * FROM quickbooks_sync_history 
WHERE quickbooks_status = 'error' 
ORDER BY created_at DESC LIMIT 10;

-- Token expiration check
SELECT user_id, company_name, token_expires_at 
FROM quickbooks_integrations 
WHERE is_active = true 
AND token_expires_at < NOW() + INTERVAL '7 days';
```

## 📊 Monitoring Checklist

### Daily Checks
- [ ] Token expiration status
- [ ] Sync success rate > 95%
- [ ] Average sync duration < 2000ms
- [ ] No critical errors in logs

### Weekly Checks
- [ ] Unsynced expense count
- [ ] Stale integrations (no sync > 7 days)
- [ ] Webhook delivery rate
- [ ] API rate limit usage

### Monthly Checks
- [ ] Refresh token expiration dates
- [ ] Category mapping accuracy
- [ ] Performance trending
- [ ] User satisfaction metrics

## 🔧 Advanced Troubleshooting

### Enable Debug Logging
```python
# In .env
QUICKBOOKS_DEBUG=true
LOG_LEVEL=DEBUG

# In code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### API Request Inspection
```python
# Add request logging
import requests
import logging

# Enable request debugging
logging.getLogger('requests').setLevel(logging.DEBUG)
logging.getLogger('urllib3').setLevel(logging.DEBUG)
```

### Manual Token Refresh
```python
from services.quickbooks_service import QuickBooksService
from models import QuickBooksIntegration

# Get integration
integration = session.query(QuickBooksIntegration).filter_by(user_id=123).first()

# Force refresh
service = QuickBooksService(integration)
success = service._refresh_token_if_needed()
```

## 🆘 Getting Help

### Error Reporting Template
When reporting issues, include:
1. Error message (exact)
2. Timestamp
3. User ID / Integration ID
4. Recent actions taken
5. Sync monitor output
6. Relevant logs

### Support Resources
- QuickBooks API Status: https://developer.intuit.com/status
- API Documentation: https://developer.intuit.com/app/developer/qbo/docs
- Community Forum: https://help.developer.intuit.com/s/
- CORA Support: support@cora.ai

## 🔄 Recovery Procedures

### Full Re-sync Procedure
1. Backup current sync history
2. Mark all expenses as unsynced
3. Reset sync counters
4. Run batch sync with monitoring
5. Verify accuracy

### Integration Reset
1. Deactivate current integration
2. Clear stored tokens
3. Re-authenticate user
4. Import sync history
5. Resume normal operations

## 📈 Prevention Best Practices

1. **Implement monitoring alerts** for token expiration
2. **Use retry logic** with exponential backoff
3. **Cache frequently accessed data** (vendors, accounts)
4. **Validate data before sync** to prevent errors
5. **Regular health checks** via monitoring dashboard
6. **Document custom mappings** and business rules
7. **Test in sandbox** before production changes