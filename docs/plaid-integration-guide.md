# Plaid Integration Guide

## Overview

CORA's Plaid integration allows you to automatically sync transactions from your bank accounts, providing real-time expense tracking and categorization without manual data entry.

## Features

- **Secure Bank Connection**: OAuth-style connection using Plaid Link
- **Multi-Account Support**: Connect checking, savings, and credit card accounts
- **Automatic Transaction Sync**: Import transactions with smart categorization
- **Real-time Updates**: Sync transactions as they happen
- **Comprehensive History**: Track all synchronization activities
- **Error Handling**: Robust error handling and retry mechanisms

## Setup Instructions

### 1. Plaid App Registration

1. **Create Plaid Account**:
   - Go to [Plaid Dashboard](https://dashboard.plaid.com/)
   - Sign up for a developer account
   - Complete verification process

2. **Create App**:
   - Go to "Apps" section
   - Click "Create App"
   - Name: "CORA AI Integration"
   - Description: "AI-powered expense tracking integration"

3. **Configure Settings**:
   - Go to "Settings" tab
   - Add redirect URI: `https://cora.ai/integrations/plaid`
   - For development: `http://localhost:8000/integrations/plaid`
   - Enable required products: Transactions

4. **Get Credentials**:
   - Copy your `Client ID` and `Secret`
   - These will be used in environment variables

### 2. Environment Configuration

Add these variables to your `.env` file:

```bash
# Plaid Configuration
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret

# Environment (Sandbox for testing, Production for live)
PLAID_ENVIRONMENT=sandbox
```

### 3. Database Migration

The Plaid integration requires new database tables. Run the migration:

```bash
# Create migration file
alembic revision --autogenerate -m "Add Plaid integration tables"

# Apply migration
alembic upgrade head
```

### 4. Install Dependencies

Add Plaid SDK to requirements:

```bash
pip install plaid-python
```

## API Endpoints

### Authentication

- `POST /api/integrations/plaid/link-token` - Create Plaid link token
- `POST /api/integrations/plaid/access-token` - Exchange public token for access token

### Integration Management

- `GET /api/integrations/plaid/status` - Get connection status
- `GET /api/integrations/plaid/accounts` - Get connected accounts
- `DELETE /api/integrations/plaid/disconnect` - Disconnect integration

### Transaction Sync

- `POST /api/integrations/plaid/sync` - Sync transactions
- `GET /api/integrations/plaid/transactions` - Get recent transactions
- `GET /api/integrations/plaid/sync/history` - Get sync history

## Usage

### 1. Connect Bank Account

1. Navigate to `/integrations/plaid`
2. Click "Connect Bank Account"
3. Select your bank from Plaid's secure interface
4. Enter your credentials (handled securely by Plaid)
5. Select accounts to connect
6. You'll be redirected back with a successful connection

### 2. Sync Transactions

1. **Manual Sync**: Click "Sync Transactions" to import recent transactions
2. **Automatic Sync**: Transactions sync automatically every 24 hours
3. **Real-time**: New transactions sync within minutes

### 3. View and Manage

- **Account List**: View all connected bank accounts with balances
- **Transaction List**: View all imported bank transactions
- **Sync History**: Monitor sync activities and errors
- **Statistics**: Track total synced amount and transaction count

## Data Mapping

### Transaction Fields

| Plaid Field | CORA Field | Notes |
|-------------|------------|-------|
| `transaction_id` | `plaid_transaction_id` | Unique identifier |
| `amount` | `amount` | Negative for expenses |
| `iso_currency_code` | `currency` | ISO currency code |
| `name` | `description` | Transaction description |
| `merchant_name` | `vendor` | Merchant information |
| `date` | `date` | Transaction date |
| `category` | `category` | Plaid category array |

### Category Mapping

CORA automatically categorizes transactions based on:

1. **Plaid Categories**: Use Plaid's built-in categorization
2. **Merchant Analysis**: Pattern matching on merchant names
3. **Default**: Fallback to "Office Supplies"

Common mappings:
- `Food and Drink` → Meals & Entertainment
- `Shopping` → Office Supplies
- `Transportation` → Transportation
- `Travel` → Travel
- `Bills and Utilities` → Utilities
- `Entertainment` → Meals & Entertainment
- `Professional Services` → Professional Services
- `Education` → Professional Development

## Security Considerations

### Plaid Security

- **OAuth Flow**: Secure token exchange process
- **Token Storage**: Access tokens encrypted in production
- **Data Encryption**: All data encrypted in transit and at rest
- **Scope Limitation**: Only transaction data accessed

### Data Protection

- **Encryption**: Sensitive data encrypted at rest
- **Access Control**: User-specific data isolation
- **Audit Trail**: Complete sync history tracking
- **Error Handling**: Secure error messages

## Troubleshooting

### Common Issues

1. **Link Token Error**: Check Plaid app configuration
2. **Access Token Expired**: Automatic refresh should handle this
3. **Sync Failures**: Check bank account permissions
4. **Missing Transactions**: Verify account selection

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('plaid').setLevel(logging.DEBUG)
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

1. **Rate Limiting**: Respect Plaid API limits
2. **Error Handling**: Implement comprehensive error handling
3. **Logging**: Log all sync activities
4. **Testing**: Test with Plaid sandbox first

## Testing

### Sandbox Mode

Use Plaid sandbox for development:

1. Use sandbox credentials in Plaid dashboard
2. Test with sandbox bank accounts
3. Verify sync functionality
4. Test error scenarios

### Test Data

Sample test transaction:

```json
{
  "transaction_id": "test_transaction_123",
  "account_id": "test_account_456",
  "amount": -25.50,
  "iso_currency_code": "USD",
  "date": "2025-01-14",
  "name": "STARBUCKS COFFEE",
  "merchant_name": "STARBUCKS COFFEE",
  "category": ["Food and Drink", "Restaurants"],
  "pending": false
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
2. Verify bank account permissions
3. Test connection functionality
4. Contact support with error details

## Future Enhancements

- **Webhook Support**: Real-time transaction updates
- **Advanced Categorization**: Machine learning improvements
- **Bulk Operations**: Mass transaction management
- **Analytics**: Integration-specific insights
- **Multi-currency**: Enhanced currency support
- **Account Aggregation**: Multiple bank support per user

## Cost Considerations

### Plaid Pricing

- **Development**: Free sandbox access
- **Production**: Pay-per-transaction model
- **Volume Discounts**: Available for high-volume users
- **Enterprise**: Custom pricing for large deployments

### Cost Optimization

1. **Efficient Syncing**: Only sync necessary date ranges
2. **Batch Operations**: Group multiple requests
3. **Caching**: Cache frequently accessed data
4. **Monitoring**: Track API usage and costs

## Integration with Other Services

### QuickBooks Integration

- **Unified Data**: Bank transactions sync to QuickBooks
- **Vendor Matching**: Automatic vendor creation
- **Category Mapping**: Consistent categorization across platforms

### Stripe Integration

- **Payment Tracking**: Track Stripe payments alongside bank transactions
- **Reconciliation**: Match payments with bank deposits
- **Complete Picture**: Full financial visibility

## Compliance

### Data Privacy

- **GDPR Compliance**: User data protection
- **CCPA Compliance**: California privacy requirements
- **SOC 2**: Security and availability standards
- **PCI DSS**: Payment card industry compliance

### Audit Requirements

- **Transaction Logging**: Complete audit trail
- **Access Controls**: User permission management
- **Data Retention**: Configurable retention policies
- **Compliance Reporting**: Automated compliance reports 