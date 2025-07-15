# 🚀 QuickBooks App Registration Guide

## 🎯 Purpose
Set up QuickBooks OAuth credentials for CORA integration

## 📋 Prerequisites
- QuickBooks Developer Account (free)
- CORA production domain (for redirect URI)

## 🔧 Step-by-Step Setup

### 1. Create QuickBooks Developer Account
1. Go to [QuickBooks Developer Portal](https://developer.intuit.com/)
2. Sign up for free developer account
3. Verify email address

### 2. Create New App
1. Navigate to "My Apps" → "Create New App"
2. Choose "OAuth 2.0" as the app type
3. Fill in app details:
   - **App Name**: CORA AI Expense Sync
   - **Description**: AI-powered expense tracking with QuickBooks integration
   - **App Type**: Web App
   - **Environment**: Sandbox (for testing)

### 3. Configure OAuth Settings
1. Go to "Development" → "Keys" tab
2. Note down:
   - **Client ID**: `ABcDefGHijKLmnOPqrsTUVwxyz1234567890`
   - **Client Secret**: `your_client_secret_here`
3. Go to "Development" → "OAuth 2.0" tab
4. Add redirect URI: `https://cora.ai/api/integrations/quickbooks/callback`
5. Add scopes:
   - `com.intuit.quickbooks.accounting`
   - `com.intuit.quickbooks.payment`
   - `openid`
   - `profile`
   - `email`

### 4. Generate Basic Auth Header
```bash
# Combine client_id:client_secret and base64 encode
echo -n "ABcDefGHijKLmnOPqrsTUVwxyz1234567890:your_client_secret_here" | base64
# Result: QUJjRGVmR0hpakpMbm5PUHFyc1RVVnd4eXoxMjM0NTY3ODkwOnlvdXJfY2xpZW50X3NlY3JldF9oZXJl
```

### 5. Environment Variables
Add to `.env.production`:
```env
# QuickBooks OAuth Configuration
QUICKBOOKS_CLIENT_ID=ABcDefGHijKLmnOPqrsTUVwxyz1234567890
QUICKBOOKS_CLIENT_SECRET=your_client_secret_here
QUICKBOOKS_BASIC_AUTH=QUJjRGVmR0hpakpMbm5PUHFyc1RVVnd4eXoxMjM0NTY3ODkwOnlvdXJfY2xpZW50X3NlY3JldF9oZXJl
QUICKBOOKS_REDIRECT_URI=https://cora.ai/api/integrations/quickbooks/callback

# QuickBooks API URLs
QUICKBOOKS_AUTH_URL=https://appcenter.intuit.com/connect/oauth2
QUICKBOOKS_TOKEN_URL=https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer
QUICKBOOKS_API_URL=https://sandbox-quickbooks.api.intuit.com/v3/company
QUICKBOOKS_USERINFO_URL=https://sandbox-accounts.platform.intuit.com/v1/openid_connect/userinfo
```

## 🧪 Testing Setup

### 1. Test OAuth Flow
```bash
# Start CORA server
python app.py

# Visit QuickBooks integration page
curl http://localhost:8000/integrations/quickbooks

# Test auth endpoint
curl http://localhost:8000/api/integrations/quickbooks/auth
```

### 2. Expected OAuth Flow
1. User clicks "Connect QuickBooks"
2. Redirected to QuickBooks authorization
3. User authorizes CORA
4. Redirected back to `/api/integrations/quickbooks/callback`
5. CORA exchanges code for tokens
6. User redirected to dashboard with success message

## 🔒 Security Considerations

### 1. Environment Variables
- ✅ Store credentials in environment variables
- ✅ Never commit secrets to git
- ✅ Use different credentials for dev/staging/prod

### 2. OAuth Security
- ✅ Validate state parameter (CSRF protection)
- ✅ Use HTTPS for all OAuth endpoints
- ✅ Implement token refresh logic
- ✅ Store tokens securely (encrypted)

### 3. API Security
- ✅ Rate limiting on OAuth endpoints
- ✅ Validate user permissions
- ✅ Log OAuth events for audit

## 🚨 Troubleshooting

### Common Issues:
1. **Invalid Redirect URI**: Ensure exact match in QuickBooks app settings
2. **Invalid Client ID**: Check environment variable is set correctly
3. **Token Refresh Failures**: Verify Basic Auth header format
4. **Sandbox vs Production**: Use sandbox URLs for testing

### Debug Commands:
```bash
# Check environment variables
echo $QUICKBOOKS_CLIENT_ID

# Test Basic Auth format
echo -n "client_id:client_secret" | base64

# Verify redirect URI
curl -I "https://appcenter.intuit.com/connect/oauth2?client_id=YOUR_ID&response_type=code&scope=com.intuit.quickbooks.accounting&redirect_uri=https://cora.ai/api/integrations/quickbooks/callback"
```

## 📊 Production Checklist

- [ ] QuickBooks app created and configured
- [ ] OAuth credentials generated
- [ ] Environment variables set
- [ ] Redirect URI configured
- [ ] Scopes added
- [ ] Basic Auth header generated
- [ ] OAuth flow tested
- [ ] Token refresh tested
- [ ] Error handling verified
- [ ] Security measures implemented

## 🔄 Next Steps

1. **Update Code**: Replace hardcoded values with environment variables
2. **Test Integration**: Complete OAuth flow end-to-end
3. **Deploy**: Add credentials to production environment
4. **Monitor**: Set up logging for OAuth events
5. **Scale**: Prepare for production QuickBooks app

---

**Status**: 🟡 IN PROGRESS - App registration guide created
**Next**: Update code to use environment variables 