# Task 06: Output Generation

**Task ID:** task_06_output_generation
**Dependencies:** All previous tasks
**Output:** market_analysis (for research_brief.json)

---

## Objective

Compile all research from Tasks 1-5 into the final `market_analysis` section of `research_brief.json`.

---

## Instructions

### Step 1: Aggregate Data
Collect outputs from all previous tasks:
- competitor_list.json (Task 1)
- pricing_data.json (Task 2)
- market_size_estimate.json (Task 3)
- positioning_map.json (Task 4)
- risk_assessment.json (Task 5)

### Step 2: Format for Data Contract
Transform aggregated data to match the `research_brief.schema.json` format defined in `ORCHESTRATION_data_contracts.yaml`.

### Step 3: Verify All Citations
Ensure every claim has a source:
- All competitors have source URLs
- Market size has source
- Pricing data has pricing page URLs
- All numerical claims cited

### Step 4: Run Validation Gates
Verify all quality gates pass:
- gate_all_competitors_cited
- gate_pricing_data_verifiable
- gate_market_size_has_source

### Step 5: Generate Final Output

---

## Output Format

```json
{
  "market_analysis": {
    "competitors": [
      {
        "name": "Asana",
        "positioning": "Work management platform for teams",
        "pricing": "Free tier available, Starter $10.99/user/month, Advanced $24.99/user/month",
        "source": "https://asana.com/pricing"
      }
    ],
    "pricing_insights": {
      "low": 10,
      "median": 50,
      "high": 200,
      "currency": "USD",
      "unit": "per user/month"
    },
    "market_size": "TAM: $12B (bottom-up: 100M knowledge workers × $120/year, source: ILO Global Employment Report), SAM: $1.2B (10% targeting creative agencies), SOM: $24M (2% Year 1 market share)",
    "positioning_opportunities": [
      "Niche focus on creative agencies (underserved segment)",
      "Flat-rate pricing model (pricing innovation vs per-user)"
    ],
    "risks": [
      "Market saturation: 10+ well-funded competitors",
      "High customer acquisition costs in crowded market"
    ]
  }
}
```

---

## Quality Checklist

Before submitting final output:
- [ ] All required fields present
- [ ] Conforms to research_brief.schema.json
- [ ] All citations present and URLs working
- [ ] No vague or unsupported claims
- [ ] Pricing insights calculated correctly
- [ ] Market size shows calculation methodology
- [ ] At least 3 positioning opportunities
- [ ] At least 3 risks identified

---

## Validation Gates

This task must pass all gates:
1. **gate_all_competitors_cited:** Every competitor has source URL
2. **gate_pricing_data_verifiable:** All pricing claims have official URLs
3. **gate_market_size_has_source:** Market size includes source and methodology

**If any gate fails, return to the relevant task and fix the issue.**

---

## Handoff

Once complete, this `market_analysis` section will be:
1. Validated by **FACT_VALIDATOR** agent
2. Included in `research_brief.json`
3. Passed to **LEAN_CANVAS_VALIDATOR** for business planning

**Your research directly impacts the quality of the entire planning phase. Ensure accuracy.**
