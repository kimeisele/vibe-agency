# Task 03: Red Flag Detection

**Task ID:** task_03_red_flag_detection
**Dependencies:** task_01, task_02
**Input:** claims_inventory.json, verified_claims.json
**Output:** flagged_hallucinations.json

---

## Objective

Detect red flags using taxonomy from `RESEARCH_red_flag_taxonomy.yaml`.

---

## Instructions

### Step 1: Apply Red Flag Patterns
From `RESEARCH_red_flag_taxonomy.yaml`:

1. **Context-collapse:** Vague claims without specifics
   - Example: "Market is growing" → No timeframe, no rate

2. **Plausibly-sounding-falsehood:** Specific claim without verification
   - Example: "Stripe has 99.99% uptime" → No source

3. **Context-free-platitude:** Generic advice
   - Example: "Focus on user experience"

4. **Category-error:** Wrong tech for problem
   - Example: "Use blockchain for faster queries"

### Step 2: Assess Severity
- **Critical:** Plausibly-sounding-falsehood with no source
- **High:** Context-collapse with numbers
- **Medium:** Platitudes, vague claims
- **Low:** Minor issues

---

## Output Format

```json
{
  "flagged_hallucinations": [
    {
      "claim": "Market is growing rapidly",
      "issue": "No timeframe, no growth rate, no source",
      "red_flag_type": "context-collapse",
      "severity": "high",
      "recommendation": "Specify: '15% annual growth 2024-2028 (based on Google Trends analysis and Crunchbase funding data)'"
    },
    {
      "claim": "Stripe has 99.99% uptime",
      "issue": "No source, possibly wrong SLA tier",
      "red_flag_type": "plausibly-sounding-falsehood",
      "severity": "critical",
      "recommendation": "Verify from Stripe SLA documentation or remove claim"
    }
  ],
  "summary": {
    "total_flags": 7,
    "by_severity": {
      "critical": 2,
      "high": 3,
      "medium": 2,
      "low": 0
    }
  }
}
```

---

## Next Task

Proceed to **Task 04: Citation Enforcement**
