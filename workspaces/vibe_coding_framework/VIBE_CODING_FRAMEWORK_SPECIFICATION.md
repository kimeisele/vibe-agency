# VIBE Coding Framework - Complete Specification

**Project Type:** Commercial
**Abstraction Level:** META (Framework for framework-building)
**Framework Version:** v1.1 (Pragmatic Mode - Hybrid: Commercial + Vague Requirements)
**Generated:** 2025-11-13
**Status:** Planning Complete ✓

---

## 🎯 Executive Summary

**Vision:** Empower non-technical users to create professional-grade code specifications through conversational AI-guided interviews

**The Gap:** AI code generation tools (GitHub Copilot, Bolt, Cursor) require technical specifications as input. Non-technical users can't create these specs → Ideas die before they start.

**Our Solution:** Conversational framework that transforms vague ideas into structured specifications (Markdown PRDs, JSON for AI tools) through guided dialogue.

**Unique Value:** First tool for SPECIFICATION generation (not code generation) - creates the input layer for existing AI code tools

---

## 🏗️ Core Architecture

```
vibe-spec CLI
   ├── Interview Engine (tree-based question flow, state machine)
   ├── Template Library (web app, mobile, API, data pipeline, etc.)
   ├── LLM Orchestrator (Claude API: question generation + plain language parsing)
   ├── Knowledge Base (DOGFOODED: NFR_CATALOG.yaml, FAE_constraints.yaml)
   └── Output Generator (Markdown PRD, JSON for AI code tools)
```

**Key Differentiators:**
- **vs. No-Code Platforms:** Creates specs, not apps (upstream layer)
- **vs. AI Code Generators:** Focuses on WHAT (spec) not HOW (code)
- **vs. Claude Skills:** Domain-agnostic (any software) + refactorable

---

## 📦 Features (MoSCoW)

### MUST HAVE (MVP - 73 complexity points, 12-16 weeks)

| ID | Feature | Complexity | Description |
|----|---------|------------|-------------|
| **F001** | Conversational Interview Engine | 21 | Tree-based question flow with backtracking, non-linear navigation |
| **F002** | Template Library | 13 | 5 starter templates (web, mobile, API, data, admin dashboard) |
| **F003** | Specification Output | 13 | Export to Markdown PRD + JSON (for Bolt, Cursor, etc.) |
| **F004** | Iterative Refinement | 13 | Edit existing specs section-by-section (refactorable requirement) |
| **F006** | Plain Language Parser | 13 | LLM-powered NLP to extract structured data from vague answers |
| **F010** | CLI Interface | 13 | Click + Rich terminal UI (cross-platform) |

### SHOULD HAVE (Phase 2 - 42 complexity points)

| ID | Feature | Description |
|----|---------|-------------|
| **F005** | AI Question Generation | LLM generates contextual follow-up questions |
| **F007** | NFR Triage Module | **DOGFOODED:** Reuses our NFR_CATALOG.yaml |
| **F008** | Constraint Checker | **DOGFOODED:** Reuses our FAE_constraints.yaml |

### COULD HAVE (Future)

| ID | Feature | Phase |
|----|---------|-------|
| **F009** | Export Integrations | Phase 4 (Bolt, Jira, Linear) |
| **F011** | Quality Analyzer | Phase 5 (AI-powered spec analysis) |

---

## 🎨 Dogfooding Architecture (Meta-Value)

**Reused from Planning Framework:**

1. **NFR_CATALOG.yaml** → F007 (NFR Triage)
   - Proven ISO 25010-based NFR categories
   - Saves 2-3 weeks development time

2. **FAE_constraints.yaml** → F008 (Constraint Checker)
   - Battle-tested anti-pattern detection
   - Warns users about impossible requirements

3. **LEAN_CANVAS interview** → Template for business validation projects

4. **VIBE_ALIGNER 4-phase structure** → Template for software projects

**Meta-Validation Test:** Use VIBE Coding Framework to generate spec for VIBE Coding Framework v2.0 (Inception Test)

---

## 🔒 Critical NFRs

| NFR | Requirement | Priority | Implementation |
|-----|-------------|----------|----------------|
| **USAB-LEARNABILITY** | Non-technical user completes first spec in < 30 min | CRITICAL | Interactive tutorial, plain language, examples |
| **MAIN-MODULARITY** | "Robust and dynamic" architecture (user requirement) | CRITICAL | Plugin architecture, swappable LLM providers |
| **MAIN-REUSABILITY** | Dogfood Planning Framework components | CRITICAL | Import NFR_CATALOG, FAE_constraints directly |
| **SEC-CONFIDENTIALITY** | User ideas are private (stealth startups) | CRITICAL | Consent flow, opt-in logging, local-first |
| **REL-AVAILABILITY** | Works offline (template mode) | HIGH | Graceful LLM fallback, cached responses |
| **COST-LLM-API** | Minimize API costs | HIGH | Aggressive caching, user budget limits ($5/project) |

**NEW NFR DISCOVERED:** `MAIN-REUSABILITY` - Specific to frameworks/ecosystems (not in original NFR_CATALOG.yaml)

---

## 🛠️ Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Language** | Python 3.10+ | Cross-platform, best LLM libraries (LangChain) |
| **CLI Framework** | Click + Rich | Proven in our Planning Framework, beautiful output |
| **LLM Integration** | LangChain + Claude API | Multi-provider support, caching built-in |
| **State Management** | python-statemachine | Supports backtracking (non-linear flow) |
| **Templates** | Jinja2 + YAML | Powerful templating, human-readable configs |
| **Caching** | diskcache | Persistent LLM response cache (cost savings) |
| **Testing** | pytest + coverage | 70%+ coverage target |

---

## 🚀 Implementation Roadmap

### Phase 1: MVP (12-16 weeks)

| Week | Milestone |
|------|-----------|
| 1-2 | Project setup, CLI skeleton, LLM POC |
| 3-5 | Interview Engine (state machine, question tree) |
| 6-8 | Template Library (5 templates) |
| 9-10 | LLM Orchestrator (F005 Question Gen, F006 Parser) |
| 11-12 | Output Generator (Markdown, JSON), Refinement (F004) |
| 13-14 | Dogfooding integration (NFR + FAE) |
| 15-16 | UX polish (tutorial, help), testing, docs |

**Deliverables:**
- ✅ CLI tool: `vibe-spec new → interview → export spec.md`
- ✅ 5 templates (web, mobile, API, data, admin)
- ✅ Markdown PRD + JSON output
- ✅ 70%+ test coverage
- ✅ Dogfooding validation (NFR + FAE integration)

---

## 📊 Success Metrics

### MVP Success Criteria

1. ✅ **Usability:** 80% of non-technical users complete first spec in < 30 min
2. ✅ **Quality:** Developers rate generated specs 7/10 or higher
3. ✅ **Completeness:** Specs include functional reqs, NFRs, constraints, acceptance criteria
4. ✅ **Meta-Test:** Framework generates high-quality spec for itself (dogfooding)

### Riskiest Assumptions (Validation Required)

| ID | Assumption | Validation Method | Risk Level |
|----|------------|-------------------|------------|
| **RA-001** | Users WANT spec tools (vs. just wanting apps built) | Interviews with 20 PMs/entrepreneurs | CRITICAL |
| **RA-002** | Generated specs are useful for developers | Developer feedback study (10 specs) | CRITICAL |
| **RA-003** | Conversational > Forms/Wizards | A/B test (completion rate) | HIGH |

---

## 🎯 CLI Usage

```bash
# Install
$ pip install vibe-spec

# Configure
$ vibe-spec config --llm-provider=claude --api-key=<key>

# Start new specification
$ vibe-spec new --template=web_app

# Conversational interview (example)
> What problem does your app solve?
User: Freelance designers waste 5 hours/week on invoicing

> Who are your target users?
User: Freelance designers and small creative agencies

[... guided questions ...]

# Export specification
$ vibe-spec export <id> --format=md > my_project_spec.md
$ vibe-spec export <id> --format=json > spec.json  # For Bolt/Cursor

# Refine existing spec
$ vibe-spec edit my_project_spec.md
```

---

## 🔄 v1.1 Framework Test #3 - Observations

### Test Context

- **Project Type:** Commercial (but vague requirements)
- **User Confidence:** MEDIUM-LOW ("die Frage, wie man sowas aufbauen würde")
- **Abstraction Level:** META (framework for framework-building)
- **Mode Used:** **HYBRID MODE** (Commercial + Vague = Full Interview + Auto-Research)

### Edge Cases Discovered

#### 1. HYBRID MODE (Commercial + Vague Requirements)
**Problem:** v1.1 defines Quick Research (nonprofit) and Full Interview (commercial), but what about commercial projects with vague requirements?

**What Happened:** Framework adapted well - used Full Interview structure WITH Auto-WebSearch research

**Recommendation:** **Formalize "Hybrid Mode"** in v1.2
```yaml
if project_type == "commercial" AND user_confidence == "LOW":
  mode: HYBRID_MODE
  structure: Full Interview (9 fields)
  augmentation: Auto-WebSearch for each vague answer
```

---

#### 2. META/RECURSIVE REQUIREMENTS
**Problem:** Estimating complexity and defining features for "frameworks" is fundamentally different than "apps"

**Examples:**
- "Interview Engine" is abstract vs. "User Login" is concrete
- FAE rules target app features, not framework components
- NFRs for frameworks prioritize MODULARITY over SCALABILITY

**What Happened:** Added `abstraction_level: META` field to project_manifest

**Recommendation:** **Add abstraction_level taxonomy** to v1.2
```yaml
abstraction_levels:
  - CONCRETE: Apps, websites, APIs (standard features)
  - LIBRARY: Reusable components, SDKs (API-focused)
  - FRAMEWORK: Tools to build tools (meta-features)
  - PLATFORM: Multi-tenant systems (ecosystem-focused)
```

---

#### 3. WEBSEARCH PARTIAL FAILURE
**Problem:** WebSearch failed 2/5 times (Claude Skills, PRD tools searches)

**What Happened:** Framework continued with available research data, no catastrophic failure

**Current Behavior:** No explicit fallback - just missing data

**Recommendation:** **Add graceful degradation strategy**
```python
if websearch_fails:
  1. Log warning: "WebSearch unavailable, using cached knowledge"
  2. Mark gaps in lean_canvas: "research_quality: PARTIAL"
  3. Suggest user manually research missing areas
  4. Continue with available data
```

---

#### 4. DOGFOODING SCENARIO
**Problem:** User is building a tool SIMILAR to the framework being used (circular dependency)

**What Happened:** Framework didn't recognize the similarity - could have offered shortcuts

**Example:** When building VIBE Coding Framework:
- Could auto-suggest: "I see you're building a specification tool. Would you like to use our Planning Framework structure as a template?"

**Recommendation:** **Add "similar project detection"** in v1.2
```python
def detect_similar_projects(user_description):
    if "specification" in user_description and "framework" in user_description:
        suggest_template("planning_framework_meta_template")
```

---

#### 5. NEW NFR DISCOVERED: MAIN-REUSABILITY
**Problem:** ISO 25010 NFR catalog doesn't include "reusability" as separate category

**Discovery:** For frameworks/ecosystems, ability to reuse components is CRITICAL NFR

**Current Workaround:** Added as sub-characteristic of MAIN-MODULARITY

**Recommendation:** **Add MAIN-REUSABILITY to NFR_CATALOG.yaml v2.0**
```yaml
- category_id: "NFR-MAIN"
  sub_characteristics:
    - id: "MAIN-REUSABILITY"
      name: "Component Reusability"
      prompt_question: "How important is it to reuse components across multiple projects/frameworks?"
      applicability: ["framework", "library", "platform"]
```

---

## 📋 Framework Improvements for v1.2

### Priority: CRITICAL

1. **Formalize Hybrid Mode**
   - Define: Commercial + Vague = Full Interview + Auto-Research
   - Document in SOP_001
   - Add mode detection logic

2. **WebSearch Fallback Strategy**
   - Graceful degradation when WebSearch fails
   - Mark research quality (HIGH/PARTIAL/LOW)
   - Suggest manual research areas

---

### Priority: HIGH

3. **abstraction_level Taxonomy**
   - Add field to project_manifest.schema.json
   - Values: CONCRETE | LIBRARY | FRAMEWORK | PLATFORM
   - Affects: Feature extraction, FAE applicability, NFR priorities

4. **MAIN-REUSABILITY NFR**
   - Add to NFR_CATALOG.yaml as separate sub-characteristic
   - Applicability: Frameworks, libraries, platforms
   - Question: "How important is component reuse across projects?"

---

### Priority: MEDIUM

5. **Dogfooding Detection**
   - Detect when user is building similar tool
   - Suggest relevant templates from existing frameworks
   - Example: "Building spec tool? Use Planning Framework as template"

6. **FAE Applicability Metadata**
   - Add `applicable_to: [app, library, framework, platform]` to FAE rules
   - Filter irrelevant warnings for meta-projects
   - Example: FAE-009 (offline-first) doesn't apply to CLI frameworks

---

## 🎓 Key Learnings

### What Worked Excellent

✅ **Auto-WebSearch Trigger:** User said "wie man sowas aufbauen würde" → Framework auto-researched conversation design patterns

✅ **Dogfooding Opportunities Identified:** NFR_CATALOG, FAE_constraints reuse saves 4-6 weeks development

✅ **Hybrid Mode (implicit):** Commercial + vague worked well even without explicit definition

✅ **Meta-Validation:** Using framework to build framework proves concept

---

### What Needs Improvement

⚠️ **Abstraction Handling:** Framework treats all "features" equally - doesn't adapt to meta/library/platform differences

⚠️ **WebSearch Reliability:** Partial failures need better handling

⚠️ **NFR Catalog Gaps:** Missing MAIN-REUSABILITY for ecosystem building

⚠️ **Mode Documentation:** Hybrid mode exists in practice but not in theory

---

**Generated by:** VIBE Agency Planning Framework v1.1 (Pragmatic Mode - Hybrid)
**Total Artifacts:** 8 (lean_canvas, 4 phases, blueprint, specification, test observations)
**Meta-Test Result:** ✅ **SUCCESS** - Framework successfully specified itself (dogfooding validated)
