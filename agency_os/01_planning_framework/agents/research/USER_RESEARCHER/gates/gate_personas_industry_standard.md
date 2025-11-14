# Validation Gate: Personas Industry Standard

**Gate ID:** gate_personas_industry_standard
**Purpose:** Ensure personas follow industry-standard format and avoid anti-patterns
**Enforcement:** WARNING ONLY - does not block progression

---

## Validation Criteria

This gate passes ONLY if:

1. **Required fields present**
   - name, age_range, job_title, goals, pain_points, tools_used, quote

2. **No anti-patterns**
   - Not too generic ("anyone who wants to be productive")
   - Not unrealistic combinations ("C-level who codes daily")
   - Not all positive traits
   - Not demographic-only (must have behavioral data)

3. **Specific and actionable**
   - Goals are measurable
   - Pain points are specific
   - Tools are named (not "various tools")

---

## Validation Logic

```python
def validate_personas_industry_standard(personas):
    issues = []
    warnings = []

    required_fields = ["name", "age_range", "job_title", "goals", "pain_points", "tools_used", "quote"]

    for i, persona in enumerate(personas):
        persona_name = persona.get("name", f"Persona #{i+1}")

        # Check required fields
        for field in required_fields:
            if field not in persona or not persona[field]:
                issues.append(f"{persona_name}: Missing required field '{field}'")

        # Check for anti-patterns

        # Anti-pattern: Too generic
        if persona.get("job_title", "").lower() in ["anyone", "everyone", "users"]:
            warnings.append(f"{persona_name}: Job title is too generic: {persona['job_title']}")

        # Anti-pattern: Demographic-only (no behavioral data)
        if not persona.get("tools_used") or not persona.get("goals"):
            warnings.append(f"{persona_name}: Lacks behavioral data (tools_used, goals)")

        # Anti-pattern: Vague goals
        goals = persona.get("goals", [])
        for goal in goals:
            if len(goal) < 10 or any(word in goal.lower() for word in ["better", "more", "improve"]):
                warnings.append(f"{persona_name}: Vague goal: '{goal}' (be more specific)")

        # Anti-pattern: Vague pain points
        pain_points = persona.get("pain_points", [])
        for pain in pain_points:
            if len(pain) < 10:
                warnings.append(f"{persona_name}: Vague pain point: '{pain}' (be more specific)")

        # Check quote exists and is meaningful
        quote = persona.get("quote", "")
        if len(quote) < 20:
            warnings.append(f"{persona_name}: Quote is too short or missing")

    # WARNING ONLY gate
    passed = True

    return {
        "passed": passed,
        "issues": issues,
        "warnings": warnings,
        "personas_checked": len(personas),
        "gate_type": "WARNING_ONLY"
    }
```

---

## Example: Pass vs. Fail

### ✅ PASS
```json
{
  "personas": [
    {
      "name": "Marketing Mary",
      "age_range": "28-35",
      "job_title": "Marketing Manager",
      "goals": ["Increase lead generation by 30%"],
      "pain_points": ["Too many disconnected tools waste time"],
      "tools_used": ["HubSpot", "Google Analytics"],
      "quote": "I need tools that help me work smarter."
    }
  ]
}
```

### ⚠️ WARNING - Too generic
```json
{
  "personas": [
    {
      "name": "Generic User",
      "job_title": "Anyone",
      "goals": ["Be more productive"],
      "pain_points": ["Things are hard"]
    }
  ]
}
```

---

## Success Message

```
✅ Gate Passed: Personas Industry Standard
- Checked: 3 personas
- All have required fields
- No major anti-patterns
- Ready for next task
```

---

## Warning Message

```
⚠️ Gate Warning: Personas Industry Standard (WARNING ONLY)
Warnings found:
- Marketing Mary: Vague goal: 'Improve efficiency' (be more specific)
- Sales Sam: Lacks behavioral data (no tools_used)

Recommendation: Make personas more specific and actionable.
Proceeding to next task (warning only).
```
