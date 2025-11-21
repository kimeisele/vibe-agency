# Changelog

All notable changes to the Vibe Agency project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Changed - 2025-11-15 - Foundation Hardening: UV Migration

**MAJOR INFRASTRUCTURE UPGRADE** - Migrated from pip to UV for faster, more reliable dependency management.

**Benefits:**
- ⚡ **10-15x faster local installs** (~10-20 sec vs 2-3 min)
- ⚡ **2-3x faster CI** (~1-2 min vs 3-5 min)
- 🔒 **Deterministic builds** via `uv.lock` (prevents version drift)
- 📦 **50% fewer config files** (consolidated into `pyproject.toml`)
- 🎯 **Simplified workflows** via Makefile (`make install`, `make test`, etc.)

**For Users (Quick Start):**
```bash
# Before
pip install -r requirements.txt
pip install pre-commit
pre-commit install

# After
make install    # One command does everything
```

**What Changed:**
- ✅ Added `pyproject.toml` - Unified project configuration (209 lines)
- ✅ Added `Makefile` - 25+ automation commands (`make help` to see all)
- ✅ Added `uv.lock` - Deterministic dependency lock file (1167 lines)
- ✅ Updated `setup.sh` - Now uses UV instead of pip
- ✅ Updated `.devcontainer/devcontainer.json` - Uses UV, adds mypy extension
- ✅ Updated GitHub Actions workflows - Use UV with caching (faster CI)
- ✅ Updated 4-layer dependency defense - All layers now UV-compatible
- ✅ Added comprehensive documentation (MIGRATION_NOTES.md, DEFENSE_STRATEGY_UV.md)

**Breaking Changes:**
- None! Fully backward compatible. `requirements.txt` still works.

**Migration Guide:**
See [MIGRATION_NOTES.md](./MIGRATION_NOTES.md) for:
- How to migrate existing environments
- Troubleshooting common issues
- FAQ for developers

**Defense Layer Updates:**
- Layer 1 (Devcontainer): Uses `uv sync --all-extras`
- Layer 2 (vibe-cli): Updated from pip auto-install to UV environment check
- Layer 3 (setup.sh): Uses `uv sync --all-extras`
- Layer 4 (CI): Uses `uv sync --frozen` with caching

See [DEFENSE_STRATEGY_UV.md](./DEFENSE_STRATEGY_UV.md) for complete defense strategy.

**Documentation:**
- [FOUNDATION_ASSESSMENT.md](./FOUNDATION_ASSESSMENT.md) - Pre-migration analysis
- [FOUNDATION_MIGRATION_PLAN.md](./FOUNDATION_MIGRATION_PLAN.md) - Migration plan
- [MIGRATION_NOTES.md](./MIGRATION_NOTES.md) - User guide & troubleshooting
- [DEFENSE_VALIDATION_REPORT.md](./DEFENSE_VALIDATION_REPORT.md) - Layer validation
- [DEFENSE_STRATEGY_UV.md](./DEFENSE_STRATEGY_UV.md) - Defense strategy guide

**Session:** claude/foundation-hardening-uv-migration-01UniXx3ZaAgpePBtgYHebZF

---

### Added - 2025-11-14

- **Delegated Execution Architecture (ADR-003)** - Brain-Arm separation for orchestrator
  - New `execution_mode` parameter in `core_orchestrator.py` (`delegated` | `autonomous`)
  - STDOUT/STDIN handoff protocol for Claude Code integration
  - `vibe-cli` wrapper tool for managing orchestrator subprocess
  - Full documentation in `docs/architecture/ADR-003_Delegated_Execution_Architecture.md`
  - User guide in `docs/guides/DELEGATED_EXECUTION_GUIDE.md`

### Fixed - 2025-11-14

- **CRITICAL REGRESSION FIX**: Orchestrator no longer makes direct LLM calls
  - **Problem**: `core_orchestrator.py` was calling `llm_client.invoke()` directly
  - **Impact**: Violated Brain-Arm architecture principle, bypassed Claude Code operator
  - **Root Cause**: GAD-002 implementation introduced autonomous execution without handoff mechanism
  - **Solution**: Refactored `execute_agent()` to delegate intelligence operations via STDOUT/STDIN
  - **Related**: ADR-003, GAD-002 Decision 6 (Agent Invocation Architecture)

### Changed - 2025-11-14

- `core_orchestrator.py` CLI now uses argparse for better UX
- Default execution mode is now `delegated` (was implicit `autonomous`)
- `llm_client` initialization only happens in `autonomous` mode (optimization)

---

## [1.2.0] - 2025-11-14 (Prior to Regression Fix)

### Added

- Core SDLC Orchestration (GAD-002)
  - Hierarchical orchestrator architecture
  - Phase-specific handlers (planning, coding, testing, deployment, maintenance)
  - Schema validation via `SchemaValidator`
  - Horizontal audits (per-phase continuous auditing)
  - Budget tracking and cost management

- Research Integration (GAD-001)
  - RESEARCH phase with fact validation
  - MARKET_RESEARCHER, TECH_RESEARCHER, USER_RESEARCHER agents
  - FACT_VALIDATOR quality gate

### Known Issues

- ⚠️ **Regression**: Orchestrator makes direct LLM calls (fixed in ADR-003)
- ⚠️ **Architectural violation**: Brain-Arm separation not enforced (fixed in ADR-003)

---

## [1.1.0] - 2025-11-13 (Estimated)

### Added

- VIBE_ALIGNER v3.0 - Intelligent Project Scope Orchestrator
- GENESIS_BLUEPRINT v5.0 - Technical Architecture Generator
- Feasibility Analysis Engine (FAE)
- Feature Dependency Graph (FDG)
- Adaptive Prioritization & Complexity Engine (APCE)

### Documentation

- QUICK_START_SESSION.md
- RELEASE_NOTES_v1.1.md
- Multiple ADRs and GADs

---

## [1.0.0] - 2025-11-01 (Estimated - Initial Release)

### Added

- Initial prompt composition system
- 6,400+ lines of curated domain knowledge
- Modular prompt templates
- File-based architecture (no databases)

---

## Migration Notes

### Upgrading to ADR-003 (Delegated Execution)

**Breaking Change**: Default execution mode is now `delegated`.

If you were using `core_orchestrator.py` directly:

```bash
# Old way (still works with --mode=autonomous)
python core_orchestrator.py /repo/root project-123

# New way (default)
./vibe-cli run project-123

# Legacy mode (for testing)
python core_orchestrator.py /repo/root project-123 --mode=autonomous
```

**No migration needed** if you use `vibe-cli`.

---

## Regression Log

### 2025-11-14: Orchestrator Direct LLM Call Regression

**Detected**: During architecture review with user
**Severity**: High (architectural violation)
**Affected Component**: `core_orchestrator.py` lines 436-507
**Fixed In**: ADR-003 implementation

**Timeline**:
- **Introduced**: GAD-002 implementation (unknown date, likely 2025-11-13)
- **Detected**: 2025-11-14 during user session
- **Fixed**: 2025-11-14 (commit a966752)

**Description**:
The orchestrator (`core_orchestrator.py`) was making direct LLM calls via `llm_client.invoke()`,
bypassing the intended Brain-Arm separation. This violated the core architectural principle
that the orchestrator should only compose prompts and manage state, while intelligence
operations should be delegated to Claude Code (the "Brain").

**Impact**:
- Claude Code operator had no visibility into workflow
- Workflow ran autonomously without human oversight
- State management mixed with intelligence execution
- Difficult to debug and audit

**Fix**:
Implemented delegated execution architecture with STDOUT/STDIN handoff protocol.
See `docs/architecture/ADR-003_Delegated_Execution_Architecture.md` for details.

---

## Deprecation Notices

### Deprecated in ADR-003

- Direct usage of `core_orchestrator.py` without `--mode` flag (use `vibe-cli` instead)
- Implicit `autonomous` mode (now requires explicit `--mode=autonomous`)

**Timeline**:
- Deprecated: 2025-11-14
- Removal: TBD (likely v2.0.0)

---

## Version History

| Version | Date       | Description                        |
|---------|------------|------------------------------------|
| 1.0.0   | 2025-11-01 | Initial release                    |
| 1.1.0   | 2025-11-13 | VIBE_ALIGNER + GENESIS_BLUEPRINT   |
| 1.2.0   | 2025-11-14 | Core SDLC Orchestration (GAD-002)  |
| 1.2.1   | 2025-11-14 | **Regression fix** (ADR-003)       |

---

## Links

- [Architecture Decisions](/docs/architecture/)
- [Release Notes (v1.1)](/RELEASE_NOTES_v1.1.md)
- [Release Notes (v1.2)](/RELEASE_NOTES_v1.2.md)
- [Contributing Guide](/CONTRIBUTING.md)
- [Documentation](/docs/)
