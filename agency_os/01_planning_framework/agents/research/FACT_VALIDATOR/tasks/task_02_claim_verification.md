# Task 02: Claim Verification

**Task ID:** task_02_claim_verification
**Dependencies:** task_01
**Input:** claims_inventory.json
**Output:** verified_claims.json

---

## Objective

Verify each claim has appropriate source. Mark as VERIFIED or UNVERIFIED.

---

## Instructions

### Step 1: Check Source Availability
For each claim:
- Does it have a source?
- Is the source a valid URL?
- Is the source credible?

### Step 2: Verify Source Type
Apply rules from `RESEARCH_red_flag_taxonomy.yaml`:
- **Acceptable sources:** Official docs, analyst reports, verified data
- **Unacceptable sources:** Blog posts, forums, social media, AI-generated content

### Step 3: Mark Verification Status
- **VERIFIED:** Has credible source
- **UNVERIFIED:** Missing source or non-credible source

---

## Output Format

```json
{
  "verified_claims": [
    {
      "claim_id": "CLAIM-001",
      "claim_text": "TAM is $6.8B",
      "source": "https://www.gartner.com/...",
      "verification_status": "VERIFIED",
      "verified_at": "2025-11-14T10:30:00Z",
      "source_type": "analyst_report"
    },
    {
      "claim_id": "CLAIM-002",
      "claim_text": "Market is growing rapidly",
      "source": null,
      "verification_status": "UNVERIFIED",
      "issue": "No source provided, claim is vague (no timeframe, no rate)"
    }
  ],
  "summary": {
    "total_claims": 45,
    "verified": 38,
    "unverified": 7
  }
}
```

---

## Next Task

Proceed to **Task 03: Red Flag Detection**
