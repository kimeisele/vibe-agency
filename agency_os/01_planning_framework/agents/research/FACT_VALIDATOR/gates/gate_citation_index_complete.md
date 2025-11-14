# Validation Gate: Citation Index Complete

**Gate ID:** gate_citation_index_complete
**Purpose:** Ensure all sources are indexed and tracked
**Enforcement:** MANDATORY - blocks progression if failed

---

## Validation Criteria

This gate passes ONLY if:

1. **Citation index exists**
   - Not empty
   - Contains all sources used

2. **All sources have metadata**
   - URL
   - Source type
   - What claims cite it

3. **No orphan sources**
   - Every source in index is cited by at least one claim
   - Every cited source is in the index

---

## Validation Logic

```python
def validate_citation_index_complete(citation_index, validated_claims):
    issues = []

    # Collect all sources from claims
    sources_in_claims = set()
    for claim in validated_claims:
        if claim.get("source"):
            sources_in_claims.add(claim["source"])

    # Collect all sources from index
    sources_in_index = set()
    for citation in citation_index:
        if citation.get("url"):
            sources_in_index.add(citation["url"])

            # Check metadata complete
            if "source_type" not in citation:
                issues.append(f"Citation {citation['url']}: Missing source_type")
            if "cited_in" not in citation or not citation["cited_in"]:
                issues.append(f"Citation {citation['url']}: No claims cite this source (orphan)")

    # Check for missing citations
    missing_from_index = sources_in_claims - sources_in_index
    if missing_from_index:
        for source in missing_from_index:
            issues.append(f"Source used in claims but missing from index: {source}")

    passed = len(issues) == 0

    return {
        "passed": passed,
        "issues": issues,
        "sources_in_index": len(sources_in_index),
        "sources_in_claims": len(sources_in_claims)
    }
```

---

## Example: Pass vs. Fail

### ✅ PASS
```json
{
  "citation_index": [
    {
      "url": "https://www.gartner.com/...",
      "source_type": "analyst_report",
      "cited_in": ["CLAIM-001", "CLAIM-005"]
    }
  ],
  "validated_claims": [
    {
      "claim_id": "CLAIM-001",
      "source": "https://www.gartner.com/..."
    }
  ]
}
```

### ❌ FAIL - Source missing from index
```json
{
  "citation_index": [],
  "validated_claims": [
    {
      "claim_id": "CLAIM-001",
      "source": "https://www.gartner.com/..."  // ❌ Not in index!
    }
  ]
}
```

---

## Success Message

```
✅ Gate Passed: Citation Index Complete
- Sources in index: 15
- Sources in claims: 15
- All sources accounted for
- No orphan sources
```

---

## Failure Message

```
❌ Gate Failed: Citation Index Complete
Issues found:
- Source used in claims but missing from index: https://www.gartner.com/...
- Citation https://asana.com: No claims cite this source (orphan)

Action Required: Update citation index to include all sources.
```
