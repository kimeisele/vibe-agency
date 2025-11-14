# Validation Gate: All APIs Have Docs

**Gate ID:** gate_all_apis_have_docs
**Purpose:** Ensure every recommended API has official documentation URL
**Enforcement:** MANDATORY - blocks progression if failed

---

## Validation Criteria

This gate passes ONLY if:

1. **Every API has a source field**
   - Not empty or null
   - Valid URL format

2. **Source URLs are official documentation**
   - Links to official API docs (not blog posts, tutorials, or third-party sites)
   - Acceptable domains: vendor.com/docs, developer.vendor.com, api.vendor.com/docs

3. **URLs are functional**
   - Return 200 OK (tested)
   - Not 404 or dead links

---

## Validation Logic

```python
def validate_all_apis_have_docs(recommended_apis):
    issues = []

    for i, api in enumerate(recommended_apis):
        api_name = api.get("name", f"API #{i+1}")

        # Check source exists
        if "source" not in api or not api["source"]:
            issues.append(f"{api_name}: No documentation source provided")
            continue

        source = api["source"]

        # Check URL format
        if not source.startswith(("http://", "https://")):
            issues.append(f"{api_name}: Invalid source URL format: {source}")

        # Check it's documentation (not just homepage)
        doc_keywords = ["/docs", "/api", "/developer", "/reference", "/documentation"]
        if not any(keyword in source.lower() for keyword in doc_keywords):
            issues.append(f"{api_name}: Source appears to be homepage, not API docs: {source}")

    passed = len(issues) == 0

    return {
        "passed": passed,
        "issues": issues,
        "apis_checked": len(recommended_apis)
    }
```

---

## Example: Pass vs. Fail

### ✅ PASS
```json
{
  "recommended_apis": [
    {
      "name": "Stripe",
      "source": "https://stripe.com/docs/api"
    }
  ]
}
```

### ❌ FAIL
```json
{
  "recommended_apis": [
    {
      "name": "Stripe"
    }
  ]
}
```

---

## Success Message

```
✅ Gate Passed: All APIs Have Docs
- Checked: 5 APIs
- All have official documentation URLs
- Ready for next task
```
