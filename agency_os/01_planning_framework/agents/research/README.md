# Research Sub-Framework

**Location:** `agency_os/01_planning_framework/agents/research/`
**Status:** ✅ Integrated (Phase 1 Complete)
**Version:** 1.0
**Architecture Decision:** See `docs/architecture/GAD-001_Research_Integration.md`

---

## Purpose

The Research Sub-Framework provides **optional, fact-based research capabilities** before business planning begins. It helps validate market assumptions, technical feasibility, and user needs with citation-backed evidence.

---

## Architecture

This is a **SUB-FRAMEWORK** within the Planning Framework, NOT a separate lifecycle state.

```
01_planning_framework/
├── agents/
│   ├── research/                    ← Research Sub-Framework
│   │   ├── MARKET_RESEARCHER/       (Competitor analysis, pricing, market sizing)
│   │   ├── TECH_RESEARCHER/         (API evaluation, library comparison, feasibility)
│   │   ├── FACT_VALIDATOR/          (Citation enforcement, hallucination detection)
│   │   └── USER_RESEARCHER/         (Persona generation, interview scripts)
│   ├── LEAN_CANVAS_VALIDATOR/       ← Main Planning Agents
│   ├── VIBE_ALIGNER/
│   └── GENESIS_BLUEPRINT/
└── knowledge/
    └── research/                    ← Research Knowledge Bases
        ├── RESEARCH_market_sizing_formulas.yaml
        ├── RESEARCH_competitor_analysis_templates.yaml
        └── ...
```

---

## How It Works

### Workflow Integration

The Research phase is **OPTIONAL** and runs BEFORE business validation:

```
User Request
    ↓
[OPTIONAL] PLANNING.RESEARCH → research_brief.json
    ↓
PLANNING.BUSINESS_VALIDATION → lean_canvas_summary.json
    ↓
PLANNING.FEATURE_SPECIFICATION → feature_spec.json
    ↓
CODING...
```

### Research Type: HYBRID

Research agents are **ACTIVE** (perform web research, API calls) **AND** use **PASSIVE** knowledge bases (templates, frameworks) for structure.

Similar to how VIBE_ALIGNER uses FAE constraints:
- **Active:** Agents discover new information through research
- **Passive:** Knowledge bases provide templates, quality frameworks, validation rules

---

## The 4 Research Agents

### 1. MARKET_RESEARCHER
**Purpose:** Competitive intelligence and market validation
**Output:** market_analysis section in research_brief.json

**Tasks:**
- Task 1: Competitor Identification
- Task 2: Pricing Analysis
- Task 3: Market Size Estimation (TAM/SAM/SOM)
- Task 4: Positioning Analysis
- Task 5: Risk Identification
- Task 6: Output Generation

**Quality Gates:**
- gate_all_competitors_cited
- gate_pricing_data_verifiable
- gate_market_size_has_source

---

### 2. TECH_RESEARCHER
**Purpose:** Technical feasibility and stack evaluation
**Output:** tech_analysis section in research_brief.json

**Tasks:**
- Task 1: API Evaluation
- Task 2: Library Comparison
- Task 3: Stack Recommendation
- Task 4: Constraint Identification (FAE integration)
- Task 5: Feasibility Validation
- Task 6: Output Generation

**Quality Gates:**
- gate_all_apis_have_docs
- gate_library_maintenance_checked
- gate_fae_violations_cited

---

### 3. FACT_VALIDATOR
**Purpose:** Citation enforcement and hallucination detection
**Output:** fact_validation section in research_brief.json

**Tasks:**
- Task 1: Knowledge Base Audit
- Task 2: Claim Verification
- Task 3: Red Flag Detection
- Task 4: Citation Enforcement
- Task 5: Quality Scoring
- Task 6: Output Generation

**Quality Gates (BLOCKING):**
- gate_all_claims_verified_or_flagged
- gate_citation_index_complete
- gate_no_critical_hallucinations

**Note:** FACT_VALIDATOR can BLOCK the entire research phase if quality score < 50 or critical issues detected.

---

### 4. USER_RESEARCHER (Optional)
**Purpose:** User persona generation and interview preparation
**Output:** user_insights section in research_brief.json (optional)

**Tasks:**
- Task 1: Persona Generation
- Task 2: Pain Point Identification
- Task 3: Interview Script Creation
- Task 4: Survey Design
- Task 5: User Journey Mapping
- Task 6: Output Generation

**Quality Gates (Warning only):**
- gate_personas_industry_standard
- gate_interview_questions_actionable

---

## Knowledge Bases

Located in `01_planning_framework/knowledge/research/`:

- **RESEARCH_market_sizing_formulas.yaml** - TAM/SAM/SOM calculation methods
- **RESEARCH_competitor_analysis_templates.yaml** - Competitive analysis frameworks
- **RESEARCH_constraints.yaml** - Citation rules, quality thresholds
- **RESEARCH_persona_templates.yaml** - Industry-standard persona formats
- **RESEARCH_interview_question_bank.yaml** - Question templates
- **RESEARCH_red_flag_taxonomy.yaml** - Hallucination detection patterns

---

## Output: research_brief.json

**Schema:**
```json
{
  "market_analysis": {
    "competitors": [...],
    "pricing_insights": {...},
    "market_size": "...",
    "positioning_opportunities": [...],
    "risks": [...]
  },
  "tech_analysis": {
    "apis_evaluated": [...],
    "libraries_compared": [...],
    "stack_recommendation": {...},
    "flagged_features": [...],
    "feasibility_score": "high|medium|low"
  },
  "fact_validation": {
    "quality_score": 85,
    "verified_claims": [...],
    "flagged_issues": [...],
    "citation_index": [...]
  },
  "user_insights": {  // Optional
    "personas": [...],
    "pain_points": [...],
    "interview_questions": [...]
  },
  "handoff_to_lean_canvas": {
    "status": "READY",
    "key_insights": [...]
  }
}
```

---

## Integration with LEAN_CANVAS_VALIDATOR

The LEAN_CANVAS_VALIDATOR accepts `research_brief.json` as **optional input** and uses insights to enrich the Lean Canvas interview:

- **Problem (Field 1):** Uses `user_insights.pain_points`
- **Customer Segments (Field 2):** Uses `user_insights.personas`
- **UVP (Field 3):** Uses `market_analysis.positioning_opportunities`
- **Solution (Field 4):** Uses `tech_analysis.feasibility_score`
- **Revenue (Field 6):** Uses `market_analysis.pricing_insights`
- **Cost Structure (Field 7):** Uses `tech_analysis` for infrastructure costs
- **Riskiest Assumptions:** Uses `tech_analysis.flagged_features` + `market_analysis.risks`

**Backward Compatibility:** If no research_brief.json is available, LEAN_CANVAS_VALIDATOR works as before (normal interview without research insights).

---

## When to Use Research

**Use Research when:**
- ✅ You're entering a new market
- ✅ You need to validate market assumptions
- ✅ Technical feasibility is uncertain
- ✅ You need competitive intelligence
- ✅ You want citation-backed business planning

**Skip Research when:**
- ✅ You already have market research
- ✅ You're building for a known market
- ✅ Time constraints (Research adds 1-2 hours)
- ✅ Internal tools (no market validation needed)

---

## State Machine

See `01_planning_framework/state_machine/RESEARCH_workflow_design.yaml` for detailed workflow design including:
- Agent execution order
- Quality gates
- Exit conditions
- Error handling
- Handoff to BUSINESS_VALIDATION

---

## Success Criteria

**Research phase succeeds when:**
- ✅ All required agents complete (MARKET, TECH, FACT_VALIDATOR)
- ✅ FACT_VALIDATOR quality_score >= 50
- ✅ No critical hallucinations detected
- ✅ research_brief.handoff_to_lean_canvas.status == 'READY'

**Research phase fails when:**
- ❌ FACT_VALIDATOR quality_score < 50
- ❌ Critical hallucinations detected
- ❌ Quality gates fail

---

## Next Steps (Phase 2)

Phase 1 (Complete):
- ✅ Research agents integrated
- ✅ ORCHESTRATION_workflow_design.yaml updated
- ✅ LEAN_CANVAS_VALIDATOR updated for optional input
- ✅ Backward compatibility verified

Phase 2 (Upcoming):
- ⏳ Orchestrator Python script implementation
- ⏳ Optional research flag handling
- ⏳ FACT_VALIDATOR blocking logic
- ⏳ Full workflow testing

---

**Documentation:**
- Architecture Decision: `/docs/architecture/GAD-001_Research_Integration.md`
- State Machine: `state_machine/RESEARCH_workflow_design.yaml`
- Knowledge Index: Update `.knowledge_index.yaml` with research knowledge bases

**Prototype Source:** github.com/kimeisele/vibe-research (development sandbox)
