# NovaPay API Technical Specification

## Authentication

All API requests require a Bearer token in the Authorization header:

```
Authorization: Bearer sk_live_xxxxxxxxxxxx
```

API keys are generated in the dashboard under Settings > API Keys. Each key is scoped to either "live" (production) or "test" (sandbox). Test keys use the prefix `sk_test_` and live keys use `sk_live_`.

## Base URL

- Production: `https://api.novapay.com/v2`
- Sandbox: `https://sandbox.novapay.com/v2`

## Create a Payment

**POST** `/v2/payments`

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| amount | integer | yes | Amount in cents (e.g., 1000 = $10.00) |
| currency | string | yes | Three-letter ISO currency code (e.g., "usd") |
| payment_method | string | yes | Payment method token from client SDK |
| description | string | no | Description for the transaction |
| metadata | object | no | Key-value pairs for your own records |
| capture | boolean | no | Whether to capture immediately (default: true) |

### Example Request

```json
{
  "amount": 2500,
  "currency": "usd",
  "payment_method": "pm_1abc2def3ghi",
  "description": "Order #1234",
  "metadata": {
    "order_id": "1234",
    "customer_email": "jane@example.com"
  }
}
```

### Response

```json
{
  "id": "pay_9xyz8wvu7tsr",
  "status": "succeeded",
  "amount": 2500,
  "currency": "usd",
  "created_at": "2026-01-15T10:30:00Z",
  "fee": 103
}
```

The `fee` field shows the NovaPay processing fee in cents.

## Webhooks

NovaPay sends webhook events for state changes. Configure your endpoint in the dashboard under Settings > Webhooks.

### Supported Events

- `payment.succeeded` — payment completed successfully
- `payment.failed` — payment attempt failed
- `payment.refunded` — full or partial refund processed
- `subscription.created` — new subscription started
- `subscription.cancelled` — subscription cancelled
- `invoice.paid` — invoice paid by customer
- `invoice.overdue` — invoice past due date

### Webhook Signature Verification

Each webhook includes a `X-NovaPay-Signature` header. Verify it using HMAC-SHA256 with your webhook secret:

```python
import hmac, hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### Retry Policy

Failed webhook deliveries are retried up to 5 times with exponential backoff: 1 min, 5 min, 30 min, 2 hours, 24 hours.

## Error Codes

| Code | Meaning |
|------|---------|
| `card_declined` | The card was declined by the issuing bank |
| `insufficient_funds` | The card has insufficient funds |
| `expired_card` | The card has expired |
| `invalid_cvv` | The CVV code is incorrect |
| `processing_error` | A temporary error occurred; retry the request |
| `rate_limit_exceeded` | Too many requests; implement backoff |

## SDKs

Official SDKs are available for:
- Python: `pip install novapay`
- Node.js: `npm install @novapay/sdk`
- Ruby: `gem install novapay`
- Go: `go get github.com/novapay/novapay-go`
- Java: available via Maven Central
