# Validation Gate: All Competitors Cited

**Gate ID:** gate_all_competitors_cited
**Purpose:** Ensure every competitor has a valid source URL
**Enforcement:** MANDATORY - blocks progression if failed

---

## Validation Criteria

This gate passes ONLY if:

1. **Every competitor has a source field**
   - No competitors with empty or null source
   - No competitors with "N/A" or "TBD" as source

2. **Every source is a valid URL**
   - Starts with `http://` or `https://`
   - Is a complete URL, not partial (e.g., not "asana.com" but "https://asana.com")
   - Links to official company website or product page

3. **All URLs are functional**
   - URLs should be tested (return 200 OK)
   - No 404 errors
   - No dead links

4. **Sources are official**
   - Links to company's official domain
   - NOT blog posts, review sites, or third-party sources
   - Acceptable: company.com, company.com/product, company.com/pricing

---

## Validation Logic

```python
def validate_all_competitors_cited(competitors):
    """
    Validates that all competitors have valid source URLs.

    Returns:
        {
            "passed": bool,
            "issues": list of str,
            "competitors_checked": int,
            "competitors_with_sources": int
        }
    """
    issues = []

    for i, competitor in enumerate(competitors):
        # Check 1: Source field exists
        if "source" not in competitor or not competitor["source"]:
            issues.append(f"Competitor #{i+1} ({competitor.get('name', 'Unknown')}) has no source")
            continue

        source = competitor["source"]

        # Check 2: Source is a valid URL format
        if not source.startswith(("http://", "https://")):
            issues.append(f"Competitor #{i+1} ({competitor.get('name', 'Unknown')}) source is not a valid URL: {source}")

        # Check 3: Source is not a placeholder
        if source.lower() in ["n/a", "tbd", "todo", "unknown"]:
            issues.append(f"Competitor #{i+1} ({competitor.get('name', 'Unknown')}) has placeholder source: {source}")

        # Check 4: URL should be reasonably complete (has domain)
        if source.count("/") < 2:  # At minimum should be https://domain.com
            issues.append(f"Competitor #{i+1} ({competitor.get('name', 'Unknown')}) has incomplete URL: {source}")

    passed = len(issues) == 0

    return {
        "passed": passed,
        "issues": issues,
        "competitors_checked": len(competitors),
        "competitors_with_sources": len([c for c in competitors if c.get("source")])
    }
```

---

## Example: Pass vs. Fail

### ✅ PASS
```json
{
  "competitors": [
    {
      "name": "Asana",
      "source": "https://asana.com"
    },
    {
      "name": "Monday.com",
      "source": "https://monday.com/product"
    }
  ]
}
```

### ❌ FAIL - No source
```json
{
  "competitors": [
    {
      "name": "Asana"
    }
  ]
}
```

### ❌ FAIL - Invalid URL
```json
{
  "competitors": [
    {
      "name": "Asana",
      "source": "asana.com"
    }
  ]
}
```

### ❌ FAIL - Placeholder
```json
{
  "competitors": [
    {
      "name": "Asana",
      "source": "TBD"
    }
  ]
}
```

---

## Error Handling

If this gate fails:
1. Return error message listing all competitors without valid sources
2. Block progression to next task or FACT_VALIDATOR
3. Require MARKET_RESEARCHER to fix and resubmit
4. Log failure for quality metrics

---

## Success Message

```
✅ Gate Passed: All Competitors Cited
- Checked: 5 competitors
- All have valid source URLs
- Ready for FACT_VALIDATOR review
```

---

## Failure Message

```
❌ Gate Failed: All Competitors Cited
Issues found:
- Competitor #1 (Asana) has no source
- Competitor #3 (Notion) has invalid URL: notion.so (missing protocol)

Action Required: Add valid source URLs for all competitors before proceeding.
```
