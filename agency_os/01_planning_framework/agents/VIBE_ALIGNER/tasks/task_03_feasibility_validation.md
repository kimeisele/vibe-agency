# Task: Feasibility Validation (FAE)

## Objective
Validate all extracted features against the Feasibility Analysis Engine (FAE) to reject impossible features BEFORE the user gets attached to them.

---

## Goal
Ensure all features are technically feasible for the user's chosen scope (prototype/MVP/v1.0) and timeline.

---

## Input Artifacts
- `extracted_features.json` (from Task 02)
- `FAE_constraints.yaml` (from knowledge base)
- Session state: `user_scope_choice`

---

## Validation Process

For EACH feature in `extracted_features.json`, check against `FAE_constraints.yaml`:

```python
# Pseudo-code for FAE validation
for feature in extracted_features:
    # Check incompatibilities
    for constraint in FAE.incompatibilities:
        if feature.name matches constraint.feature:
            if user_scope == "v1.0" and constraint.incompatible_with == "scope_v1.0":
                # REJECT IMMEDIATELY
                explain_rejection(feature, constraint)
                suggest_alternatives(constraint.alternatives_for_v1)

    # Check NFR conflicts
    inferred_nfrs = extract_nfrs(feature.description)
    for nfr_conflict in FAE.nfr_conflicts:
        if nfr_conflict.nfr_a in inferred_nfrs and nfr_conflict.nfr_b in user_constraints:
            # FLAG CONFLICT
            explain_conflict(nfr_conflict)
            suggest_resolution(nfr_conflict.resolution_options)
```

---

## Rejection Dialog Template

When FAE flags a feature as incompatible:

```
⚠️ FEASIBILITY ISSUE: {feature_name}

I've analyzed "{feature_name}" and identified a v1.0 scope conflict.

**Why it's not v1.0-ready:**
{constraint.reason}

**What it requires:**
- {required_nfr_1}
- {required_nfr_2}
- {required_nfr_3}

**Typical implementation time:** {constraint.typical_time}

**For v1.0, I recommend:**
{alternative_1} (simpler, faster)
{alternative_2} (3rd party service)

We can plan {feature_name} for v2.0 after validating the core product.

Shall we proceed with the alternative for v1.0, or would you like to extend the timeline to include this feature?
```

---

## Example Rejection

**Real-time video streaming:**

```
⚠️ FEASIBILITY ISSUE: Real-time video streaming

I've analyzed "real-time video streaming" and identified a v1.0 scope conflict.

**Why it's not v1.0-ready:**
Requires WebRTC implementation, STUN/TURN servers, signaling servers, and a media server (SFU/MCU) for scale. This is non-trivial infrastructure that typically takes 8-12 weeks to implement properly.

**What it requires:**
- Low latency (<1s)
- High bandwidth support
- High availability infrastructure
- Dedicated servers (incompatible with serverless)

**For v1.0, I recommend:**
- Pre-recorded video upload (2 weeks)
- Embed 3rd party (Zoom, Jitsi) (1 week)
- Use managed service (Mux, Wistia) (1 week)

We can plan real-time streaming for v2.0 after validating the core product.

Shall we proceed with pre-recorded video for v1.0?
```

---

## Output

Updated feature list with FAE validation results:

```json
{
  "validated_features": [
    {
      "id": "feature_1",
      "name": "...",
      "fae_validation": {
        "passed": true,
        "constraints_checked": ["FAE-001", "FAE-015"],
        "issues": []
      }
    },
    {
      "id": "feature_2",
      "name": "...",
      "fae_validation": {
        "passed": false,
        "constraints_checked": ["FAE-005"],
        "issues": [
          {
            "constraint_id": "FAE-005",
            "severity": "blocking",
            "reason": "Real-time streaming requires dedicated infrastructure",
            "alternatives": ["Pre-recorded upload", "3rd party embed"]
          }
        ]
      }
    }
  ]
}
```

---

## Success Criteria

- All features checked against FAE constraints
- Impossible features flagged and alternatives suggested
- User acknowledges feasibility concerns
- All "must_have" features have `fae_validation.passed = true`

---

## Validation Gates

- `gate_fae_all_passed.md` - Ensures all must-have features passed FAE validation
