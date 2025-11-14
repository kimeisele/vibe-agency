# Task 04: Citation Enforcement

**Task ID:** task_04_citation_enforcement
**Dependencies:** task_01, task_02, task_03
**Input:** verified_claims.json
**Output:** citation_index.json

---

## Objective

Build citation index and enforce citation requirements. Block if critical claims lack sources.

---

## Instructions

### Step 1: Build Citation Index
List all unique sources used:
- URL
- What claims cite this source
- Source type (official docs, analyst report, etc.)

### Step 2: Check Critical Claims
From `RESEARCH_red_flag_taxonomy.yaml`, critical claims requiring sources:
- Market size estimates
- Competitor pricing
- Technical feasibility assessments
- API rate limits and pricing
- Library maintenance status

### Step 3: Enforce Blocking Rules
**BLOCK if:**
- Any critical claim lacks source
- Any numerical claim lacks source
- Any competitor lacks source URL

---

## Output Format

```json
{
  "citation_index": [
    {
      "url": "https://www.gartner.com/...",
      "source_type": "analyst_report",
      "cited_in": ["CLAIM-001", "CLAIM-005"],
      "verified": true
    },
    {
      "url": "https://asana.com/pricing",
      "source_type": "official_pricing_page",
      "cited_in": ["CLAIM-002"],
      "verified": true
    }
  ],
  "enforcement_results": {
    "critical_claims_total": 10,
    "critical_claims_sourced": 8,
    "critical_claims_unsourced": 2,
    "blocking": true,
    "blocking_reason": "2 critical claims lack sources"
  }
}
```

---

## Blocking Conditions

**BLOCK if any of:**
- critical_claims_unsourced > 0
- Any market size without source
- Any competitor without source
- Any API/library recommendation without docs

---

## Next Task

Proceed to **Task 05: Correction Recommendations**
