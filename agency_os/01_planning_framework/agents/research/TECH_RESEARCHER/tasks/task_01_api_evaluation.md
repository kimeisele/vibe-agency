# Task 01: API Evaluation

**Task ID:** task_01_api_evaluation
**Dependencies:** None (first task)
**Output:** api_evaluation.json

---

## Objective

Research and evaluate external APIs required for core features. Document pricing, rate limits, reliability, and documentation quality.

---

## Instructions

### Step 1: Identify Required APIs
Based on user vision and feature requirements, identify:
- What external services are needed? (payment, email, SMS, AI, maps, etc.)
- Which features depend on external APIs?
- Are there alternative API providers for each need?

### Step 2: Research Each API
For each identified API, gather:
- **Official documentation URL**
- **Pricing** (all tiers, with exact numbers)
- **Rate limits** (requests per second/minute/day)
- **Reliability** (SLA if available, uptime guarantees)
- **Authentication method** (API key, OAuth, etc.)
- **Key limitations** (file size limits, response time, regional availability)

### Step 3: Compare Alternatives
For each API category, compare at least 2-3 alternatives:
- Pricing differences
- Rate limit differences
- Documentation quality
- Community support

### Step 4: Verify All Sources
- Test all documentation URLs
- Ensure pricing is from official pages
- Verify rate limits from official docs (not blog posts)

---

## Output Format

```json
{
  "apis_by_category": {
    "payment_processing": [
      {
        "name": "Stripe",
        "purpose": "Credit card processing",
        "pricing": "2.9% + $0.30 per transaction (standard), 2.7% + $0.05 (volume discount)",
        "rate_limits": "100 requests/second (standard account)",
        "reliability": "99.99% uptime SLA",
        "authentication": "API key (secret + publishable)",
        "key_limitations": ["3D Secure required for EU cards", "Webhook verification required"],
        "documentation_quality": "excellent",
        "source": "https://stripe.com/docs/api"
      },
      {
        "name": "PayPal",
        "purpose": "Alternative payment method",
        "pricing": "2.9% + $0.30 per transaction",
        "rate_limits": "60 requests/minute",
        "reliability": "99.9% uptime (no SLA for standard accounts)",
        "authentication": "OAuth 2.0",
        "key_limitations": ["Requires PayPal account", "Slower fund transfer"],
        "documentation_quality": "good",
        "source": "https://developer.paypal.com/docs/api/"
      }
    ]
  },
  "recommended_apis": [
    {
      "name": "Stripe",
      "purpose": "Payment processing",
      "pricing": "2.9% + $0.30 per transaction",
      "rate_limits": "100 requests/second",
      "reliability": "99.99% uptime SLA",
      "source": "https://stripe.com/docs/api",
      "selection_rationale": "Superior documentation, better SLA, more features (invoicing, subscriptions)"
    }
  ]
}
```

---

## Quality Checklist

- [ ] All required API categories identified
- [ ] At least 2-3 alternatives per category researched
- [ ] Every API has official documentation URL
- [ ] Pricing is specific (exact numbers, not "starting at")
- [ ] Rate limits are specific (not "fast" or "generous")
- [ ] SLA/reliability documented where available
- [ ] Selection rationale provided for recommendations

---

## Common API Categories

- **Payment:** Stripe, PayPal, Square
- **Email:** SendGrid, Mailgun, AWS SES
- **SMS:** Twilio, Vonage, AWS SNS
- **AI/ML:** OpenAI, Anthropic, Google AI
- **Maps:** Google Maps, Mapbox, OpenStreetMap
- **Storage:** AWS S3, Cloudflare R2, Backblaze B2
- **Authentication:** Auth0, Firebase Auth, Supabase Auth
- **Search:** Algolia, Elasticsearch, Typesense

---

## Next Task

Proceed to **Task 02: Library Comparison**
