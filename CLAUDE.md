# CLAUDE.md - Operational Snapshot

**Version:** 2.1 | **Last Verified:** 2025-11-20 | **Status:** ✅ VERIFIED

---

## 🚀 ACTIVE ROADMAP: PHASE 2.6 - HYBRID AGENT INTEGRATION

**Current Roadmap:** `docs/roadmap/phase_2_6_hybrid_integration.json`
**Status:** 0/10 Tasks Complete (0%)
**Objective:** Unite Kernel (ARCH-021 to ARCH-025) with Specialists (ARCH-005+)

**Next Task:** ARCH-026 (SpecialistAgent Adapter)
**Run:** `./bin/next-task.py` to see current task

**Strategic Goals:**
1. **Integration Layer** - Make Specialists work with Kernel dispatch (SpecialistAgent adapter)
2. **Tool Protocol** - Give SimpleLLMAgent "hands" (WriteFile, ReadFile, extensible)
3. **Hybrid Pattern** - LLM-Agents + Script-Agents unified under VibeAgent protocol

**The Problem:**
Two parallel architectures with NO integration:
- **Universe A:** Kernel → SimpleLLMAgent (can think, cannot act)
- **Universe B:** STEWARD → Specialists (can act, not in Kernel)

**The Solution:**
HYBRID AGENT PATTERN - Both types implement VibeAgent protocol, both dispatched by Kernel, both recorded in Ledger.

**See:** `docs/architecture/ROADMAP_HYBRID_INTEGRATION.md` for detailed plan

---

## 🔄 PHASE 2.5 STATUS (In Progress)

**Roadmap:** `docs/roadmap/phase_2_5_foundation.json`
**Status:** 9/13 Tasks Complete (69%)
**Current Task:** ARCH-010 (Playbook-driven tool capability declaration)

**Key Achievements:**
- ✅ ARCH-001 to ARCH-009 complete (SQLite persistence + HAP pattern proven)
- ✅ BaseSpecialist interface implemented
- ✅ All 5 specialists extracted (Planning, Coding, Testing, Deployment, Maintenance)
- ✅ Orchestrator refactored to pure routing logic

**Remaining:** ARCH-010 to ARCH-013 (capability security + documentation)

---

## ✅ CLEANUP COMPLETE (Archived)

**Previous Roadmap:** Cleanup & Stabilization - 16/16 Tasks (100%)
**Archived:** `docs/archive/cleanup_roadmap_completed_2025-11-20.json`
**Completion:** 2025-11-20

**Key Wins:**
- Boot reliability: Fail → 100% success
- Tests: 369 → 631 (+71% increase)
- Import system fixed (40+ sys.path hacks removed)
- Provider tests: 0% → 70% coverage

**See:** `docs/archive/CLEANUP_COMPLETION_REPORT.md` for metrics

---

## ⚠️ DEVELOPMENT DISCIPLINE

**Test-First Required:**
- Minimum 80% test coverage for new code (Phase 2.5 standard)
- Pre-push checks mandatory (`./bin/pre-push-check.sh`)
- No claims without passing tests

---

## 🎯 CORE PRINCIPLES (Never Change)

1. Don't trust "Complete ✅" without passing tests
2. Test first, then claim complete
3. When code contradicts tests, trust tests
4. **When in doubt: RUN THE VERIFICATION COMMAND**
5. Always use `./bin/pre-push-check.sh` before git push

---

## 📖 What This Repo Is

**vibe-agency** = File-based prompt framework for AI-assisted software project planning.

Core flow (MVP - DELEGATION ONLY):
```
Claude Code (operator) ← file-based delegation (.delegation/) ← vibe-cli → Core Orchestrator → SDLC Phases → Agents
```

**See also:**
- **INDEX.md** — Documentation hub (START HERE for navigation)
- **ARCHITECTURE_CURRENT_STATE.md** — Current system design
- **docs/architecture/** — Detailed architecture documentation

---

## ✅ OPERATIONAL STATUS

| Component | Status | Verify |
|-----------|--------|--------|
| PLANNING | ✅ Works | `uv run pytest tests/test_orchestrator_state_machine.py -v` |
| CODING | ✅ Works | `uv run pytest tests/test_core_orchestrator_tools.py -v` |
| DEPLOYMENT | ✅ Works | `uv run pytest tests/test_deployment_workflow.py -v` |
| TESTING | ⚠️ Stub | Minimal implementation |
| MAINTENANCE | ⚠️ Stub | Minimal implementation |

**Test Health:** 369/383 passing (96.3%)
**Expected Failures:** 1 (documented in INDEX.md)

**Full verification (39 tests):**
```bash
./bin/verify-claude-md.sh
```

Report: `.claude_md_verification_report.json`

---

## 🚀 Quick Start

**Verify system is healthy:**
```bash
make verify  # or ./bin/verify-claude-md.sh
```

**See full context:**
```bash
./bin/show-context.py
```

**Bootstrap a new session (recommended):**
```bash
./bin/system-boot.sh
```

This will:
- Run pre-flight checks
- Display system health and session context
- Show available playbook routes for domain-specific workflows
- Initialize STEWARD with full context

**Before committing:**
```bash
./bin/pre-push-check.sh
```

---

## 📚 Documentation Index

**→ Go to INDEX.md for complete navigation**

Quick links:
- **New agent?** → `docs/GETTING_STARTED.md`
- **Need policies?** → `docs/policies/AGENT_DECISIONS.md`
- **How to decide if code is ready?** → `docs/policies/DEVELOPMENT_STANDARDS.md`
- **What NOT to do?** → `docs/philosophy/ANTI_PATTERNS.md`
- **System broken?** → `docs/TROUBLESHOOTING.md`
- **Want to understand design?** → `docs/architecture/ARCHITECTURE_CURRENT_STATE.md`

---

## ⚠️ Known Issues

**Currently blocking:** None (all core workflows passing)

## 📊 GAD Implementation Status

**Complete:** 9/15 GADs (60%)
**Partial:** 2/15 GADs (13%)
**Recent:** GAD-500 Week 1 & GAD-501 Layer 0-1 completed 2025-11-18

See full registry: `docs/architecture/GAD_IMPLEMENTATION_STATUS.md`

---

## 🔄 File Maintenance

This file is:
- ✅ Kept lean (~120 lines) — Navigation → INDEX.md
- ✅ Auto-verified by `./bin/verify-claude-md.sh` (runs 39 tests)
- ✅ Never contains update history (use git log)
- ✅ Never used as Makefile band-aid (use proper scripts)

---
