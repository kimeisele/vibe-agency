# Question: Bedrock Truth Layer - manifest.json vs .session_handoff.json

**Date:** 2025-11-17
**Context:** LAD-2 (Claude Code Layer), GAD-700 (STEWARD), GAD-501 (Context Injection)
**Priority:** P0 (architecture alignment, not tooling)

---

## The Observed Problem

**Symptom:**
```
Agent starts fresh → sees .session_handoff.json (manual, stale)
                  → does NOT see project_manifest.json (orchestrator truth)
```

**Example:**
```bash
# Orchestrator creates:
workspace/manual-test-project/manifest.json  # ← SDLC state machine

# MOTD displays:
.session_handoff.json  # ← Manual repo-level context (disconnected!)
```

---

## What the Architecture Documents Say

### GAD-700 (STEWARD Governance)
Line 81:
```
Layer 2: Context must be enriched from project_manifest.json
```

### GAD-501 (Context Injection)
Layer 2: "Ambient Context (Passive - Active Artifacts)"

### core_orchestrator.py
Line 87:
```python
class ProjectManifest:
    """Project manifest (Single Source of Truth)"""
```

---

## The Disconnect

**Two parallel truth systems exist:**

| File | Purpose | Owner | Layer | Committed |
|------|---------|-------|-------|-----------|
| `workspace/*/manifest.json` | SDLC state machine | Orchestrator | Layer 2 (Ambient Context) | ✅ Yes |
| `.session_handoff.json` | Manual agent handoff | Human | ??? (Not in GAD-501!) | ✅ Yes |

**Question 1:** Is `.session_handoff.json` part of the designed architecture?

**Question 2:** Should MOTD read:
- A) `workspace/*/manifest.json` (orchestrator truth)
- B) `.session_handoff.json` (manual context)
- C) Both (but how to reconcile?)

---

## The GAD/LAD/VAD Lens

### Which pillar owns this?

**Option 1:** GAD-5XX (Runtime Engineering)
- Pro: GAD-501 defines Layer 2 "Ambient Context"
- Pro: manifest.json is runtime state
- Question: Should manifest.json BE the ambient context?

**Option 2:** GAD-7XX (STEWARD Governance)
- Pro: GAD-700 says "Context must be enriched from project_manifest.json"
- Pro: "manifest=truth" is a STEWARD principle
- Question: Is this a governance rule or architecture decision?

**Option 3:** GAD-8XX (Integration Matrix)
- Pro: This is about integrating orchestrator ↔ MOTD
- Question: Is this pillar 8's responsibility?

### Which layer are we in?

**LAD-2 (Claude Code Layer):**
- Tools available: ✅ Read files, ✅ Display MOTD
- No APIs required: ✅ Local file reads only
- Question: Can we read workspace/*/manifest.json in MOTD?

---

## The Lean Solution Request

**NOT asking for:**
- ❌ New scripts
- ❌ Automation
- ❌ Git hooks
- ❌ "Multi-agent coordination system"

**Asking for:**
- ✅ Architectural clarity: Which file IS the bedrock truth?
- ✅ GAD documentation: Should we document this as GAD-5XX amendment?
- ✅ Discipline: Once decided, agents follow the documented pattern

---

## The Specific Question

**Given:**
- ProjectManifest exists (workspace/*/manifest.json)
- .session_handoff.json exists (repo root, manual)
- GAD-700 says "Layer 2: Context must be enriched from project_manifest.json"
- GAD-501 defines Layer 2 as "Ambient Context"

**Question:**
**Should .session_handoff.json be deprecated in favor of reading workspace/*/manifest.json directly in display_motd()?**

**OR:**
**Should .session_handoff.json remain as a "manual override" and we document the relationship between the two files?**

**OR:**
**Is there a third option that aligns with the gracefully degraded, file-based architecture?**

---

## Success Criteria

✅ Single source of truth identified (no parallel systems)
✅ Documented in appropriate GAD/LAD/VAD
✅ Implementable through discipline (no new automation required)
✅ Aligns with existing architecture (GAD-501, GAD-700)
✅ Works in LAD-2 (Claude Code Layer - file reads only)

---

## What I Need to Know

1. **Architecture Decision:**
   - Is `.session_handoff.json` part of the design or an ad-hoc addition?
   - Should manifest.json be the primary truth for MOTD context?

2. **GAD Ownership:**
   - Which pillar owns this decision? (GAD-5XX, GAD-7XX, GAD-8XX?)
   - Should we create a new GAD sub-document (e.g., GAD-501-AMENDMENT)?

3. **Implementation Path:**
   - Once decided, what is the disciplined approach to follow?
   - No scripts - just documentation + agent adherence?

---

**This is NOT a tooling question. This is an ARCHITECTURE ALIGNMENT question.**

We have existing GADs that say "manifest.json is truth" but code that reads ".session_handoff.json".

Which should we align to?
