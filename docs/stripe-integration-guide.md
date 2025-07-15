# Stripe Integration Guide

## Overview

CORA's Stripe integration allows you to automatically sync transactions from your Stripe account, eliminating manual expense entry and providing real-time financial insights.

## Features

- **OAuth Authentication**: Secure connection using Stripe Connect
- **Automatic Transaction Sync**: Import charges and payments automatically
- **Smart Categorization**: AI-powered expense categorization
- **Real-time Updates**: Sync transactions as they happen
- **Sync History**: Track all synchronization activities
- **Error Handling**: Robust error handling and retry mechanisms

## Setup Instructions

### 1. Stripe App Registration

1. **Create Stripe App**:
   - Go to [Stripe Dashboard](https://dashboard.stripe.com/applications)
   - Click "Create application"
   - Name: "CORA AI Integration"
   - Description: "AI-powered bookkeeping integration"

2. **Configure OAuth Settings**:
   - Go to "OAuth" tab
   - Add redirect URI: `https://cora.ai/api/integrations/stripe/callback`
   - For development: `http://localhost:8000/api/integrations/stripe/callback`
   - Save changes

3. **Get Credentials**:
   - Copy your `Client ID` and `Client Secret`
   - These will be used in environment variables

### 2. Environment Configuration

Add these variables to your `.env` file:

```bash
# Stripe OAuth Configuration
STRIPE_CLIENT_ID=your_stripe_client_id
STRIPE_CLIENT_SECRET=your_stripe_client_secret
STRIPE_REDIRECT_URI=https://cora.ai/api/integrations/stripe/callback

# For development
STRIPE_REDIRECT_URI=http://localhost:8000/api/integrations/stripe/callback
```

### 3. Database Migration

The Stripe integration requires new database tables. Run the migration:

```bash
# Create migration file
alembic revision --autogenerate -m "Add Stripe integration tables"

# Apply migration
alembic upgrade head
```

### 4. Install Dependencies

Add Stripe SDK to requirements:

```bash
pip install stripe
```

## API Endpoints

### Authentication

- `GET /api/integrations/stripe/auth` - Get OAuth authorization URL
- `GET /api/integrations/stripe/callback` - Handle OAuth callback

### Integration Management

- `GET /api/integrations/stripe/status` - Get connection status
- `DELETE /api/integrations/stripe/disconnect` - Disconnect integration

### Transaction Sync

- `POST /api/integrations/stripe/sync` - Sync transactions
- `GET /api/integrations/stripe/transactions` - Get recent transactions
- `GET /api/integrations/stripe/sync/history` - Get sync history

## Usage

### 1. Connect Stripe Account

1. Navigate to `/integrations/stripe`
2. Click "Connect Stripe"
3. Authorize CORA to access your Stripe account
4. You'll be redirected back with a successful connection

### 2. Sync Transactions

1. **Manual Sync**: Click "Sync Transactions" to import recent charges
2. **Automatic Sync**: Transactions sync automatically every 24 hours
3. **Real-time**: New transactions sync within minutes

### 3. View and Manage

- **Transaction List**: View all imported Stripe transactions
- **Sync History**: Monitor sync activities and errors
- **Statistics**: Track total synced amount and transaction count

## Data Mapping

### Transaction Fields

| Stripe Field | CORA Field | Notes |
|--------------|------------|-------|
| `charge.id` | `stripe_transaction_id` | Unique identifier |
| `charge.amount` | `amount` | Converted from cents |
| `charge.currency` | `currency` | ISO currency code |
| `charge.description` | `description` | Transaction description |
| `charge.receipt_url` | `receipt_url` | Link to receipt |
| `charge.created` | `created_at` | Transaction timestamp |
| `charge.metadata` | `metadata` | JSON string |

### Category Mapping

CORA automatically categorizes transactions based on:

1. **Metadata**: Check for `category` in Stripe metadata
2. **Description**: Pattern matching on transaction description
3. **Default**: Fallback to "Office Supplies"

Common mappings:
- `office`, `supplies` → Office Supplies
- `food`, `lunch`, `restaurant` → Meals & Entertainment
- `uber`, `lyft`, `taxi` → Transportation
- `software`, `subscription` → Software & Subscriptions
- `advertising`, `marketing` → Marketing & Advertising

## Security Considerations

### OAuth Security

- **State Parameter**: CSRF protection using user ID
- **Token Storage**: Access tokens encrypted in production
- **Token Refresh**: Automatic refresh before expiration
- **Scope Limitation**: Only `read_write` scope requested

### Data Protection

- **Encryption**: Sensitive data encrypted at rest
- **Access Control**: User-specific data isolation
- **Audit Trail**: Complete sync history tracking
- **Error Handling**: Secure error messages

## Troubleshooting

### Common Issues

1. **OAuth Error**: Check redirect URI configuration
2. **Token Expired**: Automatic refresh should handle this
3. **Sync Failures**: Check Stripe account permissions
4. **Missing Transactions**: Verify charge permissions

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('stripe').setLevel(logging.DEBUG)
```

### Error Codes

- `400`: Bad request (invalid parameters)
- `401`: Unauthorized (token issues)
- `403`: Forbidden (insufficient permissions)
- `500`: Internal server error

## Best Practices

### For Users

1. **Regular Syncs**: Run manual syncs weekly
2. **Monitor History**: Check sync history for errors
3. **Verify Categories**: Review auto-categorized expenses
4. **Keep Connected**: Don't disconnect unless necessary

### For Developers

1. **Rate Limiting**: Respect Stripe API limits
2. **Error Handling**: Implement comprehensive error handling
3. **Logging**: Log all sync activities
4. **Testing**: Test with Stripe test mode first

## Testing

### Test Mode

Use Stripe test mode for development:

1. Create test charges in Stripe dashboard
2. Use test API keys
3. Verify sync functionality
4. Test error scenarios

### Test Data

Sample test transaction:

```json
{
  "id": "ch_test_1234567890",
  "amount": 2500,
  "currency": "usd",
  "description": "Office supplies from Staples",
  "receipt_url": "https://receipt.stripe.com/test/...",
  "created": 1640995200,
  "metadata": {
    "category": "Office Supplies"
  }
}
```

## Monitoring

### Key Metrics

- **Sync Success Rate**: Percentage of successful syncs
- **Transaction Volume**: Number of transactions synced
- **Error Rate**: Frequency of sync failures
- **Response Time**: API response times

### Alerts

Set up alerts for:
- High error rates
- Failed syncs
- Token refresh failures
- API rate limit approaching

## Support

For integration support:

1. Check sync history for errors
2. Verify Stripe account permissions
3. Test connection functionality
4. Contact support with error details

## Future Enhancements

- **Webhook Support**: Real-time transaction updates
- **Advanced Categorization**: Machine learning improvements
- **Bulk Operations**: Mass transaction management
- **Analytics**: Integration-specific insights
- **Multi-currency**: Enhanced currency support 