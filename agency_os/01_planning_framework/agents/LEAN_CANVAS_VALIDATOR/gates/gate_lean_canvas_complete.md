# Validation Gate: Lean Canvas Complete

## Gate ID
`gate_lean_canvas_complete`

## Purpose
Ensure all 9 Lean Canvas fields have thoughtful responses before handoff

## Validation Criteria

### MUST PASS (Blocking)
- [ ] All 9 canvas fields are filled (not empty)
- [ ] Problem field includes alternatives (current solutions)
- [ ] Customer segment is specific (not "everyone")
- [ ] UVP is clear and differentiated
- [ ] Solution/MVP is minimal (not a feature laundry list)
- [ ] At least 2 riskiest assumptions identified
- [ ] lean_canvas_summary.json is valid JSON

### SHOULD PASS (Warnings)
- [ ] Revenue model is specific (has pricing)
- [ ] Key metric is actionable (not vanity metric)
- [ ] Channels are realistic for stage (not "we'll go viral")

### COMMON FAILURES

**❌ Vague Customer Segment**
```
Bad: "Small businesses"
Good: "Solo accountants serving 5-20 local retail clients, using Excel for bookkeeping"
```

**❌ Feature List as Solution**
```
Bad: "A platform with analytics, dashboards, reporting, AI recommendations, mobile app..."
Good: "A single CSV upload tool that auto-categorizes transactions and generates a P&L statement"
```

**❌ Vanity Metric**
```
Bad: "Number of page views"
Good: "% of uploaded files that result in a completed report"
```

## Handling Failures

If validation fails:
1. Return to task_01_canvas_interview for the failing field
2. Ask clarifying questions
3. Re-run validation

## Output on Success
Proceed to VIBE_ALIGNER handoff
