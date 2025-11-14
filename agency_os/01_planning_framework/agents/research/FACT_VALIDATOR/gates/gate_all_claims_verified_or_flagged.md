# Validation Gate: All Claims Verified or Flagged

**Gate ID:** gate_all_claims_verified_or_flagged
**Purpose:** Ensure every claim is either VERIFIED with source or FLAGGED as issue
**Enforcement:** MANDATORY - blocks progression if failed

---

## Validation Criteria

This gate passes ONLY if:

1. **Every claim has verification_status**
   - Either "VERIFIED" or "UNVERIFIED"
   - No claims without status

2. **VERIFIED claims have sources**
   - Source URL provided
   - Source is valid

3. **UNVERIFIED claims are flagged**
   - Included in flagged_hallucinations
   - Have issue description
   - Have recommendation

---

## Validation Logic

```python
def validate_all_claims_verified_or_flagged(validated_claims, flagged_hallucinations):
    issues = []

    for claim in validated_claims:
        claim_id = claim.get("claim_id", "Unknown")
        status = claim.get("verification_status")

        # Check status exists
        if not status:
            issues.append(f"{claim_id}: No verification_status")
            continue

        # If VERIFIED, must have source
        if status == "VERIFIED":
            if "source" not in claim or not claim["source"]:
                issues.append(f"{claim_id}: Marked VERIFIED but no source provided")

        # If UNVERIFIED, should be in flagged_hallucinations
        if status == "UNVERIFIED":
            flagged_ids = [f.get("claim_id") for f in flagged_hallucinations]
            if claim_id not in flagged_ids:
                issues.append(f"{claim_id}: UNVERIFIED but not flagged in hallucinations")

    passed = len(issues) == 0

    return {
        "passed": passed,
        "issues": issues,
        "claims_checked": len(validated_claims)
    }
```

---

## Example: Pass vs. Fail

### ✅ PASS
```json
{
  "validated_claims": [
    {
      "claim_id": "CLAIM-001",
      "verification_status": "VERIFIED",
      "source": "https://www.gartner.com/..."
    },
    {
      "claim_id": "CLAIM-002",
      "verification_status": "UNVERIFIED"
    }
  ],
  "flagged_hallucinations": [
    {
      "claim_id": "CLAIM-002",
      "issue": "No source provided"
    }
  ]
}
```

### ❌ FAIL
```json
{
  "validated_claims": [
    {
      "claim_id": "CLAIM-001",
      "verification_status": "VERIFIED"
      // ❌ No source!
    }
  ]
}
```

---

## Success Message

```
✅ Gate Passed: All Claims Verified or Flagged
- Checked: 45 claims
- Verified: 38
- Unverified & Flagged: 7
- All claims accounted for
```

---

## Failure Message

```
❌ Gate Failed: All Claims Verified or Flagged
Issues found:
- CLAIM-001: Marked VERIFIED but no source provided
- CLAIM-005: UNVERIFIED but not flagged in hallucinations

Action Required: Fix verification status and ensure all unverified claims are flagged.
```
