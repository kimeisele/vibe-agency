# Architecture Quarantine

**Status:** Active cleanup operation (PHASE_0: Quarantine & Triage)
**Created:** 2025-11-20
**Context:** Foundation cleanup roadmap (Task Q001)

## Purpose

This directory contains GAD (Generalized Architecture Decision) documents that have been quarantined during the foundation cleanup operation. These files are NOT part of the core architectural decisions.

## Why Quarantine?

During the November 2025 reality-check audit, we discovered **GAD status inflation**: 40+ documents claimed to be "architecture decisions" but many were actually:
- Feature specifications (not architectural patterns)
- Unclear or incomplete proposals
- Duplicates or abandoned experiments

The cleanup roadmap systematically separates:
- **Good Architecture** (8 ADRs + 4 VADs + 3 LADs = 15 decisions) → Stays in `/docs/architecture/`
- **Features masquerading as architecture** → `quarantine/features/`
- **Unclear/incomplete proposals** → `quarantine/unknown/`

## Directory Structure

### `/features/` - Feature Specifications (Not Architecture)

These GADs describe **features**, not architectural patterns:

- **GAD-100** series: SDLC phase scaffolding (features, not architecture)
- **GAD-200**: Prompt routing system (feature)
- **GAD-300**: Agent delegation protocol (feature, violates ADR-003)

**Why quarantined:** Architecture describes HOW the system works (patterns, principles, constraints). Features describe WHAT the system does (capabilities, workflows). These belong in `/docs/features/` or project specs, not architecture registry.

### `/unknown/` - Unclear or Incomplete

GADs that were referenced but don't exist, or are incomplete:
- GAD-105, 201-204, 301-304: Not found (may have been planned but never implemented)
- GAD-503-504: Unclear status
- GAD-601-602, 701-702: Potentially valid but need verification
- GAD-901-909: Not found

**Why quarantined:** Cannot verify implementation status, purpose, or integration. Need investigation before declaring as architecture.

## What Remains in `/docs/architecture/`

**Core Architecture (verified and integrated):**

### ADRs (Architectural Decision Records)
- ADR-003: Delegation-first orchestration
- GAD-500: Week 1 baseline (Layer 0-1)
- GAD-501: Layer 0-1 implementation
- GAD-502: Context injection protocol
- GAD-509: Circuit breaker pattern
- GAD-510: Provider abstraction
- GAD-800: SDLC upgrade summary
- GAD-801: Test-first enforcement

### VADs (Verification Architecture Decisions)
- VAD-001, 002, 003, 004: Quality enforcement layers

### LADs (Layered Architecture Decisions)
- LAD-1, 2, 3: Deployment mode separation

**Total:** 15 architectural decisions (not 40+)

## Next Steps (Cleanup Roadmap)

1. **Q002**: Create clean ARCHITECTURE_REGISTRY.md with only verified ADRs/VADs/LADs
2. **Q003**: Document implementation status for each
3. **Q004**: Update GAD_IMPLEMENTATION_STATUS.md with honest metrics
4. **B001-B004**: Stop bleeding (fix boot, disable CI costs, freeze features)
5. **F001-F004**: Clean foundation (fix imports, enforce ADR-003, add tests)
6. **V001-V004**: Verify and document completion

## Decision Criteria

**Architecture belongs in `/docs/architecture/` if:**
- ✅ Describes a pattern, principle, or constraint
- ✅ Has implementation code that can be verified
- ✅ Integrated into core orchestration flow
- ✅ Has tests proving it works

**Otherwise → Quarantine**

## References

- **Cleanup Roadmap**: `.vibe/config/cleanup_roadmap.json`
- **Reality Check Audit**: `GAP_ANALYSIS_REALITY_CHECK_2025-11-20.md`
- **Critical Analysis**: `CRITICAL_ANALYSIS_2025-11-19.md`
- **Self-Heal Guide**: `HOW_TO_SELF_HEAL.md`
