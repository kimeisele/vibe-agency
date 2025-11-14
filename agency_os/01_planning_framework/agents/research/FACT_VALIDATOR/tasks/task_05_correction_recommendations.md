# Task 05: Correction Recommendations

**Task ID:** task_05_correction_recommendations
**Dependencies:** All previous tasks
**Input:** flagged_hallucinations.json, citation_index.json
**Output:** correction_recommendations.json

---

## Objective

Provide specific, actionable recommendations for fixing all flagged issues.

---

## Instructions

### Step 1: Group Issues by Agent
- Issues from MARKET_RESEARCHER
- Issues from TECH_RESEARCHER

### Step 2: Provide Specific Fixes
For each issue:
- What needs to be fixed
- How to fix it
- Example of correct format

### Step 3: Prioritize by Severity
- **Critical:** Must fix before proceeding
- **High:** Should fix
- **Medium:** Nice to fix
- **Low:** Optional

---

## Output Format

```json
{
  "correction_recommendations": {
    "must_fix": [
      {
        "claim_id": "CLAIM-002",
        "issue": "Market size has no source or calculation",
        "recommendation": "Add bottom-up calculation. Example: 'TAM: $12B (100M knowledge workers × $120/year, source: ILO Employment Report)'"
      }
    ],
    "should_fix": [
      {
        "claim_id": "CLAIM-010",
        "issue": "Vague growth claim without rate",
        "recommendation": "Replace 'growing rapidly' with '15% annual growth 2024-2028 (based on Google Trends analysis and Crunchbase funding trends)'"
      }
    ],
    "nice_to_fix": []
  },
  "return_to_agent": {
    "MARKET_RESEARCHER": 3,
    "TECH_RESEARCHER": 1
  }
}
```

---

## Next Task

Proceed to **Task 06: Output Generation**
