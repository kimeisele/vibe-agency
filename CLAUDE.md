# CLAUDE.md - Operational Truth Protocol

**Version:** 2.0
**Purpose:** Prevent hallucination. Show REAL operational status, not design intent.
**Last Updated:** 2025-11-15

---

## 🎯 CORE PRINCIPLES (Never Change)

1. **Don't trust "Complete ✅" without passing tests**
2. **Test first, then claim complete**
3. **When docs contradict code, trust code**
4. **When code contradicts tests, trust tests**
5. **When in doubt: RUN THE VERIFICATION COMMAND**

---

## 📖 What This Repo Is

**vibe-agency** = File-based prompt framework for AI-assisted software project planning.

**Architecture Reference:** See [ARCHITECTURE_V2.md](./ARCHITECTURE_V2.md) for conceptual model.

**Core Flow:**
```
User → vibe-cli → Core Orchestrator → SDLC Phases → Agents → Claude API
```

**5 SDLC Phases:**
1. PLANNING (4 sub-states: RESEARCH → BUSINESS_VALIDATION → FEATURE_SPECIFICATION → ARCHITECTURE_DESIGN)
2. CODING (5-phase code generation workflow)
3. TESTING (stub - transitions only)
4. DEPLOYMENT (stub - transitions only)
5. MAINTENANCE (stub - transitions only)

---

## ✅ OPERATIONAL STATUS (Dated Snapshot)

**Last Verified:** 2025-11-15

### Phase Implementation Status

| Phase | Status | Evidence | Verify Command |
|-------|--------|----------|----------------|
| PLANNING | ✅ Works | test_planning_workflow.py PASSES | `python tests/test_planning_workflow.py` |
| CODING Handler | ⚠️ Code exists, untested | coding_handler.py (211 lines) | `wc -l agency_os/00_system/orchestrator/handlers/coding_handler.py` |
| TESTING Handler | ⚠️ Stub only | testing_handler.py (108 lines) | `grep -n "STUB" agency_os/00_system/orchestrator/handlers/testing_handler.py` |
| DEPLOYMENT Handler | ⚠️ Stub only | deployment_handler.py (112 lines) | `grep -n "STUB" agency_os/00_system/orchestrator/handlers/deployment_handler.py` |
| MAINTENANCE Handler | ⚠️ Stub only | maintenance_handler.py (106 lines) | `grep -n "STUB" agency_os/00_system/orchestrator/handlers/maintenance_handler.py` |

### Core Components

| Component | Status | Evidence | Verify Command |
|-----------|--------|----------|----------------|
| Core Orchestrator | ✅ Works | State machine tested | `python tests/test_orchestrator_state_machine.py` |
| Prompt Registry | ✅ Works | 9 governance rules injected | `python tests/test_prompt_registry.py` |
| vibe-cli | ⚠️ Code exists, untested E2E | vibe-cli (629 lines) | `wc -l vibe-cli` |
| vibe-cli Tool Loop | ⚠️ Code exists, untested E2E | vibe-cli:426-497 | `grep -A 20 "def _execute_prompt" vibe-cli \| grep tool_use` |
| Research Agents | ⚠️ Missing deps | test fails: bs4 missing | `python tests/test_research_agent_e2e.py` |

### Planning Agents (✅ All Implemented)

| Agent | Status | Verify Command |
|-------|--------|----------------|
| VIBE_ALIGNER | ✅ Production ready | `ls -la agency_os/01_planning_framework/agents/VIBE_ALIGNER/` |
| LEAN_CANVAS_VALIDATOR | ✅ Production ready | `ls -la agency_os/01_planning_framework/agents/LEAN_CANVAS_VALIDATOR/` |
| GENESIS_BLUEPRINT | ✅ Production ready | `ls -la agency_os/01_planning_framework/agents/GENESIS_BLUEPRINT/` |
| MARKET_RESEARCHER | ⚠️ Needs bs4 | `python -c "import bs4" 2>&1` |
| TECH_RESEARCHER | ⚠️ Needs bs4 | `python -c "import bs4" 2>&1` |
| FACT_VALIDATOR | ⚠️ Needs bs4 | `python -c "import bs4" 2>&1` |
| USER_RESEARCHER | ✅ No tools needed | `ls -la agency_os/01_planning_framework/agents/research/USER_RESEARCHER/` |

### Knowledge Bases (✅ All Complete)

| File | Lines | Verify Command |
|------|-------|----------------|
| FAE_constraints.yaml | 736 | `wc -l agency_os/01_planning_framework/knowledge/FAE_constraints.yaml` |
| FDG_dependencies.yaml | 2546 | `wc -l agency_os/01_planning_framework/knowledge/FDG_dependencies.yaml` |
| APCE_rules.yaml | 1304 | `wc -l agency_os/01_planning_framework/knowledge/APCE_rules.yaml` |

---

## 🔍 HOW TO VERIFY CLAIMS

### Verify PLANNING Phase Works
```bash
python tests/test_planning_workflow.py
# Expected: All tests pass (state machine + transitions)
```

### Verify CODING Handler Exists (Not Just Placeholder)
```bash
wc -l agency_os/00_system/orchestrator/handlers/coding_handler.py
# Expected: >200 lines (211 as of 2025-11-15)
```

### Verify vibe-cli Has Tool Use Loop
```bash
grep -n "tool_use\|tool_result" vibe-cli | head -10
# Expected: Multiple matches in lines 426-497
```

### Verify Research Tools Dependencies
```bash
python -c "import bs4" 2>/dev/null && echo "✅ bs4 installed" || echo "❌ bs4 missing"
# Expected: bs4 missing (install: pip install beautifulsoup4)
```

### Verify Prompt Registry Works
```bash
python tests/test_prompt_registry.py
# Expected: All tests pass (governance injection)
```

---

## 🧪 META-TEST (Self-Verification)

**Can you trust THIS document?**

Run this to verify CLAUDE.md claims match reality:

```bash
#!/bin/bash
echo "=== CLAUDE.md Self-Verification ==="

# Test 1: PLANNING really works
python tests/test_planning_workflow.py && echo "✅ PLANNING verified" || echo "❌ PLANNING claim FALSE"

# Test 2: CODING handler exists (not stub)
[ $(wc -l < agency_os/00_system/orchestrator/handlers/coding_handler.py) -gt 50 ] && \
  echo "✅ CODING has implementation" || echo "❌ CODING is stub"

# Test 3: vibe-cli has tool loop
grep -q "tool_use" vibe-cli && grep -q "tool_result" vibe-cli && \
  echo "✅ vibe-cli has tool support" || echo "❌ vibe-cli missing tool loop"

# Test 4: bs4 dependency
python -c "import bs4" 2>/dev/null && \
  echo "✅ bs4 installed" || echo "❌ bs4 missing (pip install beautifulsoup4)"

# Test 5: Prompt Registry
python tests/test_prompt_registry.py 2>&1 | grep -q "PASSED" && \
  echo "✅ Prompt Registry verified" || echo "❌ Prompt Registry not tested"
```

**If ANY test fails, CLAUDE.md is out of date or system is broken.**

---

## ⚠️ KNOWN ISSUES (As of 2025-11-15)

### 1. Missing Dependencies
**Issue:** `bs4` (beautifulsoup4) not in requirements.txt
**Impact:** Research agents with tools fail
**Fix:** `pip install beautifulsoup4`
**Verify:** `python -c "import bs4"`

### 2. No CODING End-to-End Test
**Issue:** No `test_coding_workflow.py` exists
**Impact:** CODING handler (211 lines) never tested end-to-end
**Fix:** Write test similar to `test_planning_workflow.py`
**Verify:** `ls tests/test_coding_workflow.py`

### 3. No vibe-cli End-to-End Test
**Issue:** Tool use loop (Lines 426-497) never tested with real API
**Impact:** Unknown if multi-turn tool execution works
**Fix:** Write `test_vibe_cli_tool_loop.py` with mock API
**Verify:** `find tests -name "*vibe_cli*"`

### 4. Stubs Labeled as "Fully Implemented"
**Issue:** Some docs claim CODING "fully implemented" (true) but imply tested (false)
**Impact:** Misleading status - code exists but zero E2E tests
**Fix:** This document distinguishes "code exists" vs "works"

---

## 🚫 ANTI-PATTERNS (What NOT to Do)

### ❌ Don't Trust Docs Without Verification
```
BAD:  "README says complete → I assume it works"
GOOD: "README says complete → I run the test → Test missing → Status is 'untested'"
```

### ❌ Don't Confuse "Code Exists" with "Works"
```
BAD:  "coding_handler.py has 211 lines → CODING works"
GOOD: "coding_handler.py has 211 lines → CODING implemented, needs E2E test"
```

### ❌ Don't Propose Features That Already Exist
```
BAD:  "We need a tool use loop in vibe-cli"
GOOD: "vibe-cli has tool loop (L426-497) but needs E2E test"
```

### ❌ Don't Add "Future Vision" to CLAUDE.md
```
BAD:  "Phase 4 TODO: Implement XYZ"
GOOD: "XYZ not implemented: no code in expected location"
```

---

## 🎯 QUICK START (For New AI Assistants)

### Before Making Claims
```bash
# 1. Verify structure
ls -la agency_os/01_planning_framework/agents/

# 2. Check knowledge bases
wc -l agency_os/01_planning_framework/knowledge/*.yaml

# 3. Run tests to see what works
python tests/test_planning_workflow.py
python tests/test_research_agent_e2e.py  # Will fail: bs4 missing

# 4. Read honest assessment
cat ARCHITECTURE_V2.md  # Conceptual model
```

### When User Says "X is broken"
1. Run verification command from tables above
2. Read test output (don't just trust "FAILED")
3. Check actual error (e.g., "bs4 missing" vs "no integration layer")
4. Distinguish infrastructure issue from design gap

### When User Says "Implement X"
1. Search codebase first: `find . -name "*X*"`
2. Check if X already exists but is untested
3. Check ARCHITECTURE_V2.md for intended design
4. Only claim "missing" if no code exists

---

## 📚 Related Documents

- **[ARCHITECTURE_V2.md](./ARCHITECTURE_V2.md)** - Conceptual architecture (the "should be")
- **[SSOT.md](./SSOT.md)** - Implementation decisions (the "is")
- **Test files in `tests/`** - Source of truth for "works" claims

**Document Hierarchy:**
1. **Tests** = Ultimate truth (passing = works, missing = unknown)
2. **Code** = Implementation truth (exists = implemented, missing = todo)
3. **CLAUDE.md (this file)** = Operational snapshot (dated, expect drift)
4. **ARCHITECTURE_V2.md** = Conceptual model (intended design)
5. **Other docs** = May be outdated (verify before trusting)

---

## 🔄 MAINTENANCE

### When to Update This File

**✅ Update when:**
- New component reaches "passing tests" status
- Known issue is fixed (remove from Known Issues section)
- New critical component added to codebase
- Verification command changes

**❌ Don't update for:**
- Work in progress (wait for tests to pass)
- Future plans (belongs in roadmap, not here)
- Minor refactors (unless verification changes)

### How to Update

1. Make code change
2. Write/update test
3. Run test until it passes
4. Update this file with new status + verification command
5. Update "Last Verified" date
6. Run Meta-Test to ensure claims are accurate

---

## 📊 LEGEND

| Symbol | Meaning | Definition |
|--------|---------|------------|
| ✅ Works | Has passing test | Can execute NOW, verified |
| ⚠️ Untested | Code exists, no test | Implementation present, never verified end-to-end |
| ⚠️ Stub | Minimal implementation | Allows transitions but no real functionality |
| ❌ Broken | Test fails | Known issue, see Known Issues section |
| ❌ Missing | No code found | Not implemented, no files in expected location |

---

**Last Updated:** 2025-11-15
**Updated By:** Deep audit (Session: claude/review-claude-md-01CQioYzeKywYA8mEdTg3EB3)
**Next Review:** After CODING E2E test is written and passes

**Meta-Verification:**
```bash
# This document claims to be accurate as of 2025-11-15
# Run meta-test above to verify claims match reality
```
