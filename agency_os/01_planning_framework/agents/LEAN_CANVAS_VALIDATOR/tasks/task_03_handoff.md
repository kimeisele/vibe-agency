# === TASK: Handoff to VIBE_ALIGNER ===

## TASK IDENTITY
- **Task ID**: 03_handoff
- **Phase**: 3 of 3
- **Purpose**: Generate structured artifact for technical planning phase

## INPUTS
- Completed Lean Canvas (9 fields)
- Riskiest assumptions (2-4 items)

## EXPECTED OUTPUTS
- `lean_canvas_summary.json` file

## EXECUTION INSTRUCTIONS

### Generate JSON Artifact (CRITICAL: This must be valid JSON matching schema below)

Create a file named `lean_canvas_summary.json` with the following **exact structure**. All fields are required:

```json
{
  "version": "1.0",
  "canvas_fields": {
    "problem": "<Field 1 response>",
    "customer_segments": "<Field 2 response>",
    "unique_value_proposition": "<Field 3 response>",
    "solution": "<Field 4 response>",
    "channels": "<Field 5 response>",
    "revenue_streams": "<Field 6 response>",
    "cost_structure": "<Field 7 response>",
    "key_metrics": "<Field 8 response>",
    "unfair_advantage": "<Field 9 response>"
  },
  "riskiest_assumptions": [
    {
      "assumption": "<specific assumption text>",
      "why_risky": "<why this is a critical risk>",
      "validation_method": "<how MVP should test this>"
    },
    {
      "assumption": "<assumption 2>",
      "why_risky": "<why risky>",
      "validation_method": "<validation approach>"
    },
    {
      "assumption": "<assumption 3>",
      "why_risky": "<why risky>",
      "validation_method": "<validation approach>"
    }
  ],
  "readiness": {
    "status": "READY",
    "confidence_level": "high",
    "missing_inputs": []
  }
}
```

### Confirmation Message

After generating the artifact, present:

```
✅ Business Validation Complete

Your Lean Canvas is validated and saved. Here's what happens next:

**Summary:**
- Problem: [1-line summary]
- Customer: [1-line summary]
- Riskiest Assumptions: [count] identified

**Next Agent:** VIBE_ALIGNER (Feature Specification)

**What VIBE_ALIGNER will do:**
- Use your business context to extract features
- Validate technical feasibility
- Create a buildable feature specification

**What you need to do:**
- Describe the features you envision for v1.0
- VIBE_ALIGNER will already know your constraints, success criteria, and business context

I've generated `lean_canvas_summary.json` which will now be passed to VIBE_ALIGNER.

Ready to continue? (Type 'yes' or describe your first feature)
```

## ARTIFACT STORAGE

Save artifact to:
`artifacts/planning/lean_canvas_summary.json`

Update project_manifest.json:
```json
{
  "links": {
    "lean_canvas_summary": "artifacts/planning/lean_canvas_summary.json"
  }
}
```

## TRANSITION TO NEXT AGENT
Hand off to VIBE_ALIGNER with lean_canvas_summary.json as input

---
# === END TASK ===
