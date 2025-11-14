# Task 04: Constraint Identification

**Task ID:** task_04_constraint_identification
**Dependencies:** task_01, task_02, task_03
**Output:** constraint_identification.json

---

## Objective

Identify technical constraints and FAE violations. Reference existing FAE rules from `FAE_constraints.yaml`.

---

## Instructions

### Step 1: Review Features Against FAE Rules
- Load `agency_os/00_system/knowledge/FAE_constraints.yaml`
- Check each feature against FAE constraints
- Identify violations

### Step 2: Identify Stack Constraints
- Serverless limitations (stateless, timeout, cold start)
- Database constraints (connection limits, query performance)
- API rate limits
- File size limits
- Browser/platform compatibility

### Step 3: Document Each Constraint
For each constraint:
- **Feature affected**
- **FAE violation ID** (if applicable, e.g., FAE-TECH-003)
- **Description** of constraint
- **Recommendation** for mitigation

---

## Output Format

```json
{
  "technical_constraints": [
    "Real-time WebSocket connections incompatible with serverless (FAE-TECH-003)",
    "File uploads limited to 10MB on Vercel serverless functions",
    "PostgreSQL connection limit: 100 concurrent (Railway Starter plan)"
  ],
  "flagged_features": [
    {
      "feature": "Real-time collaborative editing",
      "fae_violation": "FAE-TECH-003",
      "description": "WebSockets require persistent connections, incompatible with stateless serverless model",
      "recommendation": "Use managed WebSocket service (Pusher, Ably) or switch to long-polling"
    },
    {
      "feature": "Large file uploads (>10MB)",
      "fae_violation": null,
      "description": "Vercel serverless functions have 10MB request limit",
      "recommendation": "Use direct-to-S3 uploads with presigned URLs"
    }
  ]
}
```

---

## FAE Integration (CRITICAL)

**Reference existing FAE rules, don't create new ones:**
- Check `FAE_constraints.yaml` for rule IDs
- Cite rule ID in `fae_violation` field
- If no rule exists, set `fae_violation: null` and flag for FAE team review

---

## Next Task

Proceed to **Task 05: Feasibility Validation**
