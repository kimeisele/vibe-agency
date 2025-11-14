# Task 01: Knowledge Base Audit

**Task ID:** task_01_knowledge_base_audit
**Dependencies:** None (first task)
**Input:** market_analysis.json, tech_analysis.json
**Output:** claims_inventory.json

---

## Objective

Audit all claims from market_analysis and tech_analysis. Extract every factual claim that requires verification.

---

## Instructions

### Step 1: Extract All Claims
From market_analysis:
- Market size numbers (TAM/SAM/SOM)
- Competitor names and positioning
- Pricing claims
- Growth rates, market trends
- Risk assessments

From tech_analysis:
- API pricing and rate limits
- Library maintenance status
- Technical constraints
- FAE violations
- Feasibility scores

### Step 2: Categorize Claims
- **Numerical claims:** Numbers, percentages, currency amounts
- **Competitive claims:** Competitor data, pricing, features
- **Technical claims:** API limits, library status, constraints
- **Market trends:** Growth rates, market dynamics
- **Qualitative assessments:** Feasibility scores, risk levels

### Step 3: Identify Source Requirements
For each claim, determine:
- Does it REQUIRE a source? (all numerical claims must)
- What type of source is acceptable?
- Is the claim verifiable?

---

## Output Format

```json
{
  "claims_inventory": {
    "total_claims": 45,
    "by_category": {
      "numerical": 15,
      "competitive": 12,
      "technical": 10,
      "market_trends": 5,
      "qualitative": 3
    },
    "claims": [
      {
        "claim_id": "CLAIM-001",
        "claim_text": "TAM is $6.8B",
        "category": "numerical",
        "source_required": true,
        "source_provided": "https://www.gartner.com/...",
        "origin": "market_analysis.market_size.TAM"
      },
      {
        "claim_id": "CLAIM-002",
        "claim_text": "Asana pricing: $10.99/user/month",
        "category": "competitive",
        "source_required": true,
        "source_provided": "https://asana.com/pricing",
        "origin": "market_analysis.competitors[0].pricing"
      }
    ]
  }
}
```

---

## Next Task

Proceed to **Task 02: Claim Verification**
