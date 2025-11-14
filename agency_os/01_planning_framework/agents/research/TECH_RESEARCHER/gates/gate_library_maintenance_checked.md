# Validation Gate: Library Maintenance Checked

**Gate ID:** gate_library_maintenance_checked
**Purpose:** Ensure all recommended libraries have verified maintenance status
**Enforcement:** MANDATORY - blocks progression if failed

---

## Validation Criteria

This gate passes ONLY if:

1. **Every library has maintenance_status field**
   - Not empty or null
   - Contains last commit date or activity indicator

2. **GitHub URLs provided**
   - All libraries link to GitHub (or npm/PyPI for packages)
   - URLs are valid

3. **Maintenance status is recent**
   - Last commit date within last 90 days preferred
   - If > 90 days, must be flagged with warning

4. **License documented**
   - Every library has license field
   - License is specified (MIT, Apache, GPL, etc.)

---

## Validation Logic

```python
from datetime import datetime, timedelta

def validate_library_maintenance_checked(recommended_libraries):
    issues = []
    warnings = []

    for i, lib in enumerate(recommended_libraries):
        lib_name = lib.get("name", f"Library #{i+1}")

        # Check maintenance_status exists
        if "maintenance_status" not in lib or not lib["maintenance_status"]:
            issues.append(f"{lib_name}: No maintenance_status provided")
            continue

        # Check source URL exists
        if "source" not in lib or not lib["source"]:
            issues.append(f"{lib_name}: No source URL provided")

        # Check license documented
        if "license" not in lib or not lib["license"]:
            issues.append(f"{lib_name}: No license documented")

        # Parse maintenance status for date (if available)
        maintenance = lib["maintenance_status"].lower()

        # Warning for inactive libraries
        if any(keyword in maintenance for keyword in ["inactive", "abandoned", "deprecated"]):
            issues.append(f"{lib_name}: Library appears inactive or abandoned")

        # Extract last commit date if present (format: "Active - last commit 2025-11-10")
        if "last commit" in maintenance:
            try:
                date_str = maintenance.split("last commit")[1].strip().split(",")[0].strip()
                last_commit = datetime.strptime(date_str, "%Y-%m-%d")
                days_ago = (datetime.now() - last_commit).days

                if days_ago > 90:
                    warnings.append(f"{lib_name}: Last commit {days_ago} days ago (> 90 days)")
            except:
                pass  # Date parsing failed, skip

    passed = len(issues) == 0

    return {
        "passed": passed,
        "issues": issues,
        "warnings": warnings,
        "libraries_checked": len(recommended_libraries)
    }
```

---

## Example: Pass vs. Fail

### ✅ PASS
```json
{
  "recommended_libraries": [
    {
      "name": "React",
      "license": "MIT",
      "maintenance_status": "Active - last commit 2025-11-10",
      "source": "https://github.com/facebook/react"
    }
  ]
}
```

### ❌ FAIL - No maintenance status
```json
{
  "recommended_libraries": [
    {
      "name": "React",
      "license": "MIT",
      "source": "https://github.com/facebook/react"
    }
  ]
}
```

### ❌ FAIL - Inactive library
```json
{
  "recommended_libraries": [
    {
      "name": "OldLibrary",
      "license": "MIT",
      "maintenance_status": "Inactive - last commit 2022-03-15",
      "source": "https://github.com/old/library"
    }
  ]
}
```

---

## Success Message

```
✅ Gate Passed: Library Maintenance Checked
- Checked: 8 libraries
- All have maintenance status verified
- All have licenses documented
- 1 warning: Library X last commit 95 days ago
- Ready for next task
```

---

## Failure Message

```
❌ Gate Failed: Library Maintenance Checked
Issues found:
- React: No maintenance_status provided
- Vue: Library appears inactive or abandoned
- Express: No license documented

Action Required: Verify maintenance status and document licenses for all libraries.
```
