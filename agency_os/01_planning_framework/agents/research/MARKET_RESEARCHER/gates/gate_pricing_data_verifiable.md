# Validation Gate: Pricing Data Verifiable

**Gate ID:** gate_pricing_data_verifiable
**Purpose:** Ensure all pricing claims link to official pricing pages
**Enforcement:** MANDATORY - blocks progression if failed

---

## Validation Criteria

This gate passes ONLY if:

1. **Every competitor has a pricing_url**
   - Field exists and is not empty
   - URL is complete and valid

2. **Pricing URLs are specific**
   - Links directly to pricing page (e.g., `/pricing`, `/plans`)
   - NOT just homepage (unless pricing is on homepage)

3. **Pricing data is specific**
   - Actual numbers, not vague ("starting at $X")
   - Currency specified
   - Billing period clear (monthly, annual, per-user)

4. **Verified date exists**
   - Every pricing entry has a verified_date
   - Date is recent (within last 30 days preferred)

---

## Validation Logic

```python
def validate_pricing_data_verifiable(competitor_pricing):
    """
    Validates that all pricing data is verifiable with official sources.

    Returns:
        {
            "passed": bool,
            "issues": list of str,
            "competitors_checked": int,
            "pricing_urls_valid": int
        }
    """
    issues = []

    for i, competitor in enumerate(competitor_pricing):
        comp_name = competitor.get("name", f"Competitor #{i+1}")

        # Check 1: pricing_url exists
        if "pricing_url" not in competitor or not competitor["pricing_url"]:
            issues.append(f"{comp_name}: No pricing_url provided")
            continue

        pricing_url = competitor["pricing_url"]

        # Check 2: URL is valid format
        if not pricing_url.startswith(("http://", "https://")):
            issues.append(f"{comp_name}: Invalid pricing_url format: {pricing_url}")

        # Check 3: URL appears pricing-specific (contains keywords)
        pricing_keywords = ["/pricing", "/plans", "/purchase", "/buy", "/upgrade"]
        if not any(keyword in pricing_url.lower() for keyword in pricing_keywords):
            # Warning only if URL is just homepage
            if pricing_url.count("/") <= 3:  # https://domain.com/
                issues.append(f"{comp_name}: pricing_url appears to be homepage, not pricing page: {pricing_url}")

        # Check 4: Tiers exist with actual prices
        if "tiers" not in competitor or not competitor["tiers"]:
            issues.append(f"{comp_name}: No pricing tiers provided")
        else:
            for tier_idx, tier in enumerate(competitor["tiers"]):
                # Check price is a number
                if "price" not in tier or tier["price"] is None:
                    issues.append(f"{comp_name}, Tier #{tier_idx+1}: No price specified")

                # Check currency specified
                if "currency" not in tier or not tier["currency"]:
                    issues.append(f"{comp_name}, Tier #{tier_idx+1}: No currency specified")

                # Check billing period specified
                if "billing_period" not in tier or not tier["billing_period"]:
                    issues.append(f"{comp_name}, Tier #{tier_idx+1}: No billing period specified")

        # Check 5: Verified date exists
        if "verified_date" not in competitor or not competitor["verified_date"]:
            issues.append(f"{comp_name}: No verified_date provided")

    passed = len(issues) == 0

    return {
        "passed": passed,
        "issues": issues,
        "competitors_checked": len(competitor_pricing),
        "pricing_urls_valid": len([c for c in competitor_pricing if c.get("pricing_url", "").startswith("http")])
    }
```

---

## Example: Pass vs. Fail

### ✅ PASS
```json
{
  "competitor_pricing": [
    {
      "name": "Asana",
      "pricing_url": "https://asana.com/pricing",
      "verified_date": "2025-11-14",
      "tiers": [
        {
          "tier_name": "Starter",
          "price": 10.99,
          "currency": "USD",
          "billing_period": "per user/month"
        }
      ]
    }
  ]
}
```

### ❌ FAIL - No pricing_url
```json
{
  "competitor_pricing": [
    {
      "name": "Asana",
      "tiers": []
    }
  ]
}
```

### ❌ FAIL - Vague pricing
```json
{
  "competitor_pricing": [
    {
      "name": "Asana",
      "pricing_url": "https://asana.com/pricing",
      "verified_date": "2025-11-14",
      "tiers": [
        {
          "tier_name": "Starter",
          "price": null,  // ❌ No price
          "currency": "USD",
          "billing_period": "per user/month"
        }
      ]
    }
  ]
}
```

---

## Error Handling

If this gate fails:
1. List all competitors with missing or invalid pricing URLs
2. List all tiers with incomplete pricing data
3. Block progression to next task
4. Require MARKET_RESEARCHER to fix and resubmit

---

## Success Message

```
✅ Gate Passed: Pricing Data Verifiable
- Checked: 5 competitors
- All have valid pricing URLs
- All pricing data complete with currency and billing period
- Ready for next task
```

---

## Failure Message

```
❌ Gate Failed: Pricing Data Verifiable
Issues found:
- Asana: No verified_date provided
- Monday.com, Tier #2: No currency specified
- Notion: pricing_url appears to be homepage, not pricing page: https://notion.so

Action Required: Fix pricing data issues before proceeding.
```
