# The Vibe Refinement Cycle

> **STATUS:** 🟢 ACTIVE
> **VERSION:** 1.0.0
> **RELATED:** GAD-006 (Asynchronous Intent), ARCH-044 (Git-Ops Strategy)

---

## 🎯 Purpose

The Refinement Cycle is the **meta-workflow** that transforms chaos into order. It defines how the system processes ambiguous human intention and converts it into codified, executable law (GAD documents).

This is not just a feature - **this IS the product**.

The cycle ensures:
1. **No guessing** - System asks when uncertain
2. **No surprises** - User validates before execution
3. **No drift** - Decisions are codified in architecture docs

---

## 🔄 The Five-Phase Loop

```
┌──────────────┐
│ 1. RAW       │  User drops file in workspace/inbox/
│    INTENT    │  (e.g. "Git sync is broken")
└──────┬───────┘
       │
       v
┌──────────────┐
│ 2. STEWARD   │  System boot reads inbox
│    CONTEXT   │  Injects as HIGH PRIORITY context
└──────┬───────┘  (Passive - no automatic action)
       │
       v
┌──────────────┐
│ 3. REFINEMENT│  Steward checks STEWARD.md preferences
│              │  If uncertain → Generate PROPOSAL_XY.md in inbox
└──────┬───────┘  If clear → Proceed with defaults
       │
       v
┌──────────────┐
│ 4. VALIDATION│  User edits PROPOSAL_XY.md
│              │  Yes/No/Change
└──────┬───────┘  Marks as APPROVED or REJECTED
       │
       v
┌──────────────┐
│ 5. CODIFICATION │  Steward executes approved plan
│                 │  Updates docs/architecture/GAD-XXX.md
└─────────────────┘  Archives inbox message
```

---

## 📋 Phase Details

### Phase 1: Raw Intent

**Input:** User creates file in `workspace/inbox/`
**Format:** Markdown file with arbitrary content
**Example:** `workspace/inbox/GIT_SYNC_ISSUE.md`

```markdown
# Issue: Git Operations Failing

When I push to remote, I get 403 errors.
Need to implement proper sync checks.
```

**System Response:** None (passive storage)

---

### Phase 2: Steward Context

**Trigger:** `./bin/system-boot.sh` or `kernel.boot()`
**Action:** Scan `workspace/inbox/` for `*.md` files
**Output:** Inbox messages loaded as `kernel.inbox_messages`

**Log Output:**
```
KERNEL: Inbox has 1 message(s) [HIGH PRIORITY]
KERNEL: >> INBOX: GIT_SYNC_ISSUE.md
```

**Context Injection:** Messages are available to Operator via `kernel.get_inbox_messages()`

**Key Principle:** System does NOT act automatically. It loads context and waits for operator to process.

---

### Phase 3: Refinement

**Actor:** Steward (via Operator or Specialist)
**Decision Tree:**

```python
if inbox_messages:
    for msg in inbox_messages:
        # Check STEWARD.md for policy
        policy = check_user_preferences(msg)

        if policy == "ask_first":
            # Generate proposal for user validation
            create_proposal(msg, output="workspace/inbox/PROPOSAL_XY.md")
            wait_for_user_approval()

        elif policy == "auto_execute":
            # Execute with defaults
            execute_with_defaults(msg)
            log_decision_to_gad(msg)

        else:
            # Manual intervention required
            notify_user("Manual decision needed")
```

**Proposal Format:**
```markdown
# PROPOSAL: Git-Ops Sync Strategy

**INBOX MESSAGE:** GIT_SYNC_ISSUE.md
**STATUS:** ⏳ AWAITING APPROVAL

## Summary
User reports 403 errors on git push. I propose implementing boot-time
git sync checks per ARCH-044.

## Proposed Solution
1. Add git fetch in system-boot.sh
2. Inject VIBE_GIT_STATUS env var
3. Create maintenance specialist for updates
4. Update STEWARD.md with update policy

## User Decision
- [ ] APPROVED - Execute as proposed
- [ ] APPROVED WITH CHANGES - (edit below)
- [ ] REJECTED - Do not proceed

**Changes:** (if any)
<!-- User can edit here -->

---
**AUTO-GENERATED:** 2025-11-22T14:30:00Z
```

---

### Phase 4: Validation

**Actor:** User (Human-in-Loop)
**Action:** Edit `PROPOSAL_XY.md`

**Options:**
1. **Approve:** Mark checkbox, system proceeds
2. **Modify:** Edit solution, mark checkbox, system uses modified version
3. **Reject:** Mark rejection, system archives without action

**Detection:**
- System checks for `[x] APPROVED` or `[x] REJECTED` on next boot
- Modified proposals are parsed for changes

---

### Phase 5: Codification

**Actor:** Steward (Autonomous)
**Actions:**

1. **Execute the plan**
   - Implement proposed changes
   - Run tests
   - Verify success

2. **Update GAD Documents**
   - Create/update `docs/architecture/GAD-XXX.md`
   - Document the decision and rationale
   - Include traceability to inbox message

3. **Update STEWARD.md**
   - Add new preferences if applicable
   - Update policies section

4. **Archive Inbox Message**
   - Move to `workspace/inbox/archive/YYYY-MM-DD_ORIGINAL_NAME.md`
   - Clean up proposals
   - Log completion

**Example GAD Update:**
```markdown
# GAD-044: Git-Ops Strategy

## Decision
Implement boot-time git sync checks to prevent stale repository state.

## Rationale
User reported 403 errors. Root cause: working on stale branch.
Need proactive sync detection.

## Implementation
- system-boot.sh: Add git fetch + status check
- kernel.py: Inject VIBE_GIT_STATUS in system prompt
- maintenance.py: New specialist for system updates

## Traceability
- **Inbox Message:** workspace/inbox/GIT_SYNC_ISSUE.md
- **Approval:** PROPOSAL_GIT_OPS_2025-11-22.md
- **Commit:** <commit-hash>
```

---

## 🔒 Guarantees

1. **No Silent Actions**
   - Inbox messages never auto-execute without policy
   - All proposals are explicit and user-visible

2. **Full Traceability**
   - Every decision links to inbox message
   - Every GAD links to approval
   - Archive preserves history

3. **Policy-Driven**
   - STEWARD.md defines behavior
   - User preferences are respected
   - Defaults are conservative (ask first)

4. **Crash-Safe**
   - File-based (survives crashes)
   - Idempotent (re-running is safe)
   - Atomic (proposals are complete or not)

---

## 🛠️ Example Use Cases

### Use Case 1: Git-Ops (ARCH-044)

**Inbox:** "Git sync is broken"
**Refinement:** System checks STEWARD.md → no policy found → generates proposal
**Validation:** User approves with modification (change update frequency)
**Codification:** Implement git-ops + update GAD-044 + archive inbox

### Use Case 2: Feature Request

**Inbox:** "Add dark mode to dashboard"
**Refinement:** System checks STEWARD.md → auto_execute policy → proceeds
**Validation:** (skipped - auto mode)
**Codification:** Implement feature + update GAD-XXX + archive inbox

### Use Case 3: Ambiguous Request

**Inbox:** "Make the app faster"
**Refinement:** System cannot determine approach → generates proposal with 3 options
**Validation:** User selects option 2 (optimize database queries)
**Codification:** Implement optimization + update GAD-XXX + archive inbox

---

## 🔄 Integration Points

### With Existing Systems

1. **GAD-006 (Asynchronous Intent)**
   - Refinement Cycle uses existing inbox infrastructure
   - `kernel._scan_inbox()` already implemented
   - No breaking changes required

2. **ARCH-044 (Git-Ops)**
   - First test case for Refinement Cycle
   - Validates the full loop
   - Proves file-based workflow

3. **STEWARD Protocol**
   - User preferences in STEWARD.md drive decisions
   - Manifests describe specialist capabilities
   - Delegation uses existing kernel routing

---

## 📊 Success Metrics

1. **Zero Surprise Rate:** No user complaints about "I didn't ask for that"
2. **Decision Latency:** Time from inbox drop to codification < 24h
3. **Archive Completeness:** 100% of inbox messages have GAD traceability
4. **Policy Coverage:** 100% of common scenarios have STEWARD.md policy

---

## 🚀 Next Steps

1. **Implement ARCH-044** (Git-Ops) as first test case
2. **Add Refinement Policy** to STEWARD.md
3. **Create Proposal Templates** in `.vibe/templates/`
4. **Build Archive System** for completed inbox messages

---

**Document Status:** ✅ COMPLETE
**Reviewed By:** STEWARD (Auto-Generated)
**Last Updated:** 2025-11-22
