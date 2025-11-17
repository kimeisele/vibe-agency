# SEMANTIC ANALYSIS: Technical Debt & Non-Blocking Backlog Strategy
## For vibe-agency JSON State Machine System

**Date:** 2025-11-17
**Analysis Type:** Semantic (What actually works) vs Syntactic (Does code exist)
**Focus:** How to track technical debt without blocking progress

---

## THE PROBLEM: Greenwall Symptom

### What We See (Syntactic View)
```
✅ GAD-005-ADDITION_HAIKU_HARDENING.md exists
✅ Implementation plan documented (6 phases)
✅ Test framework created (19 test scenarios)
✅ Some scenarios passing (2/19)
✅ Status marked "APPROVED"
```

### What Actually Works (Semantic View)
```
Phase 1: ✅ COMPLETE - Test harness exists
Phase 2: ❌ TODO - Shell guards not implemented
Phase 3: ❌ TODO - Error simplification not done
Phase 4: ❌ TODO - Context fixes not done
Phase 5: ❌ TODO - Recovery guidance not done
Phase 6: ❌ TODO - Haiku sim not started

Current Protection: 2/19 scenarios (10.5%)
Claimed Status: "APPROVED"
Reality Status: "Phase 1 only"
```

### The Debt Incurred
**Implicit Commitment:** "By GAD-006, this will be Haiku-proof"
**Current Delivery:** Only test harness, no actual hardening
**Risk:** If we deploy with current state + Haiku agent → system WILL break

---

## ROOT CAUSE: No Semantic Debt Tracking

### Where Semantics Break Down

**File: `test_rogue_agent_scenarios.py`**
```python
# Line 65
pytest.skip("TODO: Implement shell command kernel checks (GAD-006 Phase 2)")

# This is SEMANTIC DEBT:
# - Syntactically: Test file exists ✅
# - Semantically: Test never runs ❌
# - Status: Looks green (file exists), is red (skipped)
```

**File: `GAD-005-ADDITION_HAIKU_HARDENING.md`**
```markdown
### Phase 2: Shell-Level Guardrails (Week 3)
**Status:** NOT STARTED

Phases 3-6 follow similar pattern: Documented → NOT STARTED
```

**Files with Similar Debt:**
- `docs/architecture/GAD-006_KNOWLEDGE_DEPT_VISION.md` - Vision doc, no code
- `docs/architecture/GAD-007_STEWARD_GOVERNANCE_VISION.md` - Vision doc, no code
- `docs/architecture/GAD-008_INTEGRATION_MATRIX_VISION.md` - Vision doc, no code

**Pattern:** Many files marked PARTIAL or TODO with grand visions, minimal implementation.

---

## SEMANTIC CLASSIFICATION: What Counts as "Done"?

### Level 1: Documented ✍️
```
Exists: YES ✅
Code: NO ❌
Tests: NO ❌
Regression Risk: ZERO (no code to break)
Example: GAD-006_KNOWLEDGE_DEPT_VISION.md (architectural vision)
```

### Level 2: Code Exists, Untested ⚙️
```
Exists: YES ✅
Code: YES ✅
Tests: NO (mocked/skipped) ⚠️
Regression Risk: MEDIUM (code could have bugs)
Example: Shell command kernel check (documented, not implemented)
```

### Level 3: Tests Exist but Skipped 🔄
```
Exists: YES ✅
Code: NO ❌
Tests: YES (but pytest.skip()) ⚠️
Regression Risk: LOW (no code), but semantic debt HIGH
Example: test_rogue_agent_scenarios.py (11 scenarios skipped)
```

### Level 4: Fully Implemented & Tested ✅
```
Exists: YES ✅
Code: YES ✅
Tests: YES (passing) ✅
Regression Risk: LOW (tested)
Example: MOTD implementation, Kernel checks (Level 0/1)
```

---

## GAD-005-HAIKU: Semantic Debt Analysis

### Phase-by-Phase Reality

| Phase | Deliverable | Documented | Code | Tests | Status | Debt | Impact |
|-------|------------|-----------|------|-------|--------|------|--------|
| 1 | Test harness | ✅ | ✅ | ✅ (pass) | ✅ DONE | ZERO | Test framework ready |
| 2 | Shell guards | ✅ | ❌ | ✅ (skip) | ❌ TODO | **HIGH** | Can't prevent bypasses |
| 3 | Error clarity | ✅ | ❌ | ✅ (skip) | ❌ TODO | **HIGH** | Haiku misinterprets |
| 4 | Context fixes | ✅ | ❌ | ✅ (skip) | ❌ TODO | **HIGH** | MOTD too long |
| 5 | Recovery guides | ✅ | ❌ | ✅ (skip) | ❌ TODO | **HIGH** | No escalation |
| 6 | Haiku sim | ⚠️ | ❌ | ✅ (skip) | ❌ TODO | **CRITICAL** | Can't validate |

**Semantic Verdict:** ⚠️ PHASE 1 ONLY - Phases 2-6 are "todo()" not "done()"

### Protection Gap Analysis

```
Current State (Phase 1 only):
├─ Shell bypasses: 0/3 protected ❌ VULNERABLE
├─ Git bypasses: 0/1 protected ❌ VULNERABLE
├─ Hallucinations: 0/2 protected ❌ VULNERABLE
├─ Context overload: 0/2 protected ❌ VULNERABLE
├─ Error loops: 0/2 protected ❌ VULNERABLE
├─ Misinterpretation: 1/3 protected ⚠️ PARTIAL
└─ Recovery guidance: 1/6 protected ⚠️ PARTIAL

TOTAL: 2/19 scenarios (10.5%) ← THIS IS THE ACTUAL STATUS
```

### High-Impact Phases (Lean Approach)

**If we only do Phase 2 (Shell Guards):**
```
+6 scenarios protected (+32%)
Cost: ~8 hours
Impact: CRITICAL (blocks major bypass vector)
Regression Risk: MEDIUM (shell checks could affect workflows)
```

**If we add Phase 3 (Error Clarity):**
```
+2 more scenarios (+10.5%)
Cost: ~4 hours
Impact: HIGH (Haiku misinterpretation is real risk)
Regression Risk: LOW (error messages only)
```

**Lean Recommendation:**
Do Phase 2 + 3 first (12 hours → 52.6% protection) before:
- Phase 4 (context fixes - nice to have)
- Phase 5 (recovery - important but can be manual escalation)
- Phase 6 (Haiku sim - validation only, no protection)

---

## SOLUTION: JSON-Based Technical Debt Tracking

### Design Principles

**For JSON State Machine Systems:**
1. ✅ Minimal - One JSON schema, no database
2. ✅ Git-compatible - Human-readable, versionable
3. ✅ Non-blocking - Work continues while debt tracked
4. ✅ Semantic - Tracks reality, not documentation
5. ✅ Actionable - Clear phase + impact + effort

### Proposed Schema: `.debt_backlog.json`

```json
{
  "version": "1.0",
  "last_updated": "2025-11-17T12:00:00Z",
  "system_status": {
    "health": "95% operational, 2/19 security scenarios",
    "blocking_issues": 0,
    "technical_debt_items": 11
  },
  "work_packages": [
    {
      "id": "GAD-005-HAIKU-Phase-2",
      "title": "Shell-Level Guardrails",
      "description": "Block shell commands that bypass Python kernel checks",
      "semantics": {
        "documented": true,
        "code_exists": false,
        "tests_exist": true,
        "tests_passing": false,
        "tests_status": "3 skipped (pytest.skip())"
      },
      "impact": {
        "protection_scenarios": 6,
        "protection_coverage": "32% → 42%",
        "blocking_issues_fixed": 3,
        "regression_risk": "MEDIUM"
      },
      "effort": {
        "estimated_hours": 8,
        "phases": ["shell_pattern_matcher", "integration_tests", "docs"],
        "priority": "P0 - Blocks Haiku deployment"
      },
      "dependencies": [],
      "status": "TODO",
      "lean_score": 6,  // High impact, medium effort = 6 (max 10)
      "tracked_in": "tests/test_rogue_agent_scenarios.py:65"
    },
    {
      "id": "GAD-005-HAIKU-Phase-3",
      "title": "Simplified Error Messages",
      "description": "Make all errors Haiku-readable (1-sentence + examples)",
      "semantics": {
        "documented": true,
        "code_exists": false,
        "tests_exist": true,
        "tests_passing": false,
        "tests_status": "2 skipped (pytest.skip())"
      },
      "impact": {
        "protection_scenarios": 2,
        "protection_coverage": "42% → 52.6%",
        "blocking_issues_fixed": 2,
        "regression_risk": "LOW"
      },
      "effort": {
        "estimated_hours": 4,
        "phases": ["error_template_refactor", "kernel_error_updates", "tests"],
        "priority": "P1 - High impact, low risk"
      },
      "dependencies": [],
      "status": "TODO",
      "lean_score": 9,  // Very high impact, low effort = 9
      "tracked_in": "tests/test_rogue_agent_scenarios.py:118"
    },
    {
      "id": "GAD-005-HAIKU-Phase-4",
      "title": "Context Overload Fixes",
      "description": "Shorten CLAUDE.md, simplify prompts, highlight MOTD alerts",
      "semantics": {
        "documented": true,
        "code_exists": false,
        "tests_exist": true,
        "tests_passing": false,
        "tests_status": "2 skipped (pytest.skip())"
      },
      "impact": {
        "protection_scenarios": 2,
        "protection_coverage": "52.6% → 63%",
        "regression_risk": "LOW"
      },
      "effort": {
        "estimated_hours": 6,
        "phases": ["claude_md_trim", "prompt_refactor", "motd_redesign"],
        "priority": "P2 - Nice to have"
      },
      "dependencies": ["GAD-005-HAIKU-Phase-3"],
      "status": "TODO",
      "lean_score": 5,  // Medium impact, medium effort
      "tracked_in": "tests/test_rogue_agent_scenarios.py:132,141"
    },
    {
      "id": "MOTD-Test-Sync-Mismatch",
      "title": "Fix show-context file name mismatch",
      "description": "Test expects show-context.sh, code has show-context.py",
      "semantics": {
        "documented": false,
        "code_exists": true,
        "tests_exist": true,
        "tests_passing": false,
        "tests_status": "1 assertion fails (line 94)"
      },
      "impact": {
        "protection_scenarios": 0,
        "verification_impact": "Blocks verify-all.sh (shows failure even though code works)",
        "regression_risk": "NONE"
      },
      "effort": {
        "estimated_hours": 0.5,
        "phases": ["update_test", "verify"],
        "priority": "P0 - Unblocks verification"
      },
      "dependencies": [],
      "status": "READY_TO_FIX",
      "lean_score": 10,  // Trivial effort, high confidence impact
      "tracked_in": "tests/test_motd.py:94"
    },
    {
      "id": "CLAUDE-md-Documentation-Drift",
      "title": "Update 8 doc files with correct show-context filename",
      "description": "References to show-context.sh should be show-context.py",
      "semantics": {
        "documented": false,
        "code_exists": true,
        "tests_exist": true,
        "tests_passing": true,
        "code_is_correct": true,
        "documentation_is_correct": false
      },
      "impact": {
        "user_impact": "Users read docs, try to run nonexistent file",
        "regression_risk": "NONE"
      },
      "effort": {
        "estimated_hours": 1,
        "phases": ["batch_search_replace"],
        "priority": "P1 - UX improvement"
      },
      "dependencies": ["MOTD-Test-Sync-Mismatch"],
      "status": "READY_TO_FIX",
      "lean_score": 9,  // Trivial, improves UX significantly
      "tracked_in": ["CLAUDE.md:8 refs", "docs/architecture/GAD-*.md:7 refs"]
    }
  ],
  "regression_analysis": {
    "risks": [
      {
        "phase": "GAD-005-HAIKU-Phase-2",
        "risk": "Shell guard patterns might be too aggressive",
        "example": "Block legitimate sed usage in workflows",
        "mitigation": "Test against current workflow patterns first",
        "probability": "MEDIUM"
      },
      {
        "phase": "GAD-005-HAIKU-Phase-4",
        "risk": "Shortening CLAUDE.md might remove important details",
        "example": "Haiku or users miss critical context",
        "mitigation": "Use critical_section markers, not just trim",
        "probability": "MEDIUM"
      }
    ],
    "regression_test_plan": [
      "Run full test suite after each phase",
      "Test with real agent workflows (not just unit tests)",
      "Check git history for new edge cases"
    ]
  },
  "git_reality": {
    "last_commit": "33b1d12 Update GAD-005-ADDITION_HAIKU_HARDENING.md",
    "semantic_gap": "Phase 1 complete, Phases 2-6 documented but not implemented",
    "commits_since_phase1": 12,
    "commits_that_touched_phase2_code": 0,
    "commits_that_updated_phase2_docs": 3,
    "implication": "Documentation updated 3 times, code not touched once"
  },
  "decision_questions": {
    "q1": {
      "question": "Should we complete Phase 2 + 3 now or defer to GAD-006?",
      "options": {
        "now": {
          "pros": ["52.6% protection immediately", "Blocks Haiku from breaking system"],
          "cons": ["Takes 12 hours", "Delays other work"],
          "effort": "12 hours"
        },
        "defer": {
          "pros": ["Keeps current scope focused", "GAD-006 explicitly plans Phase 2-6"],
          "cons": ["Haiku deployment blocked", "Technical debt grows"],
          "effort": "0 hours now, 18+ hours later"
        }
      }
    },
    "q2": {
      "question": "How to prevent semantic debt accumulation?",
      "options": {
        "strict": {
          "approach": "No test skip() allowed - all tests must pass or be removed",
          "pros": ["Prevents documentation-code drift"],
          "cons": ["Can't document future work in tests"]
        },
        "lean": {
          "approach": "skip() is OK, but .debt_backlog.json must track it",
          "pros": ["Documents intent + reality", "Non-blocking"],
          "cons": ["Requires discipline to maintain"]
        },
        "hybrid": {
          "approach": "skip() with @debt decorator, auto-generation to backlog",
          "pros": ["Automatic tracking", "Code documents debt"],
          "cons": ["More tooling needed"]
        }
      },
      "recommendation": "Hybrid - use decorator for semantic tracking"
    },
    "q3": {
      "question": "How to measure 'Lean' impact?",
      "metric": "lean_score = (scenarios_fixed * 100) / effort_hours",
      "example": "Phase 3: (2 * 100) / 4 = 50 points per hour",
      "use": "Prioritize Phase 3 before Phase 4 (5 pts/hour)"
    }
  }
}
```

---

## TRACKING MECHANISM: Lean Decorator

### For Developers: Mark Semantic Debt Automatically

```python
# tests/test_rogue_agent_scenarios.py

from functools import wraps

def semantic_debt(phase: str, scenarios: int, effort_hours: int, priority: str):
    """
    Decorator to track semantic debt in test skips.

    Enables .debt_backlog.json auto-generation.
    """
    def decorator(func):
        func._semantic_debt = {
            "phase": phase,
            "scenarios": scenarios,
            "effort_hours": effort_hours,
            "priority": priority,
            "lean_score": (scenarios * 100) / effort_hours if effort_hours > 0 else 0
        }
        return func
    return decorator


# Usage in test file:

@semantic_debt(
    phase="GAD-005-HAIKU-Phase-2",
    scenarios=6,
    effort_hours=8,
    priority="P0"
)
def test_agent_overwrites_manifest_via_shell():
    """Agent tries: echo '{}' > manifest.json"""
    pytest.skip("TODO: Implement shell command kernel checks (GAD-006 Phase 2)")


# Script to generate .debt_backlog.json:
# scripts/generate-debt-backlog.py
# Reads all @semantic_debt markers and builds the JSON
```

### Integration with CI/CD

```bash
#!/bin/bash
# bin/pre-push-check.sh (extended)

echo "Checking for semantic debt..."

# Generate debt backlog
python scripts/generate-debt-backlog.py

# Report summary
echo ""
echo "📋 Technical Debt Summary:"
python -c "
import json
with open('.debt_backlog.json') as f:
    data = json.load(f)
    print(f\"  Total items: {len(data['work_packages'])}\"
    print(f\"  Blocking: {len([w for w in data['work_packages'] if w['status'] == 'BLOCKING'])}\")
    print(f\"  Ready to fix: {len([w for w in data['work_packages'] if w['status'] == 'READY_TO_FIX'])}\")
    total_lean = sum(w['lean_score'] for w in data['work_packages'])
    print(f\"  Total lean score: {total_lean}\")
"

# Optional: Fail if debt exceeds threshold
DEBT_ITEMS=$(grep -c '"status": "TODO"' .debt_backlog.json)
if [ $DEBT_ITEMS -gt 15 ]; then
    echo "⚠️  Warning: High technical debt (>15 items). Consider addressing."
fi

# Optional: Require P0 items to be addressed within N commits
```

---

## REGRESSION ANALYSIS: What Could Break?

### Phase 2 (Shell Guards) - Regression Scenarios

| Scenario | Risk | Current Impact | Mitigation |
|----------|------|-----------------|------------|
| Block legitimate sed edits | MEDIUM | Some workflows use sed for file edits | Whitelist patterns: `sed -i 's/foo/bar/' *.md` |
| Block git hooks installation | LOW | git config core.hooksPath is rare | Explicitly allow .githooks directory |
| False positive on rm -rf | HIGH | Users might need to delete test dirs | Require confirmation, not block |
| Break test cleanup | MEDIUM | Tests use rm in teardown | Allow .venv, .pytest_cache deletion |

**Test Strategy:**
```bash
# Before deploying Phase 2:
./bin/test-shell-patterns.sh

# Run against real workflow patterns
# Example: Agent runs 40 common git/file operations
# Verify: All legitimate ops pass, all attacks blocked
```

### Phase 4 (Context Fixes) - Regression Scenarios

| Scenario | Risk | Mitigation |
|----------|------|-----------|
| Remove critical section from CLAUDE.md | MEDIUM | Use `<!-- CRITICAL: Keep this -->` markers |
| Prompt truncation loses important details | HIGH | Test agent comprehension with shortened prompts |
| MOTD truncation hides warnings | MEDIUM | Reorder: Alerts first, then status |

---

## RECOMMENDATION: Phase Implementation Order (Lean)

### Sprint 0 (Immediate - 2 hours)
```
✅ Fix MOTD test/code mismatch (0.5h)
✅ Update docs for show-context.py (1h)
✅ Commit and verify (0.5h)

Result: 18/18 verification tests pass
Debt items remaining: 11
```

### Sprint 1 (This week - 12 hours)

**If you have capacity:**
```
✅ Phase 2: Shell Guards (8h) - lean_score 6
✅ Phase 3: Error Clarity (4h) - lean_score 9

Result: 52.6% protection (10/19 scenarios)
Debt items remaining: 7
Haiku deployment: NOW POSSIBLE (with caution)
```

**If limited capacity:**
```
✅ Phase 3 only: Error Clarity (4h) - lean_score 9

Result: 52.6% protection (with Phase 1)
Debt items remaining: 11
Haiku deployment: BLOCKED (needs Phase 2 first)
```

### Sprint 2 (Next sprint - defer if busy)
```
⏸️ Phase 4: Context Fixes (6h) - lean_score 5
⏸️ Phase 5: Recovery (6h) - lean_score 4
⏸️ Phase 6: Haiku Sim (8h) - lean_score 2

Reason: Lower priority (Phase 2+3 cover 80% of risk)
```

---

## METRICS: How to Know You're Done

### Definition of "Haiku-Ready"

```json
{
  "haiku_ready_criteria": {
    "scenario_coverage": {
      "threshold": "80%",
      "current": "10.5%",
      "target_phases": ["Phase 2", "Phase 3", "Phase 5"]
    },
    "test_coverage": {
      "threshold": "100% of scenarios have passing tests",
      "current": "2/19 passing"
    },
    "error_clarity": {
      "threshold": "All errors have examples + remediation",
      "current": "10/15 error types improved"
    },
    "git_safety": {
      "threshold": "No direct shell bypasses possible",
      "current": "2 vectors still open"
    },
    "verification": {
      "threshold": "verify-all.sh shows 18/18 + GAD-005-HAIKU shows 100%",
      "current": "17/18 + 10.5%"
    }
  }
}
```

---

## FINAL ANSWER TO YOUR QUESTION

### "How to handle technical debt in JSON state machine?"

**Answer: Use semantic tracking + lean scoring**

```json
{
  "principle_1": "Code + tests = truth, documentation = intent",
  "principle_2": "Skip tests is OK, track in .debt_backlog.json",
  "principle_3": "Score by lean_score (impact/effort), not by status",
  "principle_4": "Non-blocking work in parallel (semantic debt ≠ project blocker)",
  "principle_5": "Git reality (commits) > documentation (plans)",
  "implementation": [
    "Create .debt_backlog.json (single source of truth for debt)",
    "Use @semantic_debt decorator on skip() tests",
    "Auto-generate JSON from code (scripts/generate-debt-backlog.py)",
    "Include in pre-push-check.sh (report, don't block)",
    "Prioritize by lean_score (max impact/effort)",
    "Track regressions (mitigation per phase)",
    "Report git_reality (commits-since-debt-created)"
  ]
}
```

### Why This Works

1. **Minimal**: One JSON file, one decorator, one script
2. **Git-friendly**: JSON diff shows debt changes
3. **Non-blocking**: You can work while debt tracked
4. **Semantic**: Tracks reality (code + tests), not wishful thinking
5. **Actionable**: Lean score tells you what to do first
6. **Transparent**: Everyone sees what's pending and why

### What You Get

- ✅ Clear picture of real vs. documented status
- ✅ Lean priority (Phase 3 before Phase 4)
- ✅ Regression awareness (what could break)
- ✅ Non-blocking backlog (work in parallel)
- ✅ Git reality (commits reveal truth)

---

## APPENDIX: Why This Problem Exists

### Structural Root Cause

**The Gap:**
```
Testing Framework        Reality
├─ Tests exist          ├─ Phase 1 complete
├─ Tests documented     ├─ Phases 2-6 todo
└─ Tests skipped        └─ Looks like less work than it is
```

**The Pressure:**
1. "Create test harness" (Phase 1) → Easy, feels complete
2. "Document phases" → Easy, looks impressive
3. "Implement phases" → Hard, nobody commits to timeline
4. System appears 80% done after Phase 1

**The Consequence:**
- New agents inherit incomplete system
- Tests give false confidence
- Debt compounds silently
- Discovery only at deployment

**The Fix:**
Make debt **visible**, **trackable**, **prioritizable** without blocking day-to-day work.

---

**Next Step:** Create `.debt_backlog.json` + decide on Phase 2/3 timing.

Then: Senior Sonnet knows exactly what's pending and why.

