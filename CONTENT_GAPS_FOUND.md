# Content Gaps Found - Prompt Frameworks

**Date:** 2025-11-13
**Method:** Integration testing of prompt composition
**Status:** UPDATED after KB loading fix

---

## Critical Findings

### 1. Knowledge Base Loading Was Broken ✅ FIXED

**Problem:** Code checked for `used_by_tasks`, but YAMLs use `used_in_tasks`
**Fix:** Updated `prompt_runtime.py` lines 170, 177 to support both
**Result:** KB now loads correctly!
- Task 03 went from 8,549 → 36,807 chars (FAE loaded!)

---

## Missing Files

### VIBE_ALIGNER Knowledge Base

**Missing:**
1. `agency_os/01_planning_framework/knowledge/PROJECT_TEMPLATES.yaml`

**Referenced in:** `_knowledge_deps.yaml` line 38 (optional knowledge)
**Impact:** Task 02 (feature_extraction) cannot load optional templates
**Severity:** LOW (optional feature)

---

### GENESIS_BLUEPRINT Gates

**Missing:**
1. `agency_os/01_planning_framework/agents/GENESIS_BLUEPRINT/gates/gate_no_extensions_in_core.md`
2. `agency_os/01_planning_framework/agents/GENESIS_BLUEPRINT/gates/gate_all_features_mapped.md`

**Referenced in:** `task_02_design_extensions.meta.yaml` lines 34, 36
**Impact:** Task 02 cannot be composed completely
**Severity:** HIGH (blocks task execution)

**Existing gates:**
- ✅ `gate_extension_isolation.md`
- ✅ `gate_module_count_range.md`
- ✅ `gate_stdlib_only_core.md`

---

## Test Results (After KB Fix)

```
❌ VIBE_ALIGNER/02_feature_extraction: FAILED (missing PROJECT_TEMPLATES.yaml)
✅ VIBE_ALIGNER/03_feasibility_validation: OK (36,807 chars) ← KB loaded!
✅ GENESIS_BLUEPRINT/01_select_core_modules: OK (16,563 chars)
❌ GENESIS_BLUEPRINT/02_design_extensions: FAILED (missing gates)
```

**Passed:** 2/4 (50%)
**Failed:** 2/4 (50%)

---

## Next Steps

1. Create missing gate files
2. Test remaining GENESIS_BLUEPRINT tasks (03, 04, 05)
3. Test other agents (CODE_GENERATOR, QA_VALIDATOR, etc.)

---

## Knowledge Base Loading Status

**Observation:** All tests show `✓ Resolved 0 knowledge dependencies`

**Question:** Why are Knowledge Bases not being loaded?

**Check needed:**
- Are `_knowledge_deps.yaml` files configured correctly?
- Are `used_by_tasks` fields populated?
- Should FAE/FDG/APCE be loaded for VIBE_ALIGNER tasks?

---

## To Be Tested

- [ ] GENESIS_BLUEPRINT tasks 03-05
- [ ] CODE_GENERATOR tasks
- [ ] QA_VALIDATOR tasks
- [ ] DEPLOY_MANAGER tasks
- [ ] All agent KB loading
