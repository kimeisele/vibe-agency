# Task 06: Output Generation

**Task ID:** task_06_output_generation
**Dependencies:** All previous tasks
**Output:** tech_analysis (for research_brief.json)

---

## Objective

Compile all technical research into the final `tech_analysis` section of `research_brief.json`.

---

## Instructions

### Step 1: Aggregate Data
- api_evaluation.json (Task 1)
- library_comparison.json (Task 2)
- stack_recommendation.json (Task 3)
- constraint_identification.json (Task 4)
- feasibility_validation.json (Task 5)

### Step 2: Format for Data Contract
Transform to match `research_brief.schema.json` format.

### Step 3: Verify All Citations
- All APIs have documentation URLs
- All libraries have GitHub URLs
- All FAE violations cite rule IDs

### Step 4: Run Validation Gates
- gate_all_apis_have_docs
- gate_library_maintenance_checked
- gate_fae_violations_cited

---

## Output Format

```json
{
  "tech_analysis": {
    "recommended_apis": [
      {
        "name": "Stripe API",
        "purpose": "Payment processing",
        "pricing": "2.9% + $0.30 per transaction",
        "rate_limits": "100 requests/second",
        "reliability": "99.99% uptime SLA",
        "source": "https://stripe.com/docs/api"
      }
    ],
    "recommended_libraries": [
      {
        "name": "React",
        "purpose": "Frontend framework",
        "license": "MIT",
        "maintenance_status": "Active (last commit: 2025-11-10)",
        "github_stars": 220000,
        "source": "https://github.com/facebook/react"
      }
    ],
    "technical_constraints": [
      "WebSocket connections incompatible with serverless (FAE-TECH-003)",
      "File uploads limited to 10MB on Vercel"
    ],
    "feasibility_score": "high",
    "flagged_features": [
      {
        "feature": "Real-time collaborative editing",
        "fae_violation": "FAE-TECH-003",
        "recommendation": "Use managed WebSocket service (Pusher)"
      }
    ]
  }
}
```

---

## Quality Checklist

- [ ] All APIs have documentation URLs
- [ ] All libraries have GitHub URLs and maintenance status
- [ ] All FAE violations cite rule IDs
- [ ] Feasibility score with reasoning
- [ ] Technical constraints documented
- [ ] Conforms to research_brief.schema.json

---

## Handoff

This `tech_analysis` section will be:
1. Validated by **FACT_VALIDATOR**
2. Included in `research_brief.json`
3. Passed to **LEAN_CANVAS_VALIDATOR**
