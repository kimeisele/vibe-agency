# Architectural Registry (formerly GAD Status)

**Last Updated:** 2025-11-20
**Purpose:** Central registry tracking the status of Architectural Decisions (ADR), Deployment Layers (LAD), and Vertical Features (VAD).

---

## 1. Architectural Decisions (ADR)
*Structural choices, constraints, and cross-cutting concerns.*

### ADR-001: Canonical Schema Definition (formerly GAD-100)
**Status:** 🔄 PARTIAL (Phases 1-2 Complete)
**Description:** Centralized configuration management using Phoenix Config and JSON schemas.
**Implementation:** `lib/phoenix_config/`, `config/schemas/`

### ADR-002: Multi-Layered Quality Enforcement (formerly GAD-400)
**Status:** ✅ COMPLETE
**Description:** 3-Layer quality model (Session, Workflow, Deployment).
**Implementation:** `bin/pre-push-check.sh`, `.system_status.json`, CI/CD

### ADR-003: Delegated Execution (formerly GAD-511)
**Status:** 🟡 IMPLEMENTED (Smoke tests passed, full coverage pending)
**Description:** Multi-provider LLM support with delegated execution model.
**Implementation:** `agency_os/core_system/runtime/providers/`
**Notes:** Smoke tests added 2025-11-20. Full integration tests pending.

### ADR-004: System Integrity (formerly GAD-501 Layer 0)
**Status:** ✅ COMPLETE
**Description:** File integrity verification and drift detection.
**Implementation:** `scripts/verify-system-integrity.py`, `.vibe/`

### ADR-005: Integration Matrix (formerly GAD-800/801)
**Status:** ✅ COMPLETE
**Description:** Component compatibility and core orchestration.
**Implementation:** `agency_os/core_system/orchestrator/`

---

## 2. Deployment Layers (LAD)
*Environmental and operational contexts.*

### LAD-1: Session Shell (formerly GAD-501 Layer 1)
**Status:** ✅ COMPLETE
**Description:** Interactive CLI session with MOTD and health checks.
**Implementation:** `vibe-cli` (MOTD)

### LAD-2: Ambient Context (formerly GAD-501 Layer 2)
**Status:** 📋 PLANNED
**Description:** Artifact persistence and receipt system.

### LAD-3: Commit Watermarking (formerly GAD-501 Layer 3)
**Status:** 📋 PLANNED
**Description:** Local enforcement and git hooks.

### LAD-4: Remote Validation (formerly GAD-501 Layer 4)
**Status:** ✅ COMPLETE
**Description:** CI/CD gates and remote testing.

---

## 3. Features (VAD - Vertical Architecture Decisions)
*Functional capabilities and specific workflows.*

### VAD-101: Planning Handlers (formerly GAD-101)
**Status:** ✅ COMPLETE
**Description:** Vibe Aligner, Lean Canvas, Genesis Blueprint.

### VAD-102: Research Capability (formerly GAD-102)
**Status:** ✅ COMPLETE
**Description:** Market, Tech, User researchers.

### VAD-103: Knowledge Bases (formerly GAD-103)
**Status:** ✅ COMPLETE
**Description:** FAE, FDG, APCE rules.

### VAD-200: Code Generation (formerly GAD-200)
**Status:** ✅ COMPLETE
**Description:** 5-phase coding workflow.

### VAD-502: Context Projection (formerly GAD-502)
**Status:** 🟡 IMPLEMENTED (Integration verification needed)
**Description:** Runtime context injection into prompts.

### VAD-509: Iron Dome (formerly GAD-509)
**Status:** 🟡 IMPLEMENTED (Integration verification needed)
**Description:** Circuit breaker for LLM APIs.

### VAD-503: Haiku Hardening (formerly GAD-503)
**Status:** 📋 PLANNED
**Description:** Validation using lower-tier models.

### VAD-600: Knowledge Services (formerly GAD-600)
**Status:** 📋 PLANNED
**Description:** Semantic graph and domain knowledge.

### VAD-700: Governance (formerly GAD-700)
**Status:** 📋 PLANNED
**Description:** Hybrid governance framework.

---

## Summary Statistics

**Total Items:** 18
**Complete:** 10 (55%)
**Partial/Implemented:** 3 (17%)
**Planned:** 5 (28%)

**Critical Actions Taken (2025-11-20):**
- **Rescue Phase 1:** Fixed boot script, disabled live fire in CI.
- **Rescue Phase 2:** Refactored `sys.path` hacks, enforced ADR-003, added smoke tests.
- **Rescue Phase 3:** Simplified taxonomy (this document).

---

## Legend
- **ADR:** Architectural Decision Record (Structural)
- **LAD:** Layered Architecture Decision (Deployment)
- **VAD:** Vertical Architecture Decision (Feature)
