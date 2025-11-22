# Changelog

All notable changes to Vibe Agency OS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-citizen] - 2025-11-22

### Added
- **ARCH-042: The Senses** - `ListDirectoryTool` and `SearchFileTool` for autonomous filesystem navigation
  - Workspace-confined security (prevents access outside project root)
  - Integrated with Soul Governance (InvariantChecker)
  - 11 automated tests covering functionality and security boundaries
- **GAD-100: Operation Phoenix** - System resilience and graceful degradation
  - `VibeLedger` now falls back to `:memory:` mode if file-based SQLite fails
  - Added `pydantic-settings` and `pyyaml` dependencies for configuration integrity
  - 3 resilience tests covering normal boot, degraded boot, and functionality verification
- **ARCH-043: The Self-Diagnosis** - Autonomous debugging capability
  - Used Senses tools to diagnose and fix missing `project_manifest.json` in artifact loading
  - Added `project_manifest.json` to `artifact_paths` in `core_orchestrator.py`
  - Demonstrates end-to-end autonomous repair loop

### Fixed
- Core system stability: 111/111 core tests passing
- `AgentResponse` object access in tests (attribute vs. dictionary access)
- Kernel validation logic alignment across all test suites
- Circular import issues in `vibe_core.llm` module
- Missing `capabilities` property in mock agents
- `project_manifest.json` loading in `DeploymentSpecialist` precondition checks

### Changed
- Test configuration: Force `:memory:` mode for ledger to prevent DB lock issues during parallel execution
- Merge consolidation: All feature branches (Phoenix, Senses, Self-Diagnosis) merged into `main`

### Infrastructure
- Created `PHOENIX_REPORT.md` documenting system resilience improvements
- Updated `walkthrough.md` with ARCH-042, GAD-100, and ARCH-043 details
- Branch strategy: `feature/steward-alignment`, `feature/gad-100-phoenix`, `feature/arch-042-senses`, `feature/arch-043-self-diagnosis`

---

## [0.9.0] - Previous releases
(Historical changelog entries would go here)
