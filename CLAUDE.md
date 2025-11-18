# CLAUDE.md - Operational Snapshot

**Version:** 2.0 | **Last Verified:** 2025-11-18 | **Status:** ✅ VERIFIED

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
Claude Code (operator) ← STDOUT/STDIN → vibe-cli → Core Orchestrator → SDLC Phases → Agents
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

**Test Health:** 335/349 passing (97.1%)
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

**Bootstrap a new session:**
```bash
./bin/system-boot.sh
```

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

See full registry: `docs/architecture/GAD-5XX/KNOWN_ISSUES_REGISTRY.md`

---

## 🔄 File Maintenance

This file is:
- ✅ Kept lean (~120 lines) — Navigation → INDEX.md
- ✅ Auto-verified by `./bin/verify-claude-md.sh` (runs 39 tests)
- ✅ Never contains update history (use git log)
- ✅ Never used as Makefile band-aid (use proper scripts)

---
