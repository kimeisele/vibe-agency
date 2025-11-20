# CLAUDE.md - Operational Snapshot

**Version:** 2.1 | **Last Verified:** 2025-11-20 | **Status:** ✅ VERIFIED

---

## ✅ CLEANUP COMPLETE - FEATURE FREEZE LIFTED

**Cleanup Roadmap:** 16/16 Tasks Complete (100%)

All foundation cleanup tasks finished. System ready for feature development.

**Completion Summary:**
- Phase 0: Quarantine & Triage ✅ COMPLETE (4/4)
- Phase 1: Stop the Bleeding ✅ COMPLETE (4/4)
- Phase 2: Clean the Foundation ✅ COMPLETE (4/4)
- Phase 3: Verify & Document ✅ COMPLETE (4/4)

**See:** `CLEANUP_COMPLETION_REPORT.md` for detailed metrics and handoff.

**Feature Development:** NOW OPEN
- Subject to Test-First discipline (docs/policies/TEST_FIRST.md)
- Pre-push checks mandatory (./bin/pre-push-check.sh)
- Minimum 60% test coverage required

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
- **ARCHITECTURE_V2.md** — Conceptual model (the "should be")
- **SSOT.md** — Implementation decisions (the "is")
- **INDEX.md** — Documentation hub (START HERE for navigation)

---

## ✅ OPERATIONAL STATUS

| Component | Status | Verify |
|-----------|--------|--------|
| PLANNING | ✅ Works | `uv run pytest tests/test_planning_workflow.py -v` |
| CODING | ✅ Works | `uv run pytest tests/test_coding_workflow.py -v` |
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
- **Want to understand design?** → `ARCHITECTURE_V2.md`

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
