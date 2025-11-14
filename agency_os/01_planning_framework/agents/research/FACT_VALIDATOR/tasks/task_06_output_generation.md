# Task 06: Output Generation

**Task ID:** task_06_output_generation
**Dependencies:** All previous tasks
**Output:** fact_validation (for research_brief.json)

---

## Objective

Generate final fact_validation section with quality score and blocking decision.

---

## Instructions

### Step 1: Calculate Quality Score
Formula from `RESEARCH_red_flag_taxonomy.yaml`:
```
quality_score = 100 - (critical * 10) - (high * 5) - (medium * 2)
```

### Step 2: Determine Blocking Status
**BLOCK if:**
- quality_score < 50
- issues_critical > 0

### Step 3: Compile Final Output
Include:
- validated_claims
- flagged_hallucinations
- citation_index
- quality_score
- issues_found (counts)
- issues_critical (count)

---

## Output Format

```json
{
  "fact_validation": {
    "validated_claims": [...],
    "flagged_hallucinations": [...],
    "citation_index": [...],
    "quality_score": "85/100",
    "issues_found": 5,
    "issues_critical": 0,
    "handoff_status": "READY"
  }
}
```

---

## Quality Thresholds

- **Excellent:** >= 90
- **Good:** 70-89
- **Acceptable:** 50-69
- **Poor:** < 50 (BLOCKING)

---

## Blocking Decision

If blocking:
- Set handoff_status: "NOT_READY"
- Include correction_recommendations
- Require fixes before proceeding

If passing:
- Set handoff_status: "READY"
- Proceed to USER_RESEARCHER or finalize research_brief

---

## Handoff

This fact_validation section will be:
1. Included in research_brief.json
2. Used to decide if research can proceed to LEAN_CANVAS_VALIDATOR
3. Block if quality < 50 or critical issues > 0
