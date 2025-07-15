# QuickBooks App Registration Guide

## 🚀 Overview
This guide walks you through setting up a QuickBooks app for CORA integration.

## 📋 Prerequisites
- QuickBooks developer account
- Access to CORA's production URL (for redirect URI)

## 🔧 Step 1: Create QuickBooks Developer Account
1. Go to https://developer.intuit.com
2. Click "Sign Up" and create a developer account
3. Verify your email address

## 🎯 Step 2: Create a New App
1. Log in to the QuickBooks Developer Dashboard
2. Click "Create an app"
3. Select "QuickBooks Online"
4. Fill in app details:
   - **App Name**: CORA Expense Tracker
   - **Description**: AI-powered expense tracking and management
   - **Company**: Your company name
   - **Email**: Support email address

## 🔐 Step 3: Configure OAuth Settings
1. In your app settings, go to "Keys & OAuth"
2. Select environment:
   - **Development** (for testing)
   - **Production** (for live users)
3. Configure Redirect URIs:
   ```
   Development:
   - http://localhost:8000/api/integrations/quickbooks/callback
   
   Production:
   - https://your-app.railway.app/api/integrations/quickbooks/callback
   ```
4. Configure Scopes:
   - ✅ Accounting

## 🗝️ Step 4: Get Your Credentials
1. From "Keys & OAuth" page, copy:
   - **Client ID**: Your app's unique identifier
   - **Client Secret**: Your app's secret key (keep secure!)
2. Generate Basic Auth header:
   ```bash
   echo -n "CLIENT_ID:CLIENT_SECRET" | base64
   ```

## 🌍 Step 5: Environment Configuration
Create or update your `.env` file:

```env
# QuickBooks OAuth Configuration
QUICKBOOKS_CLIENT_ID=your_client_id_here
QUICKBOOKS_CLIENT_SECRET=your_client_secret_here
QUICKBOOKS_BASIC_AUTH=your_base64_encoded_credentials
QUICKBOOKS_REDIRECT_URI=https://your-app.railway.app/api/integrations/quickbooks/callback
QUICKBOOKS_ENVIRONMENT=sandbox  # or production

# API URLs (automatically set based on environment)
# Sandbox: https://sandbox-quickbooks.api.intuit.com
# Production: https://quickbooks.api.intuit.com
```

## 🧪 Step 6: Test Your Integration
1. **Sandbox Testing**:
   - Use QuickBooks Sandbox Company
   - Test data doesn't affect real accounting
   - Perfect for development

2. **Production Testing**:
   - Use a test company first
   - Verify all sync operations
   - Monitor error logs

## 📊 Step 7: Configure Webhooks (Optional)
For real-time sync updates:
1. Go to "Webhooks" in app settings
2. Add webhook endpoint:
   ```
   https://your-app.railway.app/api/integrations/quickbooks/webhook
   ```
3. Select events:
   - ✅ Purchase created
   - ✅ Purchase updated
   - ✅ Purchase deleted

## 🚨 Important Security Notes
1. **Never commit credentials** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate secrets** if compromised
4. **Use HTTPS** in production
5. **Validate webhook signatures** for security

## 🔄 Token Management
- Access tokens expire after **1 hour**
- Refresh tokens are valid for **100 days**
- CORA automatically refreshes tokens when needed
- Monitor token refresh failures in logs

## 📱 App Review Process
For production use with >100 companies:
1. Submit app for review
2. Provide test credentials
3. Document use cases
4. Wait 5-7 business days

## 🆘 Troubleshooting
### Common Issues:
1. **Invalid redirect URI**: Ensure exact match with configured URI
2. **Scope errors**: Check requested scopes match app configuration
3. **Token refresh failures**: Verify refresh token hasn't expired
4. **Rate limits**: Implement exponential backoff

### Debug Mode:
Add to `.env` for detailed logging:
```env
QUICKBOOKS_DEBUG=true
```

## 📚 Resources
- [QuickBooks API Documentation](https://developer.intuit.com/app/developer/qbo/docs/get-started)
- [OAuth 2.0 Flow](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0)
- [API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account)
- [Sandbox Companies](https://developer.intuit.com/app/developer/qbo/docs/develop/sandboxes/manage-your-sandboxes)

## ✅ Checklist Before Going Live
- [ ] App created in QuickBooks Developer Dashboard
- [ ] OAuth credentials configured
- [ ] Redirect URIs set correctly
- [ ] Environment variables added
- [ ] Sandbox testing completed
- [ ] Error handling implemented
- [ ] Token refresh logic tested
- [ ] Webhook signatures validated
- [ ] Rate limiting implemented
- [ ] Production app review (if needed)