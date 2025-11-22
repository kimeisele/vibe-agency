# vibe-agency Documentation Index

**Last Updated:** 2025-11-22 | **Source of Truth:** This file + git log

---

## 🎯 START HERE

- **[STEWARD.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/STEWARD.md)** — 📌 **SINGLE SOURCE OF TRUTH** (Project in a Box)
- **[CLAUDE.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/CLAUDE.md)** — Minimal stub (redirects to STEWARD.md)
- **[ARCHITECTURE_CURRENT_STATE.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/architecture/ARCHITECTURE_CURRENT_STATE.md)** — Current system design v4.0
- **[Architecture Docs](https://github.com/kimeisele/vibe-agency/tree/main/docs/architecture)** — Detailed architecture documentation

---

## 📋 QUICK ACTIONS

```bash
# System Health & Verification
./bin/system-boot.sh                    # Bootstrap new session (Layer 0 + Layer 1)
./bin/vibe status                       # System status & health check
./bin/show-context.py                   # Full session context (git, tests, handoff)

# System Snapshot (HERZSTÜCK) ⭐
uv run apps/agency/cli.py --snapshot    # Generate system introspection (ARCH-038)

# Quality Gates
./bin/pre-push-check.sh                 # Pre-push quality checks
uv run pytest                           # Run test suite (626 tests)
```

---

## 🗂️ DOCUMENTATION STRUCTURE

### **Getting Started (Read First)**
- **[STEWARD.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/STEWARD.md)** — 📌 Start here (complete system reference)
- [STRATEGIC_PLAN_2025-11-18.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/STRATEGIC_PLAN_2025-11-18.md) — 4-week roadmap for core stability
- [CHANGELOG.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/CHANGELOG.md) — Release history (v0.5.0 latest)

### **Policies & Standards**
- [AGENT_DECISIONS.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/policies/AGENT_DECISIONS.md) — Decision reference (15 questions)
- [GOVERNANCE_MODEL.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/GOVERNANCE_MODEL.md) — Governance & Soul rules

### **Architecture & Design**
- [ARCHITECTURE_CURRENT_STATE.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/architecture/ARCHITECTURE_CURRENT_STATE.md) — System design v4.0
- [GAD_IMPLEMENTATION_STATUS.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/architecture/GAD_IMPLEMENTATION_STATUS.md) — All GAD tracking
- [GAD-000_OPERATOR_INVERSION.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/architecture/GAD-0XX/GAD-000_OPERATOR_INVERSION.md) — Foundation principle
- [Architecture Docs](https://github.com/kimeisele/vibe-agency/tree/main/docs/architecture) — All architecture documentation
- [Phase Roadmaps](https://github.com/kimeisele/vibe-agency/tree/main/docs/roadmap) — Phase 2.5, 2.6, 3.0

### **Systems & Components**
- [vibe_core/](https://github.com/kimeisele/vibe-agency/tree/main/vibe_core) — Core runtime and agent implementation
- [apps/agency/](https://github.com/kimeisele/vibe-agency/tree/main/apps/agency) — Agency orchestrator and specialized agents
- [tests/](https://github.com/kimeisele/vibe-agency/tree/main/tests) — All verification tests (626 collected)

### **Scripts & Tools**
- `bin/vibe` — Main CLI entrypoint (status, run, etc)
- `bin/system-boot.sh` — Session bootstrap (Layer 0 + Layer 1 boot sequence)
- `bin/show-context.py` — Full session context (git, linting, tests, handoff)
- `bin/pre-push-check.sh` — Quality gates (linting, formatting, status updates)
- `apps/agency/cli.py` — Agency orchestrator CLI (--snapshot, --mission, etc)
- `tests/` — All verification tests (626 collected)

---

## 🔍 BY USE CASE

### "I'm a new agent" / "Where do I start?"
→ **[STEWARD.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/STEWARD.md)** — Complete system reference

### "What's the strategic direction?"
→ [STRATEGIC_PLAN_2025-11-18.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/STRATEGIC_PLAN_2025-11-18.md) — 4-week roadmap

### "Which GADs are implemented?"
→ [GAD_IMPLEMENTATION_STATUS.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/architecture/GAD_IMPLEMENTATION_STATUS.md) — All GAD tracking

### "I have a decision to make"
→ [AGENT_DECISIONS.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/policies/AGENT_DECISIONS.md) — Decision framework

### "I want to understand the system design"
→ [ARCHITECTURE_CURRENT_STATE.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/architecture/ARCHITECTURE_CURRENT_STATE.md) — System design v4.0

### "What's the system status?"
→ Run: `./bin/vibe status` or `./bin/show-context.py`

### "How do I get a system snapshot?"
→ Run: `uv run apps/agency/cli.py --snapshot` (ARCH-038)

### "Can I run a fresh environment test?"
→ `./tests/test_cold_boot.sh`

### "I want to see the full status"
→ `./bin/show-context.py` or `make status`

### "What's the current system snapshot?" ⭐ HERZSTÜCK
→ Run: `uv run apps/agency/cli.py --snapshot` (ARCH-038)
→ Docs: **[STEWARD.md § System Snapshot](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/STEWARD.md)** — System heartbeat & introspection

---

## 📊 CURRENT STATUS

### Test Health
- **Total:** 626 tests collected
- **Status:** ✅ Core workflows verified (PLANNING, CODING, DEPLOYMENT passing)
- **Latest:** ARCH-041 System Introspection (2025-11-22)

### Verification
- **System Snapshot:** ✅ Operational (ARCH-038)
- **Linting:** ✅ Passing (Ruff + isort)
- **Git:** ✅ Clean
- **System Sovereignty:** ✅ Verified (ARCH-040)

### Blocking Issues
None (all critical workflows passing)

---

## 🚀 CORE WORKFLOWS

### PLANNING Phase
- Status: ✅ Works (test_planning_workflow.py passes)
- Handlers: VIBE_ALIGNER, LEAN_CANVAS_VALIDATOR, GENESIS_BLUEPRINT, MARKET_RESEARCHER, TECH_RESEARCHER, FACT_VALIDATOR, USER_RESEARCHER
- Knowledge bases: FAE_constraints.yaml, FDG_dependencies.yaml, APCE_rules.yaml

### CODING Phase
- Status: ✅ Works (test_coding_workflow.py passes)
- Handler: coding_handler.py (5-phase code generation workflow)

### DEPLOYMENT Phase
- Status: ✅ Works (test_deployment_workflow.py passes)
- Handler: deployment_handler.py (4-phase deployment workflow)
- Tests: E2E validation on merge

### TESTING & MAINTENANCE Phases
- Status: ⚠️ Stub (minimal implementation)
- Transition logic: Working
- Full implementation: Deferred

---

## 🔐 SESSION CONTEXT

**Current Branch:** `claude/update-steward-documentation-01SYsqe5T54BpfjnVNybuQtC`

**Session Handoff:** `.session_handoff.json` (auto-updated by system-boot.sh)

**System Snapshot:** `uv run apps/agency/cli.py --snapshot` (ARCH-038) ⭐

**System Status:** `.system_status.json` (auto-updated by pre-push-check.sh)

**View context:** `./bin/show-context.py`

---

## 🔄 HOW TO MAINTAIN THIS INDEX

This index is:
- ✅ Updated when new major doc sections are added
- ✅ Links verified by developers before merge
- ✅ Reflects current file structure exactly
- ✅ Never contains update history (use `git log`)
- ✅ Central hub for documentation discovery

**Update this file when:**
- Adding new doc sections
- Moving files to different paths
- Creating new policy documents
- Adding new GAD initiatives

**Do NOT:**
- Add update history to this file
- Use this as a changelog
- Add implementation details (those go in the target docs)

---

## 📚 PRINCIPLES OF THIS DOCUMENTATION

1. **Single source of truth:** Tests define what works, not docs
2. **Git is absolute truth:** All metrics verified via git, not documentation claims
3. **Linked, not monolithic:** Docs point to each other, not duplicated
4. **Always runnable:** Every claim is verified or deferred
5. **Lean is better:** Documentation grows naturally from code, not imposed
6. **System Snapshot = Heartbeat:** ARCH-038 snapshot is the living system state

---
