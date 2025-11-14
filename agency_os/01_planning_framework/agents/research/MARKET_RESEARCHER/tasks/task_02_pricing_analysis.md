# Task 02: Pricing Analysis

**Task ID:** task_02_pricing_analysis
**Dependencies:** task_01_competitor_identification
**Output:** pricing_data.json

---

## Objective

Gather detailed, verifiable pricing data for all competitors identified in Task 01. Every pricing claim must link to the official pricing page.

---

## Instructions

### Step 1: Visit Official Pricing Pages
For each competitor from task_01:
- Navigate to their official pricing page
- Document the URL
- Extract current pricing information

### Step 2: Document Pricing Structure
For each competitor, capture:
- **Pricing tiers:** All available plans (Free, Basic, Pro, Enterprise, etc.)
- **Price per tier:** Exact price with currency
- **Billing period:** Monthly, annual, per-user, usage-based
- **Key features per tier:** What's included
- **Free trial:** Duration if available

### Step 3: Calculate Pricing Insights
Analyze all competitor pricing to determine:
- **Low:** Lowest entry price point
- **Median:** Middle-range pricing
- **High:** Highest tier (exclude "Enterprise custom" if no price listed)
- **Common billing unit:** Per user/month, flat rate, usage-based

### Step 4: Verify All Sources
- Test every pricing page URL
- Ensure pricing is current (check page for "updated" date if available)
- Flag any custom/contact-sales pricing

---

## Output Format

```json
{
  "competitor_pricing": [
    {
      "name": "Competitor Name",
      "pricing_url": "https://competitor.com/pricing",
      "verified_date": "2025-11-14",
      "tiers": [
        {
          "tier_name": "Basic",
          "price": 10.99,
          "currency": "USD",
          "billing_period": "per user/month",
          "annual_discount": "20% off if billed annually",
          "key_features": ["Feature 1", "Feature 2"]
        }
      ],
      "free_trial": "14 days",
      "notes": "Enterprise pricing is custom (contact sales)"
    }
  ],
  "pricing_insights": {
    "low": 10,
    "median": 50,
    "high": 200,
    "currency": "USD",
    "unit": "per user/month",
    "common_models": ["freemium", "per-user subscription"]
  }
}
```

---

## Quality Checklist

- [ ] Every competitor has a pricing_url
- [ ] All URLs tested and working
- [ ] Prices are specific numbers (not "around $X" or "starting at")
- [ ] Currency is specified
- [ ] Billing period is clear
- [ ] Verified date is included

---

## Common Pitfalls

❌ Estimating pricing without visiting the page
❌ Listing "Enterprise: Contact Sales" without researching typical enterprise pricing
❌ Using outdated pricing from blog posts or reviews
❌ Not specifying billing period (monthly vs annual makes a big difference)

---

## Next Task

Proceed to **Task 03: Market Size Estimation**
