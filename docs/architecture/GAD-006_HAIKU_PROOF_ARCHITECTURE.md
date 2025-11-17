# GAD-006: Haiku-Proof Architecture

**Status:** 📋 PLANNING
**Priority:** 🔥 CRITICAL (Enables cost-efficient operation)
**Depends On:** GAD-005 (Runtime Engineering)
**Created:** 2025-11-16

---

## 🎯 OBJECTIVE

**Make vibe-agency operable by less capable AI agents (Claude Haiku or dumber) without risk of rogue behavior.**

**Success Criteria:**
- ✅ Haiku agent can complete PLANNING workflow without operator intervention
- ✅ System prevents all identified rogue behaviors (19 scenarios)
- ✅ Error messages are "Haiku-readable" (simple, actionable)
- ✅ MOTD complexity reduced (critical alerts highlighted)
- ✅ Recovery guidance provided for all blocked operations

**Why This Matters:**
- **Cost Efficiency:** Haiku is 10-20x cheaper than Sonnet ($0.25/MTok vs $3/MTok)
- **Robustness:** If Haiku can't break it, nothing can
- **Human-Proof:** Simplifications that help Haiku also help humans
- **Defense-in-Depth:** Ultimate test of our layered architecture

---

## 📊 CURRENT STATE ANALYSIS

### Where Agents Get Intelligence

| Source | Type | Effectiveness | Haiku Risk |
|--------|------|---------------|------------|
| CLAUDE.md | Static Context | High | ⚠️ Too long (450 lines) |
| ARCHITECTURE_V2.md | Conceptual Model | Medium | ⚠️ Abstract concepts |
| Agent Prompts | Task Instructions | High | ⚠️ Some complex (200+ lines) |
| Knowledge Bases | Domain Rules | High | ✅ Structured (YAML) |
| MOTD | Runtime Context | High | ⚠️ 15+ lines, easy to miss alerts |
| Session Handoff | Agent-to-Agent | High | ✅ Simple JSON |
| Layer 0/1 | Boot Checks | Very High | ✅ Unavoidable |
| Pre-Action Kernel | Runtime Blocks | Very High | ⚠️ Python-only (shell bypass) |

### Current Vulnerabilities (19 Identified Scenarios)

#### 1️⃣ Hallucination Scenarios
- ❌ Agent references non-existent files (test exists)
- ❌ Agent invents workflow states (not tested)
- ❌ Agent hallucinates commands (not tested)

#### 2️⃣ Bypass Attempts
- ❌ **CRITICAL:** Agent uses `echo "{}" > manifest.json` (kernel bypass)
- ❌ **CRITICAL:** Agent runs `git push` (skips pre-push-check.sh)
- ⚠️ Agent modifies `.vibe/` directory (detected but not prevented)

#### 3️⃣ Misinterpretation Scenarios
- ✅ Agent ignores MOTD linting alert (kernel blocks commit)
- ❌ Agent loops on failed operation (no loop detection)
- ❌ Agent doesn't understand error message (too complex)

#### 4️⃣ Context Overload Scenarios
- ❌ Agent misses critical detail in 1000+ line prompt
- ❌ Agent skims MOTD, misses alerts (no critical section)

#### 5️⃣ Recovery Guidance Gaps
- ❌ Kernel errors lack working examples
- ❌ Repeated violations don't escalate to operator

**Score:** 2/19 scenarios protected (10.5%)
**Target:** 19/19 scenarios protected (100%)

---

## 🏗️ IMPLEMENTATION PLAN

### Phase 1: Test Harness (Week 1) - ✅ COMPLETE

**Deliverables:**
- ✅ `tests/test_rogue_agent_scenarios.py` (19 test scenarios)
- ✅ Test categories: Hallucination, Bypass, Misinterpretation, Context Overload, Recovery

**Evidence:**
```bash
uv run pytest tests/test_rogue_agent_scenarios.py -v
# Expected: 1 failed, 1 passed, 11 skipped (implementation pending)
```

**Why This Phase Matters:**
- Documents ALL known rogue behaviors
- Provides clear pass/fail criteria
- Forces us to think like a "dumb" agent

---

### Phase 2: Shell-Level Guardrails (Week 2)

**Problem:** Kernel only blocks Python operations, not shell commands.

**Solution:** Add shell command kernel checks to `core_orchestrator.py`.

**Implementation:**
```python
# In agency_os/00_system/orchestrator/core_orchestrator.py

import re
import shlex

class CoreOrchestrator:
    def _kernel_check_shell_command(self, command: str) -> None:
        """
        Kernel check: Block dangerous shell operations.

        Prevents shell-based bypasses of Python kernel checks.
        """
        # Parse command (handle pipes, redirects, etc.)
        try:
            tokens = shlex.split(command)
        except ValueError:
            # Malformed command - let shell handle it
            return

        # Check for dangerous patterns
        dangerous_patterns = [
            # File overwrites
            (r'echo.*>\s*(manifest\.json|\.session_handoff\.json)',
             "Cannot overwrite critical files via shell",
             "Use: orchestrator.save_artifact('manifest', data)"),

            # Git operations
            (r'git\s+push(?!\s+-u\s+origin\s+claude/)',
             "Cannot push without pre-push checks",
             "Use: ./bin/pre-push-check.sh && git push"),

            # System integrity violations
            (r'(rm|mv|cp).*\.vibe/',
             "Cannot modify system integrity directory",
             "This directory is protected by Layer 0 verification"),

            # Direct manifest manipulation
            (r'(cat|sed|awk).*>\s*manifest\.json',
             "Cannot directly edit manifest.json",
             "Use: orchestrator.save_artifact('manifest', data)"),
        ]

        for pattern, message, remediation in dangerous_patterns:
            if re.search(pattern, command):
                raise KernelViolationError(
                    message=message,
                    remediation=remediation,
                    example=self._get_safe_alternative(pattern)
                )

    def _get_safe_alternative(self, pattern: str) -> str:
        """Return working example for blocked operation."""
        examples = {
            "manifest": "orchestrator.save_artifact('manifest', {'phase': 'CODING'})",
            "git_push": "./bin/pre-push-check.sh && git push -u origin claude/feature-branch",
            "vibe_dir": "# Do not modify .vibe/ - it's protected by system integrity checks",
        }
        # ... return relevant example
```

**Integration Points:**
1. vibe-cli: Check shell commands before execution
2. Orchestrator: Check before subprocess.run()
3. Tests: Validate all bypass attempts blocked

**Test Coverage:**
```python
def test_agent_overwrites_manifest_via_shell():
    # Agent tries: echo '{}' > manifest.json
    with pytest.raises(KernelViolationError) as exc:
        orchestrator._kernel_check_shell_command("echo '{}' > manifest.json")
    assert "Cannot overwrite critical files" in str(exc.value)
    assert "orchestrator.save_artifact" in str(exc.value)  # Remediation

def test_agent_pushes_without_precheck():
    # Agent tries: git push origin main
    with pytest.raises(KernelViolationError) as exc:
        orchestrator._kernel_check_shell_command("git push origin main")
    assert "pre-push checks" in str(exc.value)
```

**Deliverables:**
- `_kernel_check_shell_command()` method (50 LOC)
- Integration into vibe-cli and orchestrator
- 5+ tests passing in `test_rogue_agent_scenarios.py`

---

### Phase 3: Simplified Error Messages (Week 2)

**Problem:** Current errors assume agent intelligence.

**Solution:** Make ALL errors "Haiku-readable" with clear structure.

**Error Message Template:**
```
🚫 BLOCKED: [What you tried to do]

WHY: [Simple 1-sentence explanation]

WHAT TO DO INSTEAD:
  1. [Primary solution with command]
  2. [Alternative approach]
  3. [If stuck: Ask operator]

EXAMPLE:
  ✅ [Working code]
  ❌ [What you just tried]

📚 LEARN MORE: [Link to docs/architecture/*.md]
```

**Implementation:**
```python
class KernelViolationError(Exception):
    """
    Kernel violation with Haiku-readable error message.

    All errors MUST include:
    - Simple explanation (1 sentence, no jargon)
    - Actionable remediation (numbered steps)
    - Working example (copy-pasteable)
    """

    def __init__(
        self,
        operation: str,
        why: str,
        remediation: list[str],
        example_good: str,
        example_bad: str,
        learn_more: str = None
    ):
        self.operation = operation
        self.why = why
        self.remediation = remediation
        self.example_good = example_good
        self.example_bad = example_bad
        self.learn_more = learn_more

    def __str__(self):
        msg = f"🚫 BLOCKED: {self.operation}\n\n"
        msg += f"WHY: {self.why}\n\n"
        msg += "WHAT TO DO INSTEAD:\n"
        for i, step in enumerate(self.remediation, 1):
            msg += f"  {i}. {step}\n"
        msg += f"\nEXAMPLE:\n"
        msg += f"  ✅ {self.example_good}\n"
        msg += f"  ❌ {self.example_bad}\n"
        if self.learn_more:
            msg += f"\n📚 LEARN MORE: {self.learn_more}\n"
        return msg
```

**Example Usage:**
```python
# Before
raise KernelViolationError("Cannot overwrite manifest.json")

# After
raise KernelViolationError(
    operation="You tried to overwrite manifest.json",
    why="This file tracks project state. Overwriting breaks the system.",
    remediation=[
        "Use: orchestrator.save_artifact('manifest', updated_data)",
        "Or check current state: cat manifest.json | jq .",
        "If stuck, ask operator: 'How do I update manifest?'",
    ],
    example_good="orchestrator.save_artifact('manifest', {'phase': 'CODING'})",
    example_bad="echo '{}' > manifest.json",
    learn_more="docs/architecture/ARTIFACT_REGISTRY.md"
)
```

**Test Coverage:**
```python
def test_kernel_error_is_haiku_readable():
    """Error message must be understandable by Haiku-level agent."""
    with pytest.raises(KernelViolationError) as exc:
        orchestrator._kernel_check_save_artifact("manifest.json")

    error_msg = str(exc.value)

    # Must have all required sections
    assert "🚫 BLOCKED:" in error_msg
    assert "WHY:" in error_msg
    assert "WHAT TO DO INSTEAD:" in error_msg
    assert "EXAMPLE:" in error_msg
    assert "✅" in error_msg  # Good example
    assert "❌" in error_msg  # Bad example

    # Must be concise (< 500 chars)
    assert len(error_msg) < 500

    # Must have numbered steps
    assert "1." in error_msg

    # Must have working example (copy-pasteable)
    assert "orchestrator.save_artifact" in error_msg
```

**Deliverables:**
- Updated `KernelViolationError` class (40 LOC)
- Refactor all 3 existing kernel checks to use new format
- 3+ tests validating error message structure

---

### Phase 4: MOTD Critical Alerts (Week 3)

**Problem:** MOTD is 15+ lines, Haiku might miss critical alerts.

**Solution:** Add "CRITICAL ALERTS" section at top, limit to 3 most important items.

**New MOTD Structure:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 CRITICAL ALERTS (READ THIS FIRST!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ❌ LINTING FAILED - Run: uv run ruff check . --fix
  ⚠️  DIRTY GIT - 3 uncommitted files - Run: git status
  ❌ TESTS FAILING - 5 tests failed - Run: uv run pytest

✅ System Health (Details)
  Git: ⚠️ Dirty (3 uncommitted files)
  Linting: ❌ 12 errors
  Tests: ❌ 102/107 passed
  System Integrity: ✅ Verified

📬 Session Handoff: From VIBE_ALIGNER
  ✅ Completed: Feature specification and scope negotiation
  📋 TODOs (3 remaining):
    1. Select core modules from feature_spec.json
    2. Design extension modules for complex features
    3. Create architecture diagram

⚡ Quick Commands
  ./bin/show-context.sh          # Full session context
  ./bin/pre-push-check.sh        # Run all checks before push
  ./bin/update-system-status.sh  # Refresh system status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Implementation:**
```python
# In vibe-cli

def _get_critical_alerts(system_status: dict) -> list[str]:
    """
    Extract top 3 critical alerts (max) that agent MUST see.

    Priority:
    1. System integrity failures (CRITICAL)
    2. Linting errors (blocks commits)
    3. Test failures (indicates broken code)
    4. Dirty git (warns before state transitions)
    """
    alerts = []

    # Check system integrity (highest priority)
    if not system_status.get("system_integrity", {}).get("verified", True):
        alerts.append("❌ SYSTEM INTEGRITY FAILED - Run: python scripts/verify-system-integrity.py")

    # Check linting (blocks commits)
    linting = system_status.get("linting", {})
    if linting.get("status") == "failed":
        error_count = linting.get("error_count", 0)
        alerts.append(f"❌ LINTING FAILED ({error_count} errors) - Run: uv run ruff check . --fix")

    # Check tests (indicates broken code)
    tests = system_status.get("tests", {})
    if tests.get("status") == "failed":
        failed_count = tests.get("failed", 0)
        alerts.append(f"❌ TESTS FAILING ({failed_count} failed) - Run: uv run pytest")

    # Check git (warns before operations)
    git = system_status.get("git", {})
    if git.get("status") == "dirty":
        file_count = len(git.get("uncommitted_files", []))
        alerts.append(f"⚠️  DIRTY GIT ({file_count} files) - Run: git status")

    # Return max 3 alerts (most critical)
    return alerts[:3]

def display_motd():
    """Display MOTD with critical alerts highlighted."""
    system_status = _get_system_status()
    critical_alerts = _get_critical_alerts(system_status)

    print("━" * 80)

    # Critical alerts section (ALWAYS SHOWN FIRST)
    if critical_alerts:
        print("🚨 CRITICAL ALERTS (READ THIS FIRST!)")
        print("━" * 80)
        for alert in critical_alerts:
            print(f"  {alert}")
        print()
    else:
        print("✅ No critical alerts - system healthy")
        print("━" * 80)

    # Rest of MOTD (collapsed if no alerts)
    if not critical_alerts:
        print("\n✅ System Health")
        # ... abbreviated version
    else:
        # ... full version (agent needs details to fix issues)
```

**Test Coverage:**
```python
def test_critical_alerts_shown_first():
    """Critical alerts MUST appear before any other MOTD content."""
    output = get_motd_output()
    lines = output.split("\n")

    # First non-empty line after separator must be critical alerts or "No critical alerts"
    assert "CRITICAL ALERTS" in lines[1] or "No critical alerts" in lines[1]

def test_critical_alerts_limited_to_three():
    """Never show more than 3 alerts (prevent overload)."""
    # Create system with 10 issues
    system_status = {
        "linting": {"status": "failed", "error_count": 50},
        "tests": {"status": "failed", "failed": 10},
        "git": {"status": "dirty", "uncommitted_files": ["a", "b", "c"]},
        # ... more issues
    }

    alerts = _get_critical_alerts(system_status)
    assert len(alerts) <= 3

def test_alerts_prioritize_by_severity():
    """System integrity > Linting > Tests > Git."""
    system_status = {
        "system_integrity": {"verified": False},  # Highest priority
        "linting": {"status": "failed"},
        "tests": {"status": "failed"},
        "git": {"status": "dirty"},
    }

    alerts = _get_critical_alerts(system_status)
    assert "SYSTEM INTEGRITY" in alerts[0]  # First alert
```

**Deliverables:**
- `_get_critical_alerts()` function (40 LOC)
- Updated `display_motd()` to highlight alerts (20 LOC)
- 5+ tests validating alert prioritization and display

---

### Phase 5: Recovery Playbooks (Week 3)

**Problem:** When kernel blocks operation, agent doesn't know how to recover.

**Solution:** Track violation attempts, escalate on repeated failures.

**Implementation:**
```python
# In agency_os/00_system/orchestrator/core_orchestrator.py

class CoreOrchestrator:
    def __init__(self, ...):
        # ... existing code
        self._kernel_violations: dict[str, int] = {}  # Track violation counts

    def _record_kernel_violation(self, violation_type: str) -> int:
        """
        Record kernel violation attempt, return count.

        Returns:
            Number of times this violation has occurred (1-indexed)
        """
        self._kernel_violations[violation_type] = \
            self._kernel_violations.get(violation_type, 0) + 1
        return self._kernel_violations[violation_type]

    def _kernel_check_save_artifact(self, artifact_name: str) -> None:
        """Kernel check with escalation on repeated violations."""
        if artifact_name in self.CRITICAL_ARTIFACTS:
            attempt_count = self._record_kernel_violation(f"overwrite_{artifact_name}")

            # Escalate error message based on attempts
            if attempt_count == 1:
                # First attempt: Helpful error
                raise KernelViolationError(
                    operation=f"You tried to overwrite {artifact_name}",
                    why="This file is protected to prevent accidental data loss.",
                    remediation=[
                        f"Use: orchestrator.save_artifact('{artifact_name}', data)",
                        f"Or check current: cat {artifact_name} | jq .",
                    ],
                    example_good=f"orchestrator.save_artifact('{artifact_name}', new_data)",
                    example_bad=f"echo '{{}}' > {artifact_name}",
                )
            elif attempt_count == 2:
                # Second attempt: More explicit
                raise KernelViolationError(
                    operation=f"SECOND ATTEMPT to overwrite {artifact_name}",
                    why="The previous error was not just a warning - this operation is BLOCKED.",
                    remediation=[
                        "STOP trying to overwrite this file directly",
                        f"READ THE ERROR: Use orchestrator.save_artifact('{artifact_name}', data)",
                        "If you don't understand, ask operator: 'How do I update manifest?'",
                    ],
                    example_good=f"orchestrator.save_artifact('{artifact_name}', new_data)",
                    example_bad=f"ANY direct file write (echo, cat, sed, etc.)",
                )
            else:
                # Third+ attempt: Escalate to operator
                raise KernelViolationError(
                    operation=f"REPEATED VIOLATION ({attempt_count}x) - overwrite {artifact_name}",
                    why="You have tried this operation multiple times. It is BLOCKED by design.",
                    remediation=[
                        "🚨 YOU NEED OPERATOR HELP 🚨",
                        "Ask operator: 'I'm trying to update manifest.json but keep getting blocked. What am I doing wrong?'",
                        "Do NOT retry this operation again",
                        f"For reference: Use orchestrator.save_artifact('{artifact_name}', data)",
                    ],
                    example_good="[Ask operator for help - you're stuck in a loop]",
                    example_bad=f"Trying the same operation for the {attempt_count}th time",
                )
```

**Test Coverage:**
```python
def test_kernel_escalates_on_repeated_violations():
    """Kernel should detect and escalate repeated violation attempts."""
    orchestrator = CoreOrchestrator(...)

    # First attempt - helpful error
    with pytest.raises(KernelViolationError) as exc1:
        orchestrator._kernel_check_save_artifact("manifest.json")
    assert "You tried to overwrite" in str(exc1.value)
    assert "orchestrator.save_artifact" in str(exc1.value)

    # Second attempt - more explicit
    with pytest.raises(KernelViolationError) as exc2:
        orchestrator._kernel_check_save_artifact("manifest.json")
    assert "SECOND ATTEMPT" in str(exc2.value)
    assert "STOP trying" in str(exc2.value)

    # Third attempt - escalate to operator
    with pytest.raises(KernelViolationError) as exc3:
        orchestrator._kernel_check_save_artifact("manifest.json")
    assert "REPEATED VIOLATION" in str(exc3.value)
    assert "YOU NEED OPERATOR HELP" in str(exc3.value)
    assert "Ask operator" in str(exc3.value)

def test_violation_counts_are_per_artifact():
    """Each artifact should have independent violation tracking."""
    orchestrator = CoreOrchestrator(...)

    # Violate manifest.json once
    with pytest.raises(KernelViolationError):
        orchestrator._kernel_check_save_artifact("manifest.json")

    # Violate session_handoff.json - should be first attempt
    with pytest.raises(KernelViolationError) as exc:
        orchestrator._kernel_check_save_artifact("session_handoff.json")
    assert "You tried to overwrite" in str(exc.value)  # Not "SECOND ATTEMPT"
```

**Deliverables:**
- `_record_kernel_violation()` method (10 LOC)
- `_kernel_violations` tracking dict
- Escalation logic in all 3 kernel checks (30 LOC)
- 5+ tests validating escalation behavior

---

### Phase 6: Haiku Simulation Framework (Week 4) - OPTIONAL

**Goal:** Build test harness that simulates Haiku-level reasoning.

**Approach:**
1. Use Haiku API to generate responses to prompts
2. Inject "mistakes" (hallucinations, misinterpretations)
3. Run against vibe-agency
4. Measure: How many mistakes did system prevent?

**Why Optional:**
- Requires Haiku API access
- Expensive to run (many test iterations)
- Phases 1-5 already provide strong coverage

**If Implemented:**
```python
class HaikuSimulator:
    """
    Simulate Haiku agent behavior with realistic mistakes.

    Mistake types:
    - Hallucination: 10% chance to invent file/command
    - Misinterpretation: 15% chance to misread error message
    - Context skip: 20% chance to miss detail in 200+ line prompt
    - Loop behavior: 30% chance to retry same failed operation
    """

    def simulate_task(self, prompt: str, workspace: Path) -> dict:
        # Use real Haiku API
        response = haiku_api.complete(prompt)

        # Inject mistakes based on probabilities
        if random.random() < 0.10:
            response = self._inject_hallucination(response)
        if random.random() < 0.15:
            response = self._inject_misinterpretation(response)

        # Execute against vibe-agency
        result = execute_in_workspace(response, workspace)

        return {
            "succeeded": result.success,
            "blocked_by_kernel": result.kernel_violations,
            "mistakes_prevented": len(result.kernel_violations),
        }
```

---

## 📊 SUCCESS METRICS

| Metric | Current | Target | How to Measure |
|--------|---------|--------|----------------|
| Rogue scenarios protected | 2/19 (10.5%) | 19/19 (100%) | `uv run pytest tests/test_rogue_agent_scenarios.py` |
| Kernel bypass vulnerabilities | 3 known | 0 | Shell command checks implemented |
| Error message clarity | 33% have examples | 100% | All `KernelViolationError` have examples |
| MOTD critical alerts | 0 (buried in text) | 3 max (highlighted) | `_get_critical_alerts()` function |
| Violation escalation | None | 3-tier (help → explicit → operator) | Violation tracking implemented |

---

## 🎯 ACCEPTANCE CRITERIA

**Phase 2 Complete When:**
- [ ] All shell bypass tests pass (3/3)
- [ ] `_kernel_check_shell_command()` implemented
- [ ] No regression in existing tests

**Phase 3 Complete When:**
- [ ] All kernel errors use new format (3/3)
- [ ] Error message structure tests pass (3/3)
- [ ] Manual review: Errors understandable by non-technical user

**Phase 4 Complete When:**
- [ ] MOTD shows max 3 critical alerts at top
- [ ] Alert prioritization tests pass (3/3)
- [ ] Manual review: MOTD scannable in <5 seconds

**Phase 5 Complete When:**
- [ ] Violation tracking implemented
- [ ] Escalation tests pass (5/5)
- [ ] Third violation suggests operator help

**Overall Success:**
- [ ] 19/19 rogue scenario tests passing
- [ ] Manual test: Haiku completes PLANNING workflow
- [ ] Zero regression in existing tests (107+ tests)

---

## 🔗 RELATED WORK

**Builds On:**
- GAD-004: Multi-Layered Quality Enforcement (kernel foundation)
- GAD-005: Runtime Engineering (MOTD, kernel checks)

**Enables:**
- GAD-007: Cost-Efficient Operation (Haiku for simple tasks)
- GAD-008: Autonomous Portfolio Project (Haiku-proof = autonomous-ready)

**Related Docs:**
- `docs/architecture/EXECUTION_MODE_STRATEGY.md` (delegation model)
- `CLAUDE.md` (operational truth - needs simplification)
- `ARCHITECTURE_V2.md` (conceptual model)

---

## 💭 DESIGN NOTES

**Why Focus on Haiku?**
- Haiku represents "lower bound" of agent capability
- If Haiku can operate safely, any agent can
- Cost efficiency unlocks new use cases (continuous operation, batch processing)

**Why Not Just Use Sonnet/Opus?**
- $3-15/MTok vs $0.25/MTok (12-60x cost difference)
- For simple tasks (file copy, linting check), Haiku is sufficient
- Defense-in-depth: don't rely on agent intelligence for safety

**Philosophy:**
- **System should be "idiot-proof"** - even dumb agents can't break it
- **Errors should teach, not just block** - help agent learn correct approach
- **Escalate gracefully** - first help, then explicit, then operator intervention
- **Simplicity beats sophistication** - if Haiku can't understand it, simplify it

---

## 📅 TIMELINE

- **Week 1:** Test harness (COMPLETE)
- **Week 2:** Shell guardrails + error messages (5 days)
- **Week 3:** MOTD alerts + recovery playbooks (5 days)
- **Week 4:** Haiku simulation (optional, 3 days)

**Total Effort:** 10-13 days
**Dependencies:** None (builds on GAD-005)
**Risk:** Low (additive changes, no core rewrites)

---

## 🚀 NEXT STEPS

1. **Review this proposal** with operator
2. **Decide on Phase 6** (Haiku simulation) - worth the effort?
3. **Start Phase 2** (shell guardrails) if approved
4. **Track progress** in CLAUDE.md

**Discussion Points:**
- Should we test with real Haiku API (Phase 6)?
- Are 3 critical alerts enough, or should we allow 5?
- Should violation tracking persist across orchestrator restarts?
- How do we handle agents that don't read error messages at all?

---

**Created:** 2025-11-16
**Author:** Claude Code (Sonnet 4.5)
**Status:** 📋 Awaiting Approval
