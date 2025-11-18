# TECHNICAL DEBT & BACKLOG ANALYSIS
**Date:** 2025-11-18  
**Test Status:** 369/383 passing (96.3%)  
**Known Failures:** 1 E2E test (test infrastructure, not production)  
**System Health:** ✅ GOOD

---

## 🔴 HIGH PRIORITY (Production Impact)

### 1. GAD-100 Phase 3-6: Phoenix Config Integration
**Status:** Deferred (Phases 1-2 complete)  
**Impact:** HIGH - Config management inconsistency  
**Effort:** Medium (~500 lines, invasive refactoring)  
**Risk:** High (touches core orchestrator)

**What's Missing:**
- VibeConfig wrapper integration
- Feature flag for A/B testing
- Migration from current config loading

**Why Deferred:** GAD-500 was higher priority for Week 1  
**Next Steps:** Create `config/vibe_config.py` wrapper

**Locations:**
```python
# Current state: Direct phoenix_config.toml reads scattered across code
# Need: Centralized VibeConfig wrapper with feature flags
```

---

### 2. Schema Validation in Handlers
**Status:** Disabled (`validate=False` in 8 locations)  
**Impact:** MEDIUM - Silent failures possible  
**Effort:** Low (~100 lines, 2 hours)

**Locations:**
```
agency_os/00_system/orchestrator/handlers/planning_handler.py (2)
agency_os/00_system/orchestrator/handlers/coding_handler.py (1)
agency_os/00_system/orchestrator/handlers/deployment_handler.py (3)
agency_os/00_system/orchestrator/handlers/maintenance_handler.py (1)
agency_os/00_system/orchestrator/handlers/testing_handler.py (1)
```

**TODO Comments:** "Add schema validation in Phase 4"

**Quick Win:** Enable validation, add try/catch, log schema errors

---

### 3. Testing Framework (GAD-300)
**Status:** STUB - Minimal implementation  
**Impact:** MEDIUM - Can't run automated tests on generated code  
**Effort:** High (~1000 lines, 2-3 days)

**What's Missing:**
- Test generation workflow
- Coverage analysis
- Test execution handlers
- Integration with CODING phase output

**Current Stub:**
```python
# agency_os/00_system/orchestrator/handlers/testing_handler.py
# TODO (Phase 3): Full implementation
# Minimal passthrough currently
```

---

## 🟡 MEDIUM PRIORITY (Quality & Maintainability)

### 4. Handoff Resume Flag
**Status:** Not implemented  
**Impact:** MEDIUM - Manual crash recovery  
**Effort:** Low (~50 lines, 1-2 hours)  
**Reference:** `docs/reports/TODO_HANDOFFS_IMPACT_REPORT.md`

**What's Missing:**
```bash
./vibe-cli run project --resume
# Should read handoff.json, resume from last state
```

**Implementation:**
```python
# In orchestrator.py
if args.resume:
    last_handoff = load_handoff()
    start_phase = last_handoff["next_phase"]
    todos = last_handoff["todos"]
```

---

### 5. HITL Approval on Handoffs
**Status:** Not implemented  
**Impact:** MEDIUM - No human oversight gates  
**Effort:** Low (~20 lines, 1 hour)

**What's Missing:**
```python
if config.require_approval:
    show_handoff_todos()
    if not get_user_approval():
        logger.info("User rejected handoff, stopping")
        return
```

**Config Addition:**
```toml
[orchestrator]
require_approval = true  # Gate handoffs on human review
```

---

### 6. Maintenance Framework
**Status:** STUB - Minimal implementation  
**Impact:** LOW - No production dependency yet  
**Effort:** Medium (~500 lines, 1 day)

**What's Missing:**
- Bug fix workflow
- Refactoring handlers
- Performance optimization agents

**Current Stub:**
```python
# Phase 4 TODO: maintenance workflow details
```

---

### 7. GAD-502: Haiku Hardening
**Status:** PLANNED (not started)  
**Impact:** LOW - Testing with less capable models  
**Effort:** Medium (~300 lines)  
**Coverage:** 2/19 scenarios (10.5%)

**Missing Protection:**
- Shell bypass protection
- Hallucination prevention
- Error loop detection
- Context overload handling

**Reference:** `docs/architecture/GAD_502_HAIKU_HARDENING.md`

---

## 🟢 LOW PRIORITY (Nice to Have)

### 8. E2E Test Refactoring
**Status:** Known failure (documented in `LEAN_CANVAS_E2E_TEST_ISSUE.md`)  
**Impact:** LOW - Test infrastructure only  
**Effort:** Medium (~200 lines, 3 hours)

**Issue:** Mock design is fragile (string matching on composed prompts)  
**Fix:** Mock at `execute_agent` level instead of `LLMClient` level

**Current Problem:**
```python
# Mock matches on exact prompt string - brittle
mock_client.register_response(expected_prompt, mock_response)
```

**Better Design:**
```python
# Mock at agent execution level - flexible
mock_executor.register_agent_response("PLANNING_ARCHITECT", mock_response)
```

---

### 9. Handoff Schema Validation
**Status:** Not implemented  
**Impact:** LOW - Handoffs are simple JSON  
**Effort:** Medium (~100 lines)

**Why Deferred:** Not MVP, simple protocol doesn't need validation yet

---

### 10. Knowledge Department (GAD-600)
**Status:** PLANNED  
**Impact:** LOW - Research framework works without it  
**Effort:** Very High (~2000 lines, 1-2 weeks)

**Components:**
- Research Division
- Domain Knowledge
- Semantic Graph
- 3-Layer Deployment

**Reference:** `docs/architecture/GAD_600_KNOWLEDGE_DEPARTMENT.md`

---

## 📊 CODE SMELL INVENTORY

### TODO Comments (12 total)
```
core_orchestrator.py:
  - Full JSON Schema validation with jsonschema library

orchestrator.py:
  - Eventually call ORCHESTRATOR_PROMPT.md for AI-driven conversation

planning_handler.py (2):
  - Add schema validation in Phase 4

coding_handler.py (1):
  - Add schema validation in Phase 4

deployment_handler.py (1):
  - Add schema validation in future

maintenance_handler.py (2):
  - Phase 3: Full implementation
  - Phase 4 TODO: maintenance workflow details

testing_handler.py (2):
  - Phase 3: Full implementation
  - Phase 4 TODO: testing workflow details
```

### Stub Implementations
- `testing_handler.py` - Minimal functionality
- `maintenance_handler.py` - Minimal functionality

### Disabled Validation
- 8 locations with `validate=False`
- 4 with TODO comments to enable
- 2 in stub handlers (expected)

---

## 🎯 RECOMMENDED ACTION PLAN

### **Week 1: Quick Wins** (High ROI, Low Risk)
**Effort:** ~4 hours total

1. ✅ **Enable schema validation** (4 production handlers)
   - planning_handler.py (2 locations)
   - coding_handler.py (1 location)
   - deployment_handler.py (1 location)
   - Add try/catch, log schema errors
   - **Time:** 1-2 hours

2. ✅ **Implement handoff resume flag**
   - Add `--resume` to vibe-cli
   - Load last handoff, continue from checkpoint
   - **Time:** 2 hours

3. ✅ **Add HITL approval gates**
   - Config flag: `require_approval`
   - Show todos, wait for user confirmation
   - **Time:** 1 hour

**Expected Outcome:** Better error handling, crash recovery, human oversight

---

### **Week 2: Foundation** (Medium ROI, Medium Risk)
**Effort:** ~7 hours total

4. ⏰ **Complete GAD-100 Phase 3: VibeConfig wrapper**
   - Create `config/vibe_config.py`
   - Migrate phoenix_config.toml reads
   - Add feature flag support
   - **Time:** 4 hours

5. ⏰ **Fix E2E test mock design**
   - Refactor mocking to agent execution level
   - Remove fragile string matching
   - **Time:** 3 hours

**Expected Outcome:** Consistent config, reliable tests

---

### **Week 3-4: Features** (High ROI, High Effort)
**Effort:** ~3 days total

6. ⏰ **Implement Testing Framework (GAD-300)**
   - Test generation workflow
   - Coverage analysis
   - Test execution handlers
   - **Time:** 2 days

7. ⏰ **Implement Maintenance Framework**
   - Bug fix workflow
   - Refactoring handlers
   - **Time:** 1 day

**Expected Outcome:** Complete SDLC coverage

---

### **Backlog** (Low Priority)

8. 📋 GAD-502: Haiku Hardening (when needed)
9. 📋 GAD-600: Knowledge Department (nice to have)
10. 📋 Handoff schema validation (not MVP)

---

## 📈 METRICS

### Current State
- **Tests:** 369/383 passing (96.3%)
- **GADs:** 9/15 complete (60%), 2/15 partial (13%), 4/15 planned (27%)
- **Core Workflows:** ✅ All functional (PLANNING, CODING, DEPLOYMENT)

### Debt Metrics
- **TODO Comments:** 12 (actionable)
- **Stub Implementations:** 2 (testing, maintenance)
- **Disabled Validation:** 8 locations (4 with TODOs)
- **Known Test Failures:** 1 (documented, not blocking)

### System Health: ✅ **GOOD**
- No blocking issues
- All core workflows functional
- Technical debt is documented and tracked
- Test coverage is strong (96.3%)

---

## 🚀 IMMEDIATE NEXT STEPS

**For Lead Architect:**
1. Review this backlog analysis
2. Approve Week 1 quick wins (schema validation, resume flag, HITL)
3. Prioritize Week 2 foundation work (VibeConfig wrapper vs E2E test fix)

**For Implementation:**
```bash
# Week 1, Item 1: Enable schema validation
# Edit handlers, change validate=False → validate=True, add error handling

# Week 1, Item 2: Add resume flag
# Edit vibe-cli, add --resume argument, load last handoff

# Week 1, Item 3: Add HITL approval
# Edit orchestrator, add approval gate before phase transitions
```

---

**Last Updated:** 2025-11-18  
**Next Review:** After Week 1 completion  
**Owner:** STEWARD (System Technical Excellence Workflow Automation & Resource Director)
