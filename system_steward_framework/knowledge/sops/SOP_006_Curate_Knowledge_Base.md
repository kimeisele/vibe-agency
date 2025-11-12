# SOP-006: Curate and Update Knowledge Base

**PURPOSE:** To provide a formal, governed process for identifying, reviewing, and updating knowledge base (KB) files (*.yaml) across AOS. Ensures semantic integrity, prevents conflicting rules, and maintains governance through CODEOWNERS and semantic audits.

**SCOPE:** Applies to all knowledge base files in:
- `/agency_os/*/knowledge/` (Framework-specific KBs)
- `/agency_os/00_system/knowledge/` (System-wide KBs, including AOS_Ontology.yaml)

**PRE-CONDITION:** A change to a KB file is identified (via bug report, feedback loop, or proactive governance review).

**POST-CONDITION:**
1. KB file update is validated against AOS_Ontology.yaml (semantic audit passes).
2. Appropriate Knowledge Curator(s) (via CODEOWNERS) review and approve the change.
3. Change is merged to main and CI/CD deploys updated KB to operational systems.
4. System learns: If the change was triggered by an operational issue, the fix is documented and fed into feedback loops (Task 3 in Report).

---

## STEP-BY-STEP PROCESS

### **Phase 1: Identification**

**Goal:** Detect that a KB change is needed and classify its type.

#### Step 1.1 - (Any Stakeholder) Identify Issue

An issue is identified through one of these mechanisms:

1. **Bug Report:** User or agent reports a failure (e.g., "FAE_constraints.yaml says feature X is v1.0-incompatible, but we need it")
2. **Feedback Loop:** AOS monitoring detects operational anomalies (e.g., QA_VALIDATOR repeatedly fails with same error)
3. **Proactive Audit:** Knowledge Curator runs semantic_audit.py and discovers conflicts
4. **Evolution:** New framework or agent requires new KB rules

**Action:** Open a GitHub Issue with:
- **Title:** `[KB UPDATE] <Framework>: <Brief Description>`
- **Body:**
  - Which KB file(s) affected (e.g., `FAE_constraints.yaml`)
  - What is the current problem/gap?
  - What is the proposed change?
  - Why is this change needed? (evidence: bug, user request, audit finding, etc.)

**Example Issue:**
```
Title: [KB UPDATE] Planning Framework: Reduce max_complexity threshold for v1.0

Body:
KB File: FAE_constraints.yaml (nfr_conflicts section)
Problem: Current threshold for "web_scale_scalability" allows complexity that v1.0 teams cannot handle
Evidence: BUG-202 (team overloaded), BUG-203 (project failed)
Proposed: Reduce from "web_scale" to "scalable_monolith" as default v1.0 recommendation
```

---

#### Step 1.2 - (Knowledge Curator) Classify Severity

The Knowledge Curator (assigned by CODEOWNERS) classifies the issue:

| Severity | Definition | Review Timeline | Examples |
|----------|-----------|-----------------|----------|
| **CRITICAL** | Blocks production, security risk, contradicts multiple KBs | < 24 hours | Security vulnerability in rule, framework blocker, data corruption risk |
| **HIGH** | High-impact rule error, affects multiple features | < 1 week | Incorrect time estimate, missing dependency, logical conflict |
| **MEDIUM** | Clarification, missing example, edge case refinement | < 2 weeks | Add missing example, clarify wording, add deprecation notice |
| **LOW** | Documentation, formatting, non-functional | < 1 month | Grammar fix, example improvement, link update |

**Action:** Add label to GitHub Issue: `kb-severity/critical`, `kb-severity/high`, etc.

---

### **Phase 2: Change Proposal**

**Goal:** Define the exact KB change and validate it against ontology before implementation.

#### Step 2.1 - (Developer or Curator) Propose Change

Create a **detailed change proposal** as a comment on the GitHub Issue:

**Proposal Template:**

```markdown
## PROPOSED CHANGE

**KB File(s):** FAE_constraints.yaml

**Current State:**
```yaml
nfr_conflicts:
  - id: "FAE-NFR-001"
    nfr_a: "real_time_performance_latency_<50ms"
    nfr_b: "serverless_architecture"
```

**Proposed New State:**
```yaml
nfr_conflicts:
  - id: "FAE-NFR-001"
    nfr_a: "real_time_performance_latency_<100ms"  # CHANGED: Relaxed from 50ms
    nfr_b: "serverless_architecture"
```

**Ontology Validation:**
- Terms used: `nfr_conflict` ✓ (defined in AOS_Ontology.yaml)
- Type check: `nfr_a` and `nfr_b` are strings ✓
- Owner consistency: `@aos-knowledge-curator-fae` ✓
- No circular dependencies detected ✓

**Impact Assessment:**
- **Affected Rules:** GATE_NFR_VALIDATION in CODE_GEN_quality_rules.yaml (indirect)
- **Affected Agents:** VIBE_ALIGNER (uses FAE_constraints during education phase)
- **Backward Compat:** ✓ Relaxing a constraint is backward-compatible (fewer rejections)
- **Related Issues:** BUG-202, BUG-203

**Risk:** LOW (relaxation, not tightening)
```

---

#### Step 2.2 - (System) Run Semantic Audit (Dry-Run)

The proposer (or CI/CD bot) runs the semantic audit script in **dry-run mode** to validate the proposed change:

```bash
python scripts/semantic_audit.py \
  --kb-file agency_os/01_planning_framework/knowledge/FAE_constraints.yaml \
  --proposed-change proposed_fae_nfr001.yaml \
  --dry-run
```

**Expected Output:**
```
✓ AUDIT_001: All terms defined in AOS_Ontology.yaml
✓ AUDIT_002: All types match (string, numeric_multiplier, etc.)
✓ AUDIT_003: Owner consistency check passed
✓ AUDIT_004: No circular dependencies
✓ AUDIT_005: All terms are used in at least one KB
  WARNING: FAE-TIME-020 (saml_sso_integration) not referenced in any active rule
  INFO: Consider deprecation if not needed
✓ Overall: Change is semantically valid
```

**If audit fails:** Return to Phase 2.1 and revise proposal. Do NOT proceed to Phase 3.

---

### **Phase 3: Git Implementation**

**Goal:** Create a Git branch, implement the change, and open a Pull Request (PR).

#### Step 3.1 - (Developer) Create Feature Branch

```bash
git checkout main && git pull
git checkout -b feat/kb-update-fae-nfr-001-$(date +%s)
```

**Branch Naming:** `feat/kb-update-<framework>-<change-id>-<timestamp>`

---

#### Step 3.2 - (Developer) Implement Change

Edit the KB file and apply the proposed change:

```bash
# Edit the file
nano agency_os/01_planning_framework/knowledge/FAE_constraints.yaml

# Stage the change
git add agency_os/01_planning_framework/knowledge/FAE_constraints.yaml

# Commit with descriptive message
git commit -m "feat: Update FAE_constraints.yaml - Relax NFR-001 latency from 50ms to 100ms for serverless compatibility

Resolves: Issue #XYZ
Related: BUG-202, BUG-203

Changes:
- Modified FAE-NFR-001 nfr_a from 'latency_<50ms' to 'latency_<100ms'
- Rationale: Serverless cold-start incompatibility reported in 2 production incidents

Semantic Audit: PASSED
- All terms defined in AOS_Ontology.yaml
- No type violations
- No circular dependencies detected
"
```

---

#### Step 3.3 - (CI/CD) Automatic Semantic Audit

When the PR is created, GitHub Actions automatically triggers `semantic_audit.py`:

```yaml
# .github/workflows/kb-validation.yml (example)
name: KB Semantic Validation

on:
  pull_request:
    paths:
      - 'agency_os/*/knowledge/*.yaml'
      - 'agency_os/00_system/knowledge/*.yaml'

jobs:
  semantic-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Semantic Audit
        run: |
          python scripts/semantic_audit.py \
            --mode validate \
            --changed-files ${{ github.event.pull_request.files }}
```

**If audit fails:** CI/CD blocks merge. Developer must fix and force-push to branch.

---

### **Phase 4: Human Review (CODEOWNERS)**

**Goal:** Knowledge Curator(s) review the semantic and business impact of the change.

#### Step 4.1 - (GitHub) Auto-Assign Reviewers

CODEOWNERS automatically assigns reviewers based on which KB file was modified:

- Change to `FAE_constraints.yaml` → `@aos-knowledge-curator-fae`
- Change to `CODE_GEN_quality_rules.yaml` → `@aos-knowledge-curator-code`
- Change to `AOS_Ontology.yaml` → `@aos-knowledge-curators` (all curators)

The PR is marked as "Blocked" until required reviewers approve.

---

#### Step 4.2 - (Knowledge Curator) Review & Approve

The curator reviews the PR for:

1. **Semantic Correctness** (5 min)
   - Does the change make sense in the context of related rules?
   - Are there conflicting changes in other KBs?

2. **Business Impact** (10 min)
   - Is the rationale compelling?
   - Are there unintended consequences?

3. **Ontology Consistency** (5 min)
   - Is semantic_audit.py output clean?
   - Are all terms properly defined?

**Review Checklist (for curator):**

```markdown
## KB Review Checklist

- [ ] Semantic audit passes (CI/CD green)
- [ ] Change rationale is clear and evidence-based
- [ ] No conflicting changes in related KBs
- [ ] Owner fields are consistent
- [ ] Examples provided (if new terms introduced)
- [ ] Backward compatibility assessed
- [ ] No security implications overlooked

**Curator Decision:**
- [ ] **APPROVE** - Ready to merge
- [ ] **REQUEST CHANGES** - See comments below
- [ ] **COMMENT** - FYI, but developer can merge after addressing

## Comments

[Curator writes feedback here]
```

**Approval:** Curator clicks "Approve" on the PR.

---

### **Phase 5: Merge & Deploy**

**Goal:** Merge the change and make it available to AOS agents.

#### Step 5.1 - (Developer) Merge PR

Once curator approves:

```bash
git switch main && git pull
git merge --ff-only feat/kb-update-fae-nfr-001-<timestamp>
git push origin main
```

Or use GitHub UI: Click "Merge pull request" → "Confirm merge".

---

#### Step 5.2 - (CI/CD) Deploy to Operational KB

GitHub Actions triggers post-merge workflow:

```yaml
# .github/workflows/kb-deploy.yml (example)
on:
  push:
    branches:
      - main
    paths:
      - 'agency_os/*/knowledge/*.yaml'

jobs:
  deploy-kb:
    runs-on: ubuntu-latest
    steps:
      - name: Load Updated KB into Operational Store
        run: |
          # Example: Copy KB files to a runtime-accessible location
          # or notify KBMS (Knowledge Base Management System) to refresh
          cp -r agency_os/*/knowledge/*.yaml /var/lib/aos-kbms/
          # Notify agents that KB has changed
          curl -X POST http://aos-runtime:8080/reload-kb
```

The KB is now available to all AOS agents.

---

### **Phase 6: Monitoring & Feedback**

**Goal:** Track the impact of the KB change on system behavior.

#### Step 6.1 - (System Monitoring) Watch Metrics

After deployment, AOS monitoring watches for changes in:
- Task success/failure rates
- Agent performance metrics
- Validation errors related to modified rules

**Example Metrics Dashboard:**

```
KB Change: FAE-NFR-001 (latency threshold relaxed)
Deployment Time: 2025-11-13 14:30 UTC

Metric                          Before    After     Delta
VIBE_ALIGNER success rate       92.1%     94.7%    +2.6% ✓
QA_VALIDATOR failures (NFR)      8.2%      5.1%    -3.1% ✓
CODE_GENERATOR avg time         12.3s     11.8s    -0.5s ✓
Production incidents (24h)        2         0       -2   ✓

Status: HEALTHY - Change appears beneficial
```

#### Step 6.2 - (System) Feed Back into Loops

If the change produces positive results:
- ✓ Close the GitHub Issue as "RESOLVED"
- ✓ Log the success in AOS audit trail
- ✓ If this is part of RLHF (Task 3 in Report), feed success signal to reward model

If negative results detected:
- ⚠ Create new issue: "[KB REVERT]" to rollback change
- ⚠ Follow SOP_006 again (with CRITICAL priority)

---

## TROUBLESHOOTING & EDGE CASES

### Case A: Semantic Audit Fails at Merge Time

**Symptom:** PR passes initial audit, but fails at merge (another PR modified the same KB).

**Action:**
1. Developer rebases PR against updated main: `git rebase origin/main`
2. Resolves merge conflicts in *.yaml
3. Re-runs semantic audit locally: `python scripts/semantic_audit.py --changed-files <files>`
4. Force-pushes: `git push -f origin <branch>`
5. CI/CD re-validates; if passed, curator re-approves

### Case B: CRITICAL KB Issue Requires Immediate Fix

**Symptom:** Production issue tied to KB rule error; SOP_006's 1-2 week timeline is too slow.

**Action:**
1. Knowledge Curator escalates to System Architect
2. System Architect (with CRITICAL label) bypasses formal review (but NOT semantic audit)
3. Change is fast-tracked: Identify → Audit → Merge (< 4 hours)
4. Post-merge, a full SOP_006 review is conducted for documentation purposes

### Case C: Proposed Change Conflicts with Another KB

**Symptom:** Change to `FAE_constraints.yaml` contradicts rule in `CODE_GEN_constraints.yaml`.

**Action:**
1. Semantic audit detects this and flags as AUDIT_004 (circular dependency / conflict)
2. Curator escalates to System Architect
3. Both KBs are reviewed together
4. Conflict is resolved by clarifying ownership and establishing precedence
5. Both KBs are updated in a single, coordinated PR

---

## RELATED DOCUMENTS

- **AOS_Ontology.yaml:** Defines all semantic terms used in KBs; sourced by semantic_audit.py
- **.github/CODEOWNERS:** Assigns Knowledge Curators to specific KB files
- **scripts/semantic_audit.py:** Automated validation engine; blocks merges if audit fails
- **docs/GOVERNANCE_MODEL.md:** High-level governance architecture

---

## CHANGE HISTORY

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2025-11-12 | AOS Setup | Initial SOP |

---

**Last Updated:** 2025-11-12
**Maintained By:** @aos-knowledge-curators
