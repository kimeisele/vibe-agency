# Validation Gate: No Critical Hallucinations

**Gate ID:** gate_no_critical_hallucinations
**Purpose:** Block progression if critical hallucinations detected
**Enforcement:** MANDATORY BLOCKING - stops entire workflow if failed

---

## Validation Criteria

This gate passes ONLY if:

1. **No critical severity issues**
   - issues_critical == 0
   - No flagged hallucinations with severity: "critical"

2. **Quality score >= 50**
   - Calculated score meets threshold
   - Formula: 100 - (critical * 10) - (high * 5) - (medium * 2)

3. **Critical claims have sources**
   - Market size has source
   - All competitors have sources
   - All API/library recommendations have docs

---

## Validation Logic

```python
def validate_no_critical_hallucinations(fact_validation):
    issues = []
    blocking_reasons = []

    # Check issues_critical
    issues_critical = fact_validation.get("issues_critical", 0)
    if issues_critical > 0:
        blocking_reasons.append(f"{issues_critical} critical issues found")

    # Check quality_score
    quality_score_str = fact_validation.get("quality_score", "0/100")
    quality_score = int(quality_score_str.split("/")[0])

    if quality_score < 50:
        blocking_reasons.append(f"Quality score {quality_score} < 50 threshold")

    # Check flagged hallucinations for critical severity
    flagged = fact_validation.get("flagged_hallucinations", [])
    critical_flags = [f for f in flagged if f.get("severity") == "critical"]

    if critical_flags:
        for flag in critical_flags:
            issues.append(f"Critical hallucination: {flag.get('claim', 'Unknown')}")

    # BLOCKING decision
    blocking = len(blocking_reasons) > 0

    passed = not blocking

    return {
        "passed": passed,
        "blocking": blocking,
        "blocking_reasons": blocking_reasons,
        "issues": issues,
        "quality_score": quality_score,
        "issues_critical": issues_critical
    }
```

---

## Example: Pass vs. Fail

### ✅ PASS
```json
{
  "fact_validation": {
    "quality_score": "85/100",
    "issues_critical": 0,
    "flagged_hallucinations": []
  }
}
```

### ❌ FAIL - Critical issues
```json
{
  "fact_validation": {
    "quality_score": "40/100",
    "issues_critical": 2,
    "flagged_hallucinations": [
      {
        "claim": "Stripe has 99.99% uptime",
        "severity": "critical"
      }
    ]
  }
}
```

---

## Blocking Behavior

When this gate fails:
1. **STOP** workflow progression
2. **RETURN** to MARKET_RESEARCHER or TECH_RESEARCHER
3. **REQUIRE** fixes before proceeding
4. **BLOCK** handoff to LEAN_CANVAS_VALIDATOR

---

## Success Message

```
✅ Gate Passed: No Critical Hallucinations
- Quality score: 85/100 (above 50 threshold)
- Critical issues: 0
- Research quality acceptable
- Ready to proceed to USER_RESEARCHER or finalize research_brief
```

---

## Failure Message (BLOCKING)

```
🛑 GATE BLOCKED: Critical Hallucinations Detected

Blocking reasons:
- 2 critical issues found
- Quality score 40 < 50 threshold

Critical issues:
- Stripe has 99.99% uptime (no source)
- Market size has no source

ACTION REQUIRED:
1. Return to MARKET_RESEARCHER to fix market size citation
2. Return to TECH_RESEARCHER to fix API claims
3. Re-run FACT_VALIDATOR after fixes

WORKFLOW BLOCKED - Cannot proceed to LEAN_CANVAS_VALIDATOR
```
