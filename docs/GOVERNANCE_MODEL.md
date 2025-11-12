# AOS Governance Model (Phase 1: Foundation)

**Version:** 1.0
**Status:** Active (Phase 1 Implementation)
**Last Updated:** 2025-11-12
**Maintained By:** @aos-system-architect, @aos-knowledge-curators

---

## Executive Summary

The AOS Governance Model establishes a **formal, Git-based process** for managing the Knowledge Bases (KBs) that encode system intelligence. This document describes the foundational governance layer required for AOS v0.2+ to be reliable, auditable, and self-improving.

**Key Principles:**
1. **Knowledge-as-Code:** KB files (*.yaml) are treated like source code—versioned, reviewed, and validated.
2. **Semantic Authority:** AOS_Ontology.yaml is the single source of truth for all semantic terms across KBs.
3. **Curator-Driven Governance:** Domain experts (Knowledge Curators) are responsible for the semantic integrity of their KBs.
4. **Automated Validation:** CI/CD enforces semantic consistency before changes are merged.
5. **Traceability:** Every KB change is tracked, reviewed, and auditable.

---

## Problem Statement: Why Governance is Needed

### The Gaps (from Deep Research Report)

**Gap 3: Undefined Knowledge Management**
- Status: KBs are static artifacts with no formal curation process
- Risk: Semantic drift (terms reused with different meanings), stale rules, conflicting constraints
- Example: "reliability" means different things in FAE_constraints.yaml vs. QA_constraints.yaml

**Gap 5: Myopic Production Feedback Loop**
- Status: System reacts to bugs but doesn't strategically improve KBs
- Risk: Same error patterns repeat; no systematic learning from failures
- Example: QA validation fails 5 times for the same missing constraint; KB never updated

### Why This Matters for v0.2+

As AOS scales to multiple frameworks (Planning, Code Gen, QA, Deploy, Maintenance), the KBs become the **critical path** for system reliability:
- Agent behavior is determined by KB rules
- Bad rules → bad decisions → failed projects
- Without governance, KBs become "tribal knowledge" (undocumented, inconsistent)

---

## Governance Architecture

### Layer 1: Semantic Foundation (AOS_Ontology.yaml)

**What:** A master data dictionary that defines all semantic terms used across KBs.

**Scope:**
- 100+ semantic terms (concept, constraint, pattern, process, role)
- Type definitions (numeric_multiplier, timestamp, boolean, etc.)
- Ownership assignments (which curator is responsible)
- Semantic categories (feasibility, architecture, quality_assurance, etc.)

**Example Term Definition:**
```yaml
terms:
  feature_scope_conflict:
    definition: "A feature incompatible with v1.0 due to complexity"
    type: "concept"
    used_in:
      - "FAE_constraints.yaml"
    owner: "@aos-knowledge-curator-fae"
    semantic_category: "feasibility"
```

**Why This Matters:**
- Prevents semantic variation (same concept, different names across KBs)
- Enables automated validation (semantic_audit.py checks for term misuse)
- Single point of evolution (add new term → automatically available to all KBs)

### Layer 2: CODEOWNERS (Git-Based Access Control)

**What:** A GitHub/GitLab CODEOWNERS file that maps KB files to Knowledge Curators.

**Mechanism:**
1. Developer creates PR that modifies `FAE_constraints.yaml`
2. GitHub automatically requests review from `@aos-knowledge-curator-fae` (via CODEOWNERS)
3. Curator must approve before PR can merge
4. With "Require review from Code Owners" enabled, this is **mandatory**

**CODEOWNERS Structure:**

```
# Core Knowledge Bases
/agency_os/01_planning_framework/knowledge/FAE_constraints.yaml @aos-knowledge-curator-fae
/agency_os/02_code_gen_framework/knowledge/CODE_GEN_constraints.yaml @aos-knowledge-curator-code
/agency_os/03_qa_framework/knowledge/QA_constraints.yaml @aos-knowledge-curator-qa

# Central Ontology (requires ALL curators)
/agency_os/00_system/knowledge/AOS_Ontology.yaml @aos-knowledge-curators

# Fallback
* @aos-system-architect
```

**Why This Matters:**
- Enforces human review before KB changes go live
- Creates clear ownership (no "who's responsible for this rule?" ambiguity)
- Integrates with Git workflow (curators don't need special tools)

### Layer 3: Semantic Audit (CI/CD Validation)

**What:** An automated Python script (`semantic_audit.py`) that validates KB files.

**Validation Rules (from AOS_Ontology.yaml):**

| Audit Rule | Check | Failure | Example |
|-----------|-------|---------|---------|
| **AUDIT_001** | All terms used in KB must be defined in ontology | ERROR | Using `feature_scope_conflict` without ontology entry |
| **AUDIT_002** | All value types must match term definition | ERROR | Setting `complexity_multiplier: "high"` (should be numeric) |
| **AUDIT_003** | Term owner must be consistent across KBs | WARNING | Same term owned by different curators in different files |
| **AUDIT_004** | No circular dependencies between term definitions | ERROR | Term A references B, B references A → conflict |
| **AUDIT_005** | Detect orphaned terms (defined but unused) | INFO | Term in ontology but no KB references it |
| **AUDIT_006** | Stale terms (last_updated > 6 months ago) | INFO | Old constraint no longer relevant |

**Execution:**
- Runs automatically on every PR (GitHub Actions)
- Blocks merge if ERRORS detected
- Allows merge if only WARNINGS/INFO

**Why This Matters:**
- Catches semantic errors before they reach production
- Prevents invalid YAML/schema violations
- Documents evolution of KBs over time

### Layer 4: Standard Operating Procedures (SOP_006)

**What:** A formal, step-by-step process for identifying, proposing, reviewing, and deploying KB changes.

**The Process:**

```
Identification (Phase 1)
    ↓
Change Proposal (Phase 2)
    ↓
Git Implementation (Phase 3)
    ↓
Semantic Audit (CI/CD, automated)
    ↓
CODEOWNERS Review (Phase 4, human)
    ↓
Merge & Deploy (Phase 5)
    ↓
Monitoring & Feedback (Phase 6)
```

**Key Features:**
- **Structured:** Each phase has clear inputs/outputs
- **Traceable:** Every change linked to issue/PR/commit
- **Evidence-Based:** Proposals must include rationale (bug report, monitoring data, etc.)
- **Reversible:** Change can be reverted if negative impact detected

**Why This Matters:**
- Moves KB curation from ad-hoc to industrialized process
- Enables learning: operational failures → KB improvements → better decisions
- Foundation for Task 3 (Feedback Loops) in Deep Research Report

---

## Knowledge Curator Roles

### Role Definition

A **Knowledge Curator** is a domain expert responsible for the semantic integrity of one or more KBs.

### Responsibilities

| Task | Frequency | Time | Owner |
|------|-----------|------|-------|
| Review KB PRs | Per PR | 15 min | Curator |
| Respond to semantic audit warnings | Daily | 10 min | Curator |
| Quarterly KB review (stale rule cleanup) | Quarterly | 2 hours | Curator |
| Update/deprecate terms in ontology | As needed | 30 min | All curators together |

### Curator Assignments (Phase 1)

| Framework | KB Files | Curator | Contact |
|-----------|----------|---------|---------|
| Planning (01) | FAE, APCE, FDG | @aos-knowledge-curator-fae, @aos-knowledge-curator-apce, @aos-knowledge-curator-fdg | TBD |
| Code Gen (02) | CODE_GEN_* | @aos-knowledge-curator-code | TBD |
| QA (03) | QA_* | @aos-knowledge-curator-qa | TBD |
| Deploy (04) | DEPLOY_* | @aos-knowledge-curator-deploy | TBD |
| Maintenance (05) | MAINTENANCE_* | @aos-knowledge-curator-maintenance | TBD |
| System (00) | AOS_Ontology, ORCHESTRATION | @aos-system-architect | TBD |

**Note:** Curators for Planning Framework (FAE, APCE, FDG) are TBD and must be assigned in next phase.

---

## Integration with Feedback Loops (Task 3 - Future)

The governance model enables **systematic learning** through feedback loops:

```
AOS Runtime
    ↓ (operational metrics, errors)
    ↓
Monitoring & Alerting
    ↓ (detects anomalies)
    ↓
Trigger KB Review (Task 3)
    ↓ (Issue created)
    ↓
SOP_006 Process
    ↓ (Change proposed & reviewed)
    ↓
KB Updated
    ↓ (CI/CD deploys)
    ↓
AOS Runtime (improved)
```

This closes the loop: **Observation → Analysis → Improvement → Action**.

---

## Implementation Roadmap

### Phase 1: Foundation (CURRENT - 2025-11-12)

**Status:** ✅ Implemented

- ✅ AOS_Ontology.yaml (central semantic definition)
- ✅ .github/CODEOWNERS (curator assignments)
- ✅ semantic_audit.py (CI/CD validation)
- ✅ SOP_006_Curate_Knowledge_Base.md (formal process)
- ✅ This documentation

**Deliverables:**
- Git-based KB management with CODEOWNERS
- Automated semantic validation (blocks invalid changes)
- Formal curation process (SOP_006)

**Impact:**
- ✓ Solves "Gap 3: Undefined Knowledge Management"
- ✓ Lays foundation for Task 3 (Feedback Loops)
- ✓ Enables scalable KB governance

### Phase 2: Runtime Integration (v0.3 - TBD)

**Status:** Planned (requires prompt_runtime.py)

- Context Engineering in prompt_runtime.py
- Dynamic KB loading (RAG into agent prompts)
- Real-time KB validation during agent execution

**See:** Task 1 in Deep Research Report

### Phase 3: Feedback Loops (v0.3 - TBD)

**Status:** Planned (requires operational monitoring)

- Operation Layer (EDD architecture)
- Trigger KB reviews from operational failures
- AITL/HITL feedback loops (STRATEGY_SYNTHESIZER agent)

**See:** Task 3 in Deep Research Report

### Phase 4: Autonomous Learning (v0.3+ - TBD)

**Status:** Vision (requires RLHF + TT-SI infrastructure)

- RLHF (slow, strategic learning from HITL signals)
- TT-SI (fast, tactical learning during inference)
- Self-improving agents that refine their own KBs

**See:** Task 3C in Deep Research Report

---

## Best Practices

### For Knowledge Curators

1. **Keep Terms in Sync**
   - When you add a constraint to your KB, ask: "Is this term in AOS_Ontology?"
   - If not, create a PR to add it to the ontology first

2. **Document Rationale**
   - Every KB rule should have a "why" comment
   - Example: `# FAE-TIME-002: OAuth adds 1-2 weeks based on real projects`

3. **Review PRs Thoroughly**
   - Run `semantic_audit.py --dry-run` locally before approving
   - Ask: "Does this change align with our framework principles?"

4. **Monitor for Stale Rules**
   - Quarterly review: Are there rules that no longer apply?
   - Mark as deprecated (don't delete immediately)

### For Developers

1. **Never Edit KB Files Directly in Main**
   - Always create a feature branch
   - Always include rationale in commit message

2. **Run Semantic Audit Before Creating PR**
   - `python scripts/semantic_audit.py --file <your_kb_file>`
   - Fix any errors before pushing

3. **Be Specific in Change Proposals**
   - Link to GitHub issues, monitoring data, or user reports
   - Explain the "why" in clear business terms

### For System Architect

1. **Monitor Audit Results**
   - Watch for trends (are certain rules frequently violated?)
   - Use audit patterns to guide v0.3 design

2. **Keep Ontology Lean**
   - Don't add 100 terms at once
   - Grow it incrementally as needs emerge

3. **Enable Curator Teams**
   - Ensure curators have time/resources to do their job
   - Quarterly sync calls to discuss ontology evolution

---

## Metrics & Health Checks

### Key Metrics

| Metric | Target | Check Frequency |
|--------|--------|-----------------|
| **KB PR Approval Time** | < 24 hours | Daily |
| **Semantic Audit Pass Rate** | > 95% | Per PR |
| **Stale Rules Detected** | < 5% of total | Monthly |
| **Curator Review Coverage** | 100% | Per PR |

### Monitoring Dashboard (Example)

```
AOS Governance Health Check
===========================

KB Files: 45
Total Terms: 127
Audit Pass Rate: 98%

Recent Changes:
- FAE_constraints.yaml (2 days ago)
- CODE_GEN_quality_rules.yaml (1 week ago)
- AOS_Ontology.yaml (5 days ago)

Curators Assignments:
- @aos-knowledge-curator-fae: 3 KBs, 12 open reviews
- @aos-knowledge-curator-code: 3 KBs, 5 open reviews
- @aos-knowledge-curator-qa: 3 KBs, 2 open reviews

Pending Actions:
- [URGENT] CRITICAL KB issue #XYZ - 2 days overdue
- [NORMAL] Quarterly stale rule cleanup for Deploy Framework
- [INFO] 3 terms in ontology not yet used (consider removal)
```

---

## FAQ & Troubleshooting

### Q: What if a Knowledge Curator is unavailable?

**A:** System Architect can approve PRs to their KBs as a fallback. Escalate to architecture team.

### Q: Can I bypass semantic audit for urgent fixes?

**A:** No. CRITICAL issues can be fast-tracked (4 hour timeline via System Architect), but semantic audit MUST pass. Governance without validation is ineffective.

### Q: How do I deprecate an old rule?

**A:** Via SOP_006:
1. Mark rule with `deprecated: true` in YAML
2. Document replacement or reason in comment
3. Create PR (semantic audit passes, curator approves)
4. After 6 months, remove deprecated rule

### Q: What if ontology term definitions conflict?

**A:** This is exactly what AUDIT_004 detects. Escalate to System Architect to resolve. Often requires clarifying scope/ownership.

---

## Related Documents

- **AOS_Ontology.yaml** - Central semantic definition (source of truth)
- **.github/CODEOWNERS** - Curator assignments (access control)
- **scripts/semantic_audit.py** - Validation engine (CI/CD automation)
- **SOP_006_Curate_Knowledge_Base.md** - Detailed process (step-by-step)
- **AGENCY_OS_DEEP_DIVE_REPORT.md** - Research & rationale (context)

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-12 | AOS Setup Team | Initial governance model (Phase 1) |

---

**Last Updated:** 2025-11-12
**Maintained By:** @aos-system-architect
**Status:** Active / Phase 1 Complete
