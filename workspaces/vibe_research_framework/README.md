# 🔬 VIBE RESEARCH FRAMEWORK

**Version:** 1.0.0
**Status:** Planning Complete ✅
**Timeline:** 12-13 weeks
**Complexity Budget:** 37/60 points (61% utilization)

---

## 📖 Overview

The **VIBE RESEARCH FRAMEWORK** is an integration-ready extension to the VIBE AGENCY planning workflow. It adds a new **RESEARCH** sub-state that provides fact-based validation **before** business planning begins.

### The Problem
Currently, users jump from idea → Lean Canvas without verifying:
- Market assumptions (competitors, pricing, market size)
- Technical feasibility (API limits, library maintenance, stack constraints)
- User insights (personas, pain points, interview questions)

This leads to **hallucinated assumptions** and failed pivots.

### The Solution
Add an **optional** RESEARCH phase with 4 specialized agents that generate a citation-backed `research_brief.json` artifact.

---

## 🏗️ Architecture

```
PLANNING (Phase)
│
├── RESEARCH (NEW - Optional)
│   ├── MARKET_RESEARCHER (Competitor analysis, pricing, market sizing)
│   ├── TECH_RESEARCHER (API evaluation, library comparison, FAE validation)
│   ├── FACT_VALIDATOR (Hallucination detection, citation enforcement)
│   └── USER_RESEARCHER (Persona generation, interview scripts)
│   │
│   └─→ research_brief.json
│
├── BUSINESS_VALIDATION (Updated to accept research_brief.json)
│   └── LEAN_CANVAS_VALIDATOR
│   └─→ lean_canvas_summary.json
│
└── FEATURE_SPECIFICATION
    └── VIBE_ALIGNER
    └─→ feature_spec.json
```

---

## ✨ Key Features

### 1. MARKET_RESEARCHER Agent
- **Competitor identification** (with sources)
- **Pricing analysis** (verifiable pricing data)
- **Market size estimation** (TAM/SAM/SOM with formulas)
- **Positioning opportunities** (differentiation analysis)
- **Risk identification** (market saturation, timing risks)

### 2. TECH_RESEARCHER Agent
- **API evaluation** (rate limits, pricing, reliability via docs)
- **Library comparison** (GitHub stars, maintenance status, license)
- **Stack recommendation** (based on project type)
- **Technical constraint identification** (FAE-style validation)
- **Feasibility scoring** (high/medium/low with explanations)

### 3. FACT_VALIDATOR Agent
- **Knowledge base audit** (like the audit document)
- **Claim verification** (all claims need sources)
- **Red flag detection** (context-collapse, plausible falsehoods, platitudes)
- **Citation enforcement** (blocks output if critical claims lack sources)
- **Quality scoring** (X/100 with issue breakdown)

### 4. USER_RESEARCHER Agent
- **Persona generation** (industry-standard templates)
- **Pain point identification** (extracted from vision)
- **Interview script creation** (actionable questions)
- **Survey design** (survey template generation)
- **User journey mapping** (5-stage template)

---

## 📊 Validation Results

### FAE (Feasibility Analysis Engine)
✅ **PASSED** - No FAE violations detected
⚠️ FACT_VALIDATOR flagged for review (high complexity but justified)

### FDG (Feature Dependency Graph)
✅ **PASSED** - No missing dependencies
✅ No circular dependencies

### APCE (Complexity & Prioritization Engine)
✅ **PASSED** - 37/60 complexity budget (61% utilization)
✅ Must Have: 32 points (87% of scope)
✅ Should Have: 5 points (13% of scope)

---

## 🎯 Deliverables

| Artifact | Location | Status |
|----------|----------|--------|
| Feature Specifications | `artifacts/planning/VIBE_RESEARCH_FRAMEWORK_SPECS.md` | ✅ Complete |
| Technical Blueprint | `artifacts/planning/TECHNICAL_BLUEPRINT.md` | ✅ Complete |
| Project Manifest | `project_manifest.json` | ✅ Complete |
| Implementation Roadmap | See Technical Blueprint | ✅ 7 sprints defined |

---

## 🚀 Implementation Roadmap

### Sprint 1-2: Foundation (Weeks 1-2)
- Directory structure + data contracts
- State machine integration
- Knowledge base YAML files

### Sprint 3-4: MARKET_RESEARCHER (Weeks 3-4)
- 6 tasks + 3 gates
- Competitor analysis templates

### Sprint 5-6: TECH_RESEARCHER (Weeks 5-6)
- 6 tasks + 3 gates
- FAE integration

### Sprint 7-9: FACT_VALIDATOR (Weeks 7-9)
- 6 tasks + 3 gates
- Red flag taxonomy

### Sprint 10-11: USER_RESEARCHER (Weeks 10-11)
- 6 tasks + 2 gates
- Persona templates

### Sprint 12: Integration (Week 12)
- LEAN_CANVAS_VALIDATOR updates
- Backward compatibility testing

### Sprint 13: Testing & Docs (Week 13)
- Full test suite
- User + developer documentation

---

## ⚠️ Critical Success Factors

1. **Citation Enforcement** - FACT_VALIDATOR blocks output if critical claims lack sources
2. **Backward Compatibility** - LEAN_CANVAS_VALIDATOR works with AND without research
3. **Optionality** - Users can skip RESEARCH phase
4. **Zero Breaking Changes** - Existing workflows unchanged
5. **FAE Integration** - TECH_RESEARCHER references existing FAE rules

---

## 📋 Next Steps

1. ✅ Review feature specs + blueprint
2. ⏳ Confirm 12-13 week timeline with team
3. ⏳ Begin Sprint 1 (foundation + data contracts)
4. ⏳ Set up agent composition test environment

---

## 📚 Documentation

- **Feature Specs:** [VIBE_RESEARCH_FRAMEWORK_SPECS.md](artifacts/planning/VIBE_RESEARCH_FRAMEWORK_SPECS.md)
- **Technical Blueprint:** [TECHNICAL_BLUEPRINT.md](artifacts/planning/TECHNICAL_BLUEPRINT.md)
- **Project Manifest:** [project_manifest.json](project_manifest.json)

---

**Framework Execution:** VIBE_ALIGNER v3.0
**Generated:** 2025-11-14
**Status:** ✅ Ready for Implementation
