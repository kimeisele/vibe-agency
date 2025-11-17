# Architecture Index

📖 **New here?** Read [STRUCTURE.md](STRUCTURE.md) first to understand the 3-document-type system (GAD/LAD/VAD).

---

## The 8 Pillars (GAD)

### GAD-1XX: [Pillar 1 - TBD]
- [GAD-100: Main Document](GAD-1XX/GAD-100.md) ⚠️ TODO: Migrate from GAD-001

### GAD-2XX: [Pillar 2 - TBD]
- [GAD-200: Main Document](GAD-2XX/GAD-200.md) ⚠️ TODO: Migrate from GAD-002

### GAD-3XX: [Pillar 3 - TBD]
- [GAD-300: Main Document](GAD-3XX/GAD-300.md) ⚠️ TODO: Migrate from GAD-003

### GAD-4XX: [Pillar 4 - TBD]
- [GAD-400: Main Document](GAD-4XX/GAD-400.md) ⚠️ TODO: Migrate from GAD-004

### GAD-5XX: Runtime Engineering ✅
- [GAD-500: Runtime Engineering EPIC](GAD-5XX/GAD-500.md)
- [GAD-501: Layer 0 and Layer 1](GAD-5XX/GAD-501.md)
- [GAD-502: Haiku Hardening](GAD-5XX/GAD-502.md)

### GAD-6XX: Knowledge Department ✅
- [GAD-600: Knowledge Department EPIC](GAD-6XX/GAD-600.md)

### GAD-7XX: STEWARD Governance ✅
- [GAD-700: STEWARD Governance EPIC](GAD-7XX/GAD-700.md)

### GAD-8XX: Integration Matrix ✅
- [GAD-800: Integration Matrix EPIC](GAD-8XX/GAD-800.md)

---

## Layers (LAD) ✅

The Layer Architecture Documents provide horizontal views across all pillars:

- **[LAD-1](LAD/LAD-1.md)**: Browser Layer (prompt-only, $0 cost)
- **[LAD-2](LAD/LAD-2.md)**: Claude Code Layer (tool-based, $20/mo)
- **[LAD-3](LAD/LAD-3.md)**: Runtime Layer (API-based, $50-200/mo)

---

## Verification (VAD) - Coming in PR 3

The Verification Architecture Documents test cross-pillar integration:

- **VAD-001**: Core Workflow Verification - Coming Soon
- **VAD-002**: Knowledge Integration - Coming Soon
- **VAD-003**: Layer Degradation - Coming Soon

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

### Legacy GAD Files (Pre-Migration)
These files remain at the root level pending further review and consolidation:

- GAD-001_Research_Integration.md
- GAD-001_VERIFICATION_HARNESS.md
- GAD-002_Core_SDLC_Orchestration.md
- GAD-002_VERIFICATION_HARNESS.md
- GAD-003_Research_Capability_Restoration.md
- GAD-003_COMPLETION_ASSESSMENT.md
- GAD-003_IMPLEMENTATION_STATUS.md
- GAD-004_Multi_Layered_Quality_Enforcement.md

---

## Navigation Tips

1. **Start with STRUCTURE.md** to understand the 3-tier system
2. **Use ARCHITECTURE_MAP.md** for the big picture
3. **Browse by pillar** (GAD-XXX) for vertical slices
4. **Browse by layer** (LAD-X) for horizontal views ✅
5. **Check VAD** for integration tests (coming in PR 3)

---

**Last Updated**: 2025-11-17  
**Version**: 2.0 (Week 2 PR 2 - LAD Documents Complete)
