# Master Prompt Template

**Version:** 1.0
**Purpose:** Standardized template for creating Master Prompts that work for all agent intelligence levels
**Last Updated:** 2025-11-17

---

## 📋 HOW TO USE THIS TEMPLATE

1. **Copy this file** to your GAD directory (e.g., `docs/architecture/GAD-1XX/Masterprompt-GAD-XYZ.md`)
2. **Fill in all sections** marked with `[FILL THIS IN]`
3. **Delete placeholder text** (anything in square brackets)
4. **Run verification** commands to ensure accuracy
5. **Commit** the completed Master Prompt

---

## 🎯 MASTER PROMPT: [FILL: Short descriptive title]

**GAD Reference:** [FILL: GAD-XXX or other architecture reference]
**Phase:** [FILL: Phase number or name (e.g., "Phase 3", "Integration", "Migration")]
**Estimated Time:** [FILL: Hours or days (e.g., "4-6 hours", "2 days")]
**Complexity:** [FILL: Simple | Medium | Complex | Expert-Only]
**Target Branch:** [FILL: Branch name (must start with claude/ and end with session ID)]

---

## 📊 CONTEXT (What You Need to Know)

### Current State
[FILL: Describe what exists NOW - be specific, provide verification commands]

**Verify current state:**
```bash
[FILL: Commands to verify current state]
# Example:
# ls -la agency_os/01_planning_framework/agents/
# uv run pytest tests/test_planning_workflow.py -v
```

### What's Broken/Missing
[FILL: List specific problems, regressions, or missing features]

**Evidence:**
```bash
[FILL: Commands that demonstrate the problem]
# Example:
# uv run pytest tests/ -v  # Shows failing tests
# grep -r "TODO" agency_os/  # Shows incomplete work
```

### Dependencies
[FILL: List what must exist BEFORE starting this work]

- [ ] [FILL: Dependency 1 - be specific]
- [ ] [FILL: Dependency 2 - include verification command]

**Verify dependencies:**
```bash
[FILL: Commands to verify dependencies are met]
```

---

## 🎯 GOAL (What Success Looks Like)

### Primary Objectives
[FILL: What MUST be delivered - numbered list, specific, measurable]

1. [FILL: Objective 1 - include success criteria]
2. [FILL: Objective 2 - include verification command]
3. [FILL: Objective 3 - include expected output]

### Success Criteria
[FILL: How do we know it's done? Be specific and measurable]

**Acceptance Tests:**
```bash
[FILL: Commands that prove success]
# Example:
# uv run pytest tests/test_new_feature.py -v  # All tests pass
# ./bin/verify-all.sh  # Zero regressions
```

**Expected Output:**
```
[FILL: What output do we expect to see?]
# Example:
# ✅ 15/15 tests passing
# ✅ Zero linting errors
# ✅ Documentation updated
```

### Non-Goals (What NOT to Do)
[FILL: Explicitly state what is OUT OF SCOPE to prevent scope creep]

- ❌ [FILL: Thing NOT to do]
- ❌ [FILL: Another thing to avoid]

---

## 🛠️ IMPLEMENTATION PLAN

### Phase 1: [FILL: Phase Name]
**Goal:** [FILL: What this phase delivers]
**Time:** [FILL: Estimated hours]

**Tasks:**
1. [FILL: Specific task - include file paths]
2. [FILL: Another task - include commands]
3. [FILL: Verification step]

**Verification:**
```bash
[FILL: Commands to verify Phase 1 complete]
```

**Deliverables:**
- [ ] [FILL: Deliverable 1 - specific file or feature]
- [ ] [FILL: Deliverable 2 - with verification]

---

### Phase 2: [FILL: Phase Name]
**Goal:** [FILL: What this phase delivers]
**Time:** [FILL: Estimated hours]

**Tasks:**
1. [FILL: Specific task]
2. [FILL: Another task]

**Verification:**
```bash
[FILL: Commands to verify Phase 2 complete]
```

**Deliverables:**
- [ ] [FILL: Deliverable 1]
- [ ] [FILL: Deliverable 2]

---

[FILL: Add more phases as needed - follow same structure]

---

## ✅ TEST-FIRST REQUIREMENTS (MANDATORY)

**Policy:** [Test-First Development](../../policies/TEST_FIRST.md) is MANDATORY.

### Test Strategy
[FILL: Describe how this work will be tested]

**Tests to Write/Update:**
1. [FILL: Test file 1 - what it tests]
2. [FILL: Test file 2 - what it tests]

**Test Execution:**
```bash
[FILL: Commands to run tests]
# Example:
# uv run pytest tests/test_new_feature.py -v
# uv run pytest --cov=module_name --cov-fail-under=80
```

**Coverage Requirements:**
- New code: **80% minimum**
- Bug fixes: **100% coverage**

---

## 🚨 KNOWN RISKS & MITIGATIONS

### Risk 1: [FILL: Risk name]
**Probability:** [High | Medium | Low]
**Impact:** [High | Medium | Low]
**Mitigation:** [FILL: How to prevent or handle this risk]

### Risk 2: [FILL: Risk name]
**Probability:** [High | Medium | Low]
**Impact:** [High | Medium | Low]
**Mitigation:** [FILL: How to prevent or handle this risk]

---

## 🔄 ROLLBACK PLAN

### If Things Go Wrong
[FILL: Step-by-step instructions to undo changes if work fails]

**Rollback Steps:**
```bash
[FILL: Commands to rollback changes]
# Example:
# git reset --hard HEAD
# git checkout main
# ./bin/verify-all.sh  # Verify main branch still works
```

**What Gets Preserved:**
[FILL: What should NOT be deleted during rollback]

- [FILL: Important file/data to preserve]

---

## 📚 REFERENCE MATERIALS

### Architecture Documents
[FILL: Links to relevant GAD/VAD/LAD docs]

- [FILL: GAD-XXX: Title](../GAD-XXX.md)
- [FILL: VAD-XXX: Title](../VAD/VAD-XXX.md)

### Related Code
[FILL: Links to key files/modules that will be modified]

- [FILL: File 1](../../path/to/file.py) - Brief description
- [FILL: File 2](../../path/to/file.py) - Brief description

### External Resources
[FILL: Links to external docs, tutorials, or references]

- [FILL: Resource name](https://example.com) - Why it's relevant

---

## 🎓 CONTEXT FOR AGENTS (All Intelligence Levels)

### For Simple Agents (Haiku)
[FILL: Ultra-simple explanation - what to do, step by step, no ambiguity]

**Step-by-step:**
1. [FILL: First thing to do]
2. [FILL: Second thing to do]
3. [FILL: How to verify it worked]

**If you get stuck:**
[FILL: Where to ask for help, what error messages mean]

### For Advanced Agents (Sonnet/Opus)
[FILL: High-level context - architectural reasoning, design decisions]

**Key Design Decisions:**
- [FILL: Decision 1 - why this approach was chosen]
- [FILL: Decision 2 - trade-offs considered]

**Optimization Opportunities:**
[FILL: Optional improvements that could be made (but are NOT required)]

---

## 🔍 VERIFICATION CHECKLIST (Before Marking Complete)

Run these commands and ensure ALL pass:

```bash
# 1. Tests pass
[FILL: Test commands]

# 2. Linting clean
uv run ruff check . --fix
uv run ruff format .

# 3. No regressions
./bin/verify-all.sh

# 4. Documentation updated
[FILL: Documentation verification commands]

# 5. Pre-push checks
./bin/pre-push-check.sh
```

**Manual Checks:**
- [ ] [FILL: Manual check 1]
- [ ] [FILL: Manual check 2]
- [ ] All TODOs in code resolved or tracked
- [ ] CLAUDE.md updated with new verification commands (if applicable)
- [ ] Session handoff updated

---

## 📝 COMPLETION REPORT (Fill this out when DONE)

**Completed By:** [FILL: Agent name/session ID]
**Date:** [FILL: YYYY-MM-DD]
**Time Taken:** [FILL: Actual hours/days]
**Branch:** [FILL: Branch name]
**PR Number:** [FILL: #XXX]

### What Was Delivered
[FILL: List what was actually completed - be specific]

- [FILL: Deliverable 1 - include file paths]
- [FILL: Deliverable 2 - include verification]

### Deviations from Plan
[FILL: What changed during implementation and why]

- [FILL: Change 1 - reason]
- [FILL: Change 2 - reason]

### Final Verification
```bash
[FILL: Copy-paste output of verification commands]
```

### Known Issues / Follow-Up Work
[FILL: Any issues discovered or work that needs to happen next]

- [FILL: Issue 1 - create GitHub issue if needed]
- [FILL: Issue 2 - reference ticket number]

---

## 🎯 NEXT STEPS (After This Work)

### Immediate Follow-Up
[FILL: What should happen immediately after this work is merged]

1. [FILL: Next step 1]
2. [FILL: Next step 2]

### Future Enhancements
[FILL: Ideas for future improvements (not required now)]

- [FILL: Enhancement 1]
- [FILL: Enhancement 2]

---

**END OF TEMPLATE**

---

## 📖 TEMPLATE USAGE NOTES

### When to Use This Template
- Creating Master Prompts for GAD implementations
- Planning complex multi-phase work
- Delegating work to other agents (any intelligence level)
- Ensuring work is reproducible and verifiable

### When NOT to Use This Template
- Trivial one-step tasks (just do it)
- Exploratory research (use a simpler format)
- Bug fixes (use GitHub issue template)

### Template Maintenance
- Update version number when template structure changes
- Keep verification commands aligned with current tooling
- Ensure compatibility with Test-First Development policy
