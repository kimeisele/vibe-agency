# Architecture Index

📖 **New here?** Read [STRUCTURE.md](STRUCTURE.md) first to understand the 3-document-type system (GAD/LAD/VAD).

---

## The 8 Pillars (GAD)

### GAD-1XX: Planning & Research ✅
- [GAD-100: Planning & Research EPIC](GAD-1XX/GAD-100.md) (Migrated from GAD-001 + GAD-003)
- [GAD-101: Research Tool Integration](GAD-1XX/GAD-101.md) ⚠️ Planned

### GAD-2XX: Core Orchestration & Workflow ✅
- [GAD-200: Core Orchestration EPIC](GAD-2XX/GAD-200.md) (Migrated from GAD-002)
- [GAD-201: Testing Handler](GAD-2XX/GAD-201.md) ⚠️ Planned
- [GAD-202: Maintenance Handler](GAD-2XX/GAD-202.md) ⚠️ Planned

### GAD-3XX: Agent Framework & Runtime ✅
- [GAD-300: Agent Framework EPIC](GAD-3XX/GAD-300.md) (New pillar)
- [GAD-301: Prompt Composition System](GAD-3XX/GAD-301.md) ⚠️ Planned
- [GAD-302: Agent Lifecycle Management](GAD-3XX/GAD-302.md) ⚠️ Planned

### GAD-4XX: Quality & Testing ✅
- [GAD-400: Quality & Testing EPIC](GAD-4XX/GAD-400.md) (Migrated from GAD-004)

### GAD-5XX: Runtime Engineering ✅
- [GAD-500: Runtime Engineering EPIC](GAD-5XX/GAD-500.md)
- [GAD-501: Layer 0 and Layer 1](GAD-5XX/GAD-501.md)
- [GAD-502: Haiku Hardening](GAD-5XX/GAD-502.md)
- [GAD-509: Circuit Breaker Protocol (Iron Dome)](GAD-5XX/GAD-509.md) ✅
- [GAD-510: Quota Manager (Cost Control)](GAD-5XX/GAD-510.md) ✅
- [GAD-511: Neural Adapter Strategy (Multi-Provider LLM)](GAD-5XX/GAD-511.md) ✅

### GAD-6XX: Knowledge Department ✅
- [GAD-600: Knowledge Department EPIC](GAD-6XX/GAD-600.md)

### GAD-7XX: STEWARD Governance ✅
- [GAD-700: STEWARD Governance EPIC](GAD-7XX/GAD-700.md)

### GAD-8XX: Integration Matrix ✅
- [GAD-800: Integration Matrix EPIC](GAD-8XX/GAD-800.md)

---

## Layers (LAD) ✅

The Layer Architecture Documents provide horizontal views across all pillars:

- [**LAD-1**: Browser Layer](LAD/LAD-1.md) - Prompt-only, $0 cost
- [**LAD-2**: Claude Code Layer](LAD/LAD-2.md) - Tool-based, $20/mo
- [**LAD-3**: Runtime Layer](LAD/LAD-3.md) - API-based, $50-200/mo

---

## Verification (VAD) ✅

The Verification Architecture Documents test cross-pillar integration:

- [**VAD-001**: Core Workflow Verification](VAD/VAD-001_Core_Workflow.md) - Tests SDLC + Quality + Runtime
- [**VAD-002**: Knowledge Integration](VAD/VAD-002_Knowledge_Integration.md) - Tests Knowledge + STEWARD
- [**VAD-003**: Layer Degradation](VAD/VAD-003_Layer_Degradation.md) - Tests graceful degradation

---

## Other Architecture Documents

### Foundation
- [ARCHITECTURE_MAP.md](ARCHITECTURE_MAP.md) - Big picture overview
- [STRUCTURE.md](STRUCTURE.md) - Documentation system explanation

### ADRs (Architecture Decision Records)
- [ADR-003: Delegated Execution Architecture](ADR-003_Delegated_Execution_Architecture.md)
- [ADR-003 Amendment: MVP Clarification](ADR-003_AMENDMENT_MVP_Clarification.md)

### Strategy & Analysis
- [EXECUTION_MODE_STRATEGY.md](EXECUTION_MODE_STRATEGY.md)
- [ARCHITECTURE_GAP_ANALYSIS.md](ARCHITECTURE_GAP_ANALYSIS.md)
- [CRITICAL_PATH_ANALYSIS.yaml](CRITICAL_PATH_ANALYSIS.yaml)
- [SYSTEM_DATA_FLOW_MAP.yaml](SYSTEM_DATA_FLOW_MAP.yaml)

### Legacy GAD Files (Archived)
These files have been archived after migration to new structure:

**Location:** `archive/pre-migration/`

- GAD-001_Research_Integration.md → **GAD-100** (Planning & Research)
- GAD-001_VERIFICATION_HARNESS.md → Archived
- GAD-002_Core_SDLC_Orchestration.md → **GAD-200** (Orchestration)
- GAD-002_VERIFICATION_HARNESS.md → Archived
- GAD-003_Research_Capability_Restoration.md → **GAD-100** (Part of Planning)
- GAD-003_COMPLETION_ASSESSMENT.md → Archived
- GAD-003_IMPLEMENTATION_STATUS.md → Archived
- GAD-004_Multi_Layered_Quality_Enforcement.md → **GAD-400** (Quality)

**Migration Date:** 2025-11-17

---

## Navigation Tips

1. **Start with STRUCTURE.md** to understand the 3-tier system
2. **Use ARCHITECTURE_MAP.md** for the big picture
3. **Browse by pillar** (GAD-XXX) for vertical slices
4. **Browse by layer** (LAD-X) for horizontal views across pillars
5. **Check VAD** for cross-pillar integration tests

---

**Last Updated**: 2025-11-19
**Version**: 3.1 (Infrastructure Sync - GAD-509, GAD-510, GAD-511 documented)
