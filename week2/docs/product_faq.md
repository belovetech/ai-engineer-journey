# NovaPay Product FAQ

## What is NovaPay?

NovaPay is a cloud-based payment processing platform designed for small and medium businesses. It handles credit card transactions, invoicing, and subscription billing through a single API and dashboard.

## Pricing Plans

### Starter Plan
- Monthly fee: $0/month
- Transaction fee: 2.9% + $0.30 per transaction
- Features: basic payment processing, email receipts, standard support
- Best for: businesses processing fewer than 500 transactions/month

### Pro Plan
- Monthly fee: $49/month
- Transaction fee: 2.4% + $0.25 per transaction
- Features: everything in Starter plus recurring billing, custom invoices, webhook integrations, priority support
- Best for: businesses processing 500-5,000 transactions/month

### Enterprise Plan
- Monthly fee: custom pricing
- Transaction fee: negotiable volume discounts
- Features: everything in Pro plus dedicated account manager, SLA guarantees, custom integrations, on-premise deployment option
- Best for: businesses processing over 5,000 transactions/month

## Refund and Return Policy

Refunds can be initiated within 90 days of the original transaction. To process a refund:
1. Log into the NovaPay dashboard
2. Navigate to Transactions > Find the transaction
3. Click "Issue Refund" and enter the refund amount (partial or full)
4. The refund typically appears on the customer's statement within 5-10 business days

NovaPay does not charge a fee for processing refunds, but the original transaction fee is not returned.

## Security

NovaPay is PCI DSS Level 1 certified. All card data is encrypted using AES-256 and tokenized before storage. We never store raw card numbers on our servers. Two-factor authentication is required for all dashboard access.

## API Rate Limits

- Starter: 100 requests/minute
- Pro: 500 requests/minute
- Enterprise: 2,000 requests/minute (configurable)

Exceeding the rate limit returns HTTP 429. Implement exponential backoff in your integration.

## Supported Countries

NovaPay currently operates in 34 countries across North America, Europe, and Asia-Pacific. Full country list is available at docs.novapay.com/countries. Expansion to Latin America is planned for Q3 2026.

## Contact Support

- Email: support@novapay.com
- Phone: 1-800-NOVAPAY (available Mon-Fri, 9am-6pm EST)
- Live chat: available on the dashboard for Pro and Enterprise customers
- Emergency line for Enterprise: 1-800-NOVA-911 (24/7)
