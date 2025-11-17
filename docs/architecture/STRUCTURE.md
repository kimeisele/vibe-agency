# Architecture Documentation Structure

**Last Updated**: 2025-11-17  
**Status**: Active

---

## Overview

This directory contains all architecture documentation for Vibe Agency, organized into 3 document types across 3 dimensions:

```
DIMENSION 1: PILLARS (Vertical - 8 architectural pillars)
DIMENSION 2: LAYERS (Horizontal - 3 deployment layers)
DIMENSION 3: VERIFICATION (Cross-cutting - integration tests)
```

---

## The 3 Document Types

### 1. GAD (Guidance Architecture Documents)

**Purpose**: The 8 architectural pillars  
**Scope**: One pillar across all layers  
**Structure**: `GAD-XYZ` (X=Pillar number, YZ=Sub-document number)

**Example**:
```
GAD-5XX/
├─ GAD-500.md  # Runtime Engineering EPIC
├─ GAD-501.md  # Runtime Layer 0 and Layer 1
└─ GAD-502.md  # Runtime Haiku Hardening
```

**The 8 Pillars**:
- GAD-1XX: [Pillar 1 - TBD]
- GAD-2XX: [Pillar 2 - TBD]
- GAD-3XX: [Pillar 3 - TBD]
- GAD-4XX: [Pillar 4 - TBD]
- GAD-5XX: Runtime Engineering
- GAD-6XX: Knowledge Department
- GAD-7XX: STEWARD Governance
- GAD-8XX: Integration Matrix

---

### 2. LAD (Layer Architecture Documents)

**Purpose**: Layer-specific overview  
**Scope**: All pillars within one layer  
**Structure**: `LAD-X.md` (X=Layer number)

**Example**:
```
LAD/
├─ LAD-1.md  # Browser Layer (what works in browser-only mode?)
├─ LAD-2.md  # Claude Code Layer (what tools are available?)
└─ LAD-3.md  # Runtime Layer (what services are running?)
```

**The 3 Layers**:
- Layer 1: Browser (Prompt-only, $0 cost)
- Layer 2: Claude Code (Tool-based, $20/mo)
- Layer 3: Runtime (API-based, $50-200/mo)

**Status**: ✅ Complete (See LAD/ directory)

---

### 3. VAD (Verification Architecture Documents)

**Purpose**: Cross-pillar integration tests  
**Scope**: Tests that multiple GADs work together  
**Structure**: `VAD-XXX_Name.md`

**Example**:
```
VAD/
├─ VAD-001_Core_Workflow.md
├─ VAD-002_Knowledge_Integration.md
└─ VAD-003_Layer_Degradation.md
```

**Purpose**: The "security matrix" between pillars - verifies that different architectural components integrate correctly.

**Status**: ✅ Complete (See VAD/ directory)

---

## Numbering Convention

### GAD Numbers (3-digit)

```
GAD-XYZ:
  X = Pillar (1-8)
  YZ = Sub-document (00-99)

Examples:
  GAD-100: Pillar 1 main document (EPIC)
  GAD-101: Pillar 1 sub-document 1
  GAD-500: Runtime Engineering EPIC
  GAD-501: Runtime Layer 0 details
```

**Rationale**: 
- First digit identifies pillar
- 99 sub-documents per pillar = scalable
- Automatic sorting works correctly

---

### LAD Numbers (single-digit)

```
LAD-X:
  X = Layer (1-3)

Examples:
  LAD-1: Browser Layer
  LAD-2: Claude Code Layer
  LAD-3: Runtime Layer
```

**Rationale**: Only 3 layers, no need for more digits.

---

### VAD Numbers (3-digit)

```
VAD-XXX:
  XXX = Sequential (001-999)

Examples:
  VAD-001: First verification test
  VAD-002: Second verification test
```

**Rationale**: Sequential numbering, no hierarchy needed.

---

## Directory Structure

```
docs/architecture/
│
├─ GAD-1XX/              # Pillar 1 family
│  └─ GAD-100.md         # Main document
│
├─ GAD-2XX/              # Pillar 2 family
│  └─ GAD-200.md
│
├─ GAD-3XX/              # Pillar 3 family
│  └─ GAD-300.md
│
├─ GAD-4XX/              # Pillar 4 family
│  └─ GAD-400.md
│
├─ GAD-5XX/              # Runtime Engineering
│  ├─ GAD-500.md         # EPIC
│  ├─ GAD-501.md         # Layer 0 and Layer 1
│  └─ GAD-502.md         # Haiku Hardening
│
├─ GAD-6XX/              # Knowledge Department
│  └─ GAD-600.md         # EPIC
│
├─ GAD-7XX/              # STEWARD Governance
│  └─ GAD-700.md         # EPIC
│
├─ GAD-8XX/              # Integration Matrix
│  └─ GAD-800.md         # EPIC
│
├─ LAD/                  # Layer overviews (horizontal views)
│  ├─ LAD-1.md           # Browser Layer
│  ├─ LAD-2.md           # Claude Code Layer
│  └─ LAD-3.md           # Runtime Layer
│
├─ VAD/                  # Verification tests (cross-pillar integration)
│  ├─ VAD-001_Core_Workflow.md
│  ├─ VAD-002_Knowledge_Integration.md
│  └─ VAD-003_Layer_Degradation.md
│
├─ ARCHITECTURE_MAP.md   # Big picture overview
├─ INDEX.md              # Navigation index
└─ STRUCTURE.md          # This file (explains the system)
```

---

## When to Create Each Document Type

### Create a GAD when:
- Defining a new architectural pillar
- Adding sub-documents to existing pillar (layer-specific details, additions)

### Create a LAD when:
- Documenting what works in a specific layer
- Need horizontal view across all pillars

### Create a VAD when:
- Testing integration between 2+ pillars
- Verifying cross-cutting concerns
- Implementing "security matrix" tests

---

## Navigation

**Start here**: [INDEX.md](INDEX.md)  
**Big picture**: [ARCHITECTURE_MAP.md](ARCHITECTURE_MAP.md)  
**Understand layers**: [LAD/](LAD/)  
**Browse pillars**: [GAD-5XX/](GAD-5XX/), [GAD-6XX/](GAD-6XX/), etc.  
**Check integration**: [VAD/](VAD/)

---

## Maintenance

### Adding a new GAD sub-document:
1. Determine pillar number (1-8)
2. Find next available number in that family (e.g., GAD-503)
3. Create file in appropriate directory
4. Update INDEX.md

### Adding a new VAD:
1. Find next sequential number (e.g., VAD-004)
2. Create file in VAD/ directory
3. Create test skeleton in tests/architecture/
4. Update INDEX.md

---

## Migration History

**2025-11-17 (Week 1 PR 1)**: Initial structure established
- Created 8 pillar directories (GAD-1XX through GAD-8XX)
- Created LAD/ and VAD/ directories (placeholders)
- Migrated GAD-005 → GAD-500, GAD-501, GAD-502
- Migrated GAD-006 → GAD-600
- Migrated GAD-007 → GAD-700
- Migrated GAD-008 → GAD-800
- Created placeholders for GAD-1XX through GAD-4XX
- Established 3-document-type system
- Created INDEX.md and STRUCTURE.md

**2025-11-17 (Final PR - Weeks 2 & 3 Combined)**: LAD and VAD implementation
- ✅ Created LAD-1.md (Browser Layer)
- ✅ Created LAD-2.md (Claude Code Layer)
- ✅ Created LAD-3.md (Runtime Layer)
- ✅ Created VAD-001_Core_Workflow.md
- ✅ Created VAD-002_Knowledge_Integration.md
- ✅ Created VAD-003_Layer_Degradation.md
- ✅ Created test skeletons in tests/architecture/
- ✅ Updated INDEX.md to reflect completion
- ✅ Updated STRUCTURE.md to reflect completion

**Pending migrations**:
- GAD-001 files (Research Integration) → Determine target pillar
- GAD-002 files (Core SDLC) → Determine target pillar
- GAD-003 files (Research Capability) → Determine target pillar
- GAD-004 files (Quality Enforcement) → Determine target pillar

---

## Principles

1. **Separation of Concerns**: GAD (vertical), LAD (horizontal), VAD (cross-cutting)
2. **Scalability**: 3-digit numbering allows 99 sub-docs per pillar
3. **Self-Organizing**: Clear folder structure per pillar
4. **Git-Friendly**: `git mv` preserves history during migration
5. **Graceful Degradation**: Every layer documented separately (LAD)

---

## Why 3 Document Types?

### GAD alone is NOT enough

**Scenario 1**: Developer asks "What can I do in Layer 2?"
```
Without LAD: Read GAD-501, 601, 701, 801 (4 docs, tedious)
With LAD: Read LAD-2 (1 doc, overview)
```

**Scenario 2**: Architect asks "Do Runtime + STEWARD work together?"
```
Without VAD: Hidden somewhere in GAD-500 or GAD-700
With VAD: VAD-003 explicitly tests this integration
```

**Scenario 3**: Tester asks "How do I test Graceful Degradation?"
```
Without VAD: No idea where that's documented
With VAD: VAD-003_Layer_Degradation.md
```

The 3-document-type system covers all 3 dimensions of the architecture:
- **GAD** = Pillars (vertical through layers)
- **LAD** = Layers (horizontal across pillars)
- **VAD** = Verification (security net between pillars)

---

**END OF STRUCTURE.md**
