# CLAUDE.md - Truth Protocol for AI Assistants

**Version:** 1.0
**Date:** 2025-11-15
**Purpose:** Prevent hallucination. Show REAL implementation status, not design intent.

---

## 🚨 CRITICAL: Read This First

If you are an AI assistant (Claude, GPT, Gemini, etc.) working on this repo:

**DO NOT TRUST ANYTHING MARKED "Complete ✅" WITHOUT VERIFYING TESTS PASS.**

This document contains the VERIFIED truth about what actually works vs. what's just designed.

---

## What This Repo Is

**vibe-agency** is a file-based prompt framework for software project planning. It uses Claude AI (via delegated mode) to transform vague ideas into validated specs.

**Core Architecture:**
- **Deterministic ("not alive")**: State machine in `core_orchestrator.py`, knowledge bases in YAML
- **Intelligent ("alive")**: Claude Code handles prompts, decisions, fallbacks via STDIN/STDOUT

**Workflow Phases:**
1. PLANNING (VIBE_ALIGNER, LEAN_CANVAS_VALIDATOR, optional RESEARCH)
2. CODING (placeholder)
3. TESTING (placeholder)
4. DEPLOYMENT (placeholder)
5. MAINTENANCE (placeholder)

**Only PLANNING is fully implemented. Everything else is design-only.**

---

## VERIFIED Implementation Status (Tests Run 2025-11-15)

### ✅ WHAT ACTUALLY WORKS (Tests Pass)

#### 1. VIBE_ALIGNER (Planning Agent)
- **Status:** ✅ FULLY FUNCTIONAL
- **Evidence:** User has successfully used it for real projects
- **Location:** `agency_os/01_planning_framework/agents/VIBE_ALIGNER/`
- **Workflow:** 6-step feature specification (Education → Extraction → Feasibility → Gaps → Negotiation → Output)
- **Output:** `feature_spec.json`

#### 2. Knowledge Bases (Static YAML)
- **Status:** ✅ COMPLETE
- **Files:**
  - `FAE_constraints.yaml` (736 lines - feasibility rules)
  - `FDG_dependencies.yaml` (2546 lines - dependency mappings)
  - `APCE_rules.yaml` (1304 lines - complexity scoring)
  - `TECH_STACK_PATTERNS.yaml`, `PROJECT_TEMPLATES.yaml`
- **Evidence:** Files exist, YAML is valid, used by VIBE_ALIGNER

#### 3. Prompt Composition System
- **Status:** ✅ FUNCTIONAL
- **Location:** `agency_os/00_system/runtime/prompt_runtime.py`
- **Features:** Composes prompts from `_prompt_core.md` + tasks + knowledge deps
- **Evidence:** VIBE_ALIGNER works, which uses this system

#### 4. Core Orchestrator (Basic State Machine)
- **Status:** ✅ PARTIALLY FUNCTIONAL
- **Location:** `agency_os/00_system/orchestrator/core_orchestrator.py`
- **What Works:**
  - Phase transitions (PLANNING → CODING → etc.)
  - Agent routing for PLANNING phase
  - Manifest management (project_manifest.json)
- **What DOESN'T Work:** Tool execution loop (see below)

---

### ⚠️ WHAT'S DESIGNED BUT BROKEN (Tests Fail)

#### 1. Research Sub-Framework (GAD-001/GAD-003)
- **Status:** ⚠️ **INCOMPLETE - CRITICAL DESIGN FLAWS**
- **Location:** `agency_os/01_planning_framework/agents/research/`
- **What EXISTS:**
  - 4 research agents (MARKET_RESEARCHER, TECH_RESEARCHER, FACT_VALIDATOR, USER_RESEARCHER)
  - Tool definitions (`tool_definitions.yaml`)
  - Tool executor (`tool_executor.py`)
  - Google Custom Search client (`google_search_client.py`)
  - Web fetch client (`web_fetch_client.py`)

- **What's BROKEN:**
  - **STDIN/STDOUT protocol has NO integration layer** (see GAD-003_COMPLETION_ASSESSMENT.md:100-112)
  - Orchestrator sends `INTELLIGENCE_REQUEST` to STDOUT - but who reads it?
  - Orchestrator blocks on `sys.stdin.readline()` - but who sends input?
  - **Result:** Orchestrator will HANG FOREVER waiting for input that never comes

- **Evidence:**
  - Test: `tests/test_research_agent_e2e.py` - **FAILS** with detailed gap analysis
  - Error: "NO integration layer exists!" (line 153 of test output)

- **What's Needed to Fix:**
  1. Either: Build Claude Code integration wrapper that implements STDIN/STDOUT protocol
  2. Or: Rewrite orchestrator to call Anthropic API directly (no STDIN/STDOUT)
  3. Either way: Write end-to-end test with REAL Claude API, not just unit tests

#### 2. Tool Execution (Google Search, Web Fetch)
- **Status:** ⚠️ **WORKS IN ISOLATION, BROKEN IN ORCHESTRATOR**
- **Evidence:**
  - `tool_executor.py` works when called directly
  - `google_search_client.py` works with valid API keys
  - But orchestrator's tool loop (core_orchestrator.py:631-663) will block on STDIN

- **Dependencies:**
  - ✅ FIXED: Added `requests`, `beautifulsoup4`, `google-api-python-client` to requirements.txt
  - ⚠️ REQUIRED: `GOOGLE_SEARCH_API_KEY` and `GOOGLE_SEARCH_ENGINE_ID` env vars (see docs/GOOGLE_SEARCH_SETUP.md)

---

### ❌ WHAT'S DESIGN-ONLY (No Implementation)

#### 1. CODING Framework
- **Status:** ❌ PLACEHOLDER ONLY
- **Location:** `agency_os/02_code_gen_framework/`
- **Evidence:** Agent structure exists, but no implementation

#### 2. TESTING Framework (QA)
- **Status:** ❌ PLACEHOLDER ONLY
- **Location:** `agency_os/03_qa_framework/`

#### 3. DEPLOYMENT Framework
- **Status:** ❌ PLACEHOLDER ONLY
- **Location:** `agency_os/04_deploy_framework/`

#### 4. MAINTENANCE Framework
- **Status:** ❌ PLACEHOLDER ONLY
- **Location:** `agency_os/05_maintenance_framework/`

---

## Architecture Decision Records (GADs) - REAL Status

### GAD-001: Research Integration
- **Status:** ⚠️ Phase 1 claimed "Complete", but tests FAIL
- **File:** `docs/architecture/GAD-001_Research_Integration.md`
- **Reality:** Infrastructure exists, but STDIN/STDOUT integration missing

### GAD-002: Core SDLC Orchestration
- **Status:** ✅ Phase 1-3 COMPLETE (state machine works for PLANNING)
- **File:** `docs/architecture/GAD-002_Core_SDLC_Orchestration.md`
- **Reality:** Only PLANNING phase is implemented

### GAD-003: Research Capability Restoration
- **Status:** ⚠️ INCOMPLETE (own assessment admits this!)
- **File:** `docs/architecture/GAD-003_COMPLETION_ASSESSMENT.md:6`
- **Quote:** "Status: ⚠️ INCOMPLETE - Critical design gaps identified"
- **Reality:** Tools work in isolation, orchestrator integration broken

---

## How to Verify Claims (Anti-Hallucination Protocol)

When someone says "X is complete", verify with:

```bash
# 1. Run tests
python tests/test_research_agent_e2e.py
python tests/test_planning_workflow.py

# 2. Check for dependencies
pip install -r requirements.txt

# 3. Look for REAL usage, not just structure
ls -la agency_os/02_code_gen_framework/  # (Empty = not implemented)

# 4. Read completion assessments
cat docs/architecture/GAD-003_COMPLETION_ASSESSMENT.md
```

---

## Known Issues (As of 2025-11-15)

1. **STDIN/STDOUT Protocol Incomplete** (GAD-003 blocker)
   - Orchestrator implements one side, but no integration layer exists
   - Orchestrator will block forever on `sys.stdin.readline()`

2. **Research Agents Not Runnable** (despite structure existing)
   - Tools work in isolation
   - No end-to-end path from user input → research → output

3. **Misleading "Complete ✅" Markers**
   - Many docs claim completion without passing tests
   - README.md in research/ says "Phase 1 Complete" but tests fail

4. **Missing Dependencies in requirements.txt** (FIXED 2025-11-15)
   - `requests`, `beautifulsoup4`, `google-api-python-client` were missing
   - Now added

---

## What to Build Next (No New Features!)

**DO NOT add new features until core is verified:**

1. **Fix GAD-003 STDIN/STDOUT Integration**
   - Option A: Build Claude Code wrapper script
   - Option B: Rewrite orchestrator to use Anthropic API directly
   - Write E2E test with REAL Claude API

2. **Write Integration Tests**
   - Test VIBE_ALIGNER end-to-end with real manifest
   - Test state transitions (PLANNING → CODING)
   - Test error handling (missing artifacts, invalid input)

3. **Fix Misleading Docs**
   - Update GAD-001 README to reflect REAL status
   - Remove "Complete ✅" from untested components
   - Add "Verified: [date]" to completed items

4. **Infrastructure Hardening**
   - Add pytest to CI/CD
   - Add test coverage requirements
   - Enforce: No "Complete" without passing test

---

## For External Consultants / AI Assistants

**Before proposing new features (like "GAD-004"), verify what already exists:**

1. Read this file (CLAUDE.md) - it's the source of truth
2. Run tests: `python tests/test_*.py`
3. Check `docs/architecture/GAD-003_COMPLETION_ASSESSMENT.md` for known gaps
4. If proposing "missing module X", search codebase first: `find . -name "*X*"`

**The user is frustrated because previous assistants:**
- Proposed features that already exist
- Claimed completion without running tests
- Used fancy metaphors instead of showing code
- Iterated endlessly without building

**Be different: Test first, build second, verify third.**

---

## Quick Start (For New AI Assistants)

```bash
# 1. Verify structure
ls -la agency_os/01_planning_framework/agents/

# 2. Check knowledge bases
wc -l agency_os/01_planning_framework/knowledge/*.yaml

# 3. Run tests to see what's broken
python tests/test_research_agent_e2e.py  # Will fail with gap analysis

# 4. Read the honest assessment
cat docs/architecture/GAD-003_COMPLETION_ASSESSMENT.md

# 5. Ask user: "What specifically should I verify/fix?" (Don't propose new features!)
```

---

## Anti-Pattern: What NOT to Do

❌ **Don't say:** "I'll implement GAD-004: Graph-Based Knowledge Module"
✅ **Do say:** "GAD-003 is incomplete. Should I fix the STDIN/STDOUT integration or rewrite to use Anthropic API directly?"

❌ **Don't say:** "Research module is missing"
✅ **Do say:** "Research module exists but integration is broken (see test output)"

❌ **Don't say:** "Phase 1 complete ✅"
✅ **Do say:** "Phase 1 structure exists, but tests fail. Need to fix [specific issue]."

---

## Test Evidence (Last Run: 2025-11-15 02:24:59 UTC)

```
tests/test_research_agent_e2e.py:
  ✅ XML parsing works
  ✅ Tool executor works (in isolation)
  ❌ STDIN/STDOUT protocol BROKEN (no integration layer)
  ❌ End-to-end flow FAILS (orchestrator blocks on stdin)

Verdict: GAD-003 NOT complete despite docs claiming it
```

---

## Maintainer Notes

**This file (CLAUDE.md) is the ONLY source of truth for AI assistants.**

When implementation status changes:
1. Run tests to verify
2. Update this file with evidence (test output, file paths)
3. Add verification date
4. Remove "broken" markers only when tests pass

**No "complete ✅" without passing tests. Period.**

---

**Last Updated:** 2025-11-15 02:25 UTC
**Updated By:** Claude (Sonnet 4.5) - Session: claude/research-steward-module-01LJ5RTQxriP5nZSXYEhte7f
**Next Review:** After GAD-003 STDIN/STDOUT integration is fixed
