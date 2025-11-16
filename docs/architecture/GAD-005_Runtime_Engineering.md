# GAD-005: Runtime Engineering - Self-Regulating Execution Environment

**Status:** 🔲 DRAFT (Pending Review)
**Date:** 2025-11-16
**Authors:** Claude Code (System Architect), Gemini (Co-Architect)
**Supersedes:** N/A
**Related:** GAD-004 (Multi-Layered Quality Enforcement), GAD-003 (File-Based Delegation), ADR-003 (Delegated Execution)

---

## Executive Summary

This document defines **Runtime Engineering** - the strategic evolution from prompt engineering to context engineering to **self-regulating execution**.

**The Problem:** Current system relies on documentation (CLAUDE.md checklists) and external enforcement (GitHub Actions). Agents can still violate constraints, produce inconsistent state, or skip critical steps because the runtime environment doesn't actively prevent mistakes.

**The Solution:** A **Self-Regulating Execution Environment** that enforces correctness at runtime through:

1. **Session Shell (Layer 1)** - Persistent, state-aware REPL that makes context unavoidable
2. **Pre-Action Kernel (Layer 2)** - Internal orchestrator circuit breaker with declarative rules
3. **Integration with Layer 3** - References existing CI/CD validation (GAD-004 Phase 3)

**Impact:** System becomes **impossible to misuse** because violations are prevented at runtime, not documented for agents to remember.

**Timeline:** 3 weeks (Week 1: Session Shell, Week 2: Pre-Action Kernel, Week 3: Integration)

**Risk:** LOW (backward compatible, incremental rollout)

---

## Table of Contents

1. [Context & Problem Statement](#1-context--problem-statement)
2. [Decision: Runtime Engineering](#2-decision-runtime-engineering)
3. [BLUEPRINT: Architectural Design](#3-blueprint-architectural-design)
4. [IMPLEMENTATION: Concrete Code](#4-implementation-concrete-code)
5. [HARNESS: Testing & Verification](#5-harness-testing--verification)
6. [Rollout Plan](#6-rollout-plan)
7. [Success Metrics](#7-success-metrics)
8. [Appendix: Rejected Alternatives](#8-appendix-rejected-alternatives)

---

## 1. Context & Problem Statement

### 1.1. The Strategic Evolution

```
Phase 1: Prompt Engineering (2020-2023)
  Goal: "What should I tell the AI?"
  Tool: Carefully crafted prompts
  Limit: AI forgets between turns

Phase 2: Context Engineering (2023-2024)
  Goal: "What context should I provide?"
  Tool: RAG, knowledge bases, structured data
  Limit: AI doesn't enforce constraints

Phase 3: Runtime Engineering (2024-2025)  ← WE ARE HERE
  Goal: "How does the system self-regulate?"
  Tool: Active runtime enforcement
  Result: System prevents mistakes during execution
```

### 1.2. Current State: Passive Documentation

**What We Have (GAD-004 Complete):**
- ✅ **Layer 1:** Session-scoped checks (`bin/pre-push-check.sh`, `.system_status.json`)
- ✅ **Layer 2:** Workflow-scoped quality gates (manifest recording, AUDITOR blocking)
- ✅ **Layer 3:** Deployment-scoped validation (E2E tests in CI/CD)

**What's Missing:**
- ❌ Agents can skip Layer 1 checks (no enforcement, just scripts)
- ❌ Orchestrator has no internal self-checks (relies on external quality gates)
- ❌ Context is passive (agents must run `./bin/show-context.sh` manually)

**The Gap:** System provides tools for correctness but doesn't **force** their use.

### 1.3. The Fundamental Problem

**Current Workflow (Manual Vigilance Required):**
```
Agent starts work
  → Must remember to run ./bin/show-context.sh
  → Must remember to check .system_status.json
  → Must remember to run ./bin/pre-push-check.sh
  → Must remember to read session handoff
  → [If they forget any step: silent failure]
```

**Desired Workflow (Automatic Enforcement):**
```
Agent runs: vibe-cli
  → Session Shell auto-boots
  → System status auto-displayed (unavoidable)
  → Session handoff auto-shown (unavoidable)
  → Quality checks auto-enforced before mutations
  → [Impossible to skip critical steps]
```

**Core Insight:** Documentation-driven correctness scales poorly. Runtime enforcement scales infinitely.

---

## 2. Decision: Runtime Engineering

### 2.1. What We're Building

**GAD-005 Decision:** Implement a **Self-Regulating Execution Environment** via two new runtime components:

1. **Session Shell** (Agent-facing)
   - Transform `vibe-cli` from one-shot command → persistent REPL
   - Auto-boot system checks (health validation)
   - Ambient awareness (state always visible in prompt)
   - "Login screen" with synthesized context

2. **Pre-Action Kernel** (Orchestrator-internal)
   - Circuit breaker before all state mutations
   - Declarative rule engine (`kernel_rules.yaml`)
   - Self-checks before: artifact saves, state transitions, git operations
   - Fail-fast with actionable error messages

### 2.2. Relationship to Existing Work

**GAD-005 is NOT replacing GAD-004.** It's the **runtime implementation layer** that makes GAD-004's 3-layer model **self-enforcing**.

| Layer | GAD-004 (Strategy) | GAD-005 (Runtime Implementation) |
|-------|-------------------|----------------------------------|
| **Layer 1** | Session-scoped checks (scripts) | **Session Shell** (persistent REPL) |
| **Layer 2** | Workflow-scoped gates (quality gates) | **Pre-Action Kernel** (internal circuit breaker) |
| **Layer 3** | Deployment-scoped validation (CI/CD) | *(Already implemented in GAD-004 Phase 3)* |

**Analogy:**
- GAD-004 = "Here are the rules" (policy document)
- GAD-005 = "Here's how the system enforces the rules itself" (enforcement engine)

### 2.3. Design Principles

1. **Unavoidable by Design** - Critical context cannot be skipped (shown at boot)
2. **Fail-Fast with Guidance** - Errors block execution but provide fix instructions
3. **Declarative Configuration** - Rules live in YAML, not Python code
4. **Backward Compatible** - Existing workflows continue to work
5. **Observable Enforcement** - All checks logged for auditability

---

## 3. BLUEPRINT: Architectural Design

### 3.1. Component A: Session Shell

#### 3.1.1. Current State (vibe-cli as one-shot tool)

```bash
# Current behavior
$ vibe-cli run project-name
[Executes task]
[Exits]

# Problems:
# - No health checks
# - No state visibility
# - Agent must manually run show-context.sh
# - Easy to miss critical information
```

#### 3.1.2. Target State (vibe-cli as persistent REPL)

```bash
# New behavior
$ vibe-cli
[BOOT SEQUENCE]
  1. Running system health checks...
     ✅ Git working directory: clean
     ✅ Tests: passing
     ✅ Linting: passing
     ⚠️  Session handoff: exists (from previous agent)

  2. Loading session context...
     Project: prabhupad_os
     Phase: CODING
     Last commit: abc123 "feat: add authentication"

[MOTD - MESSAGE OF THE DAY]
  ════════════════════════════════════════════════════════
  📋 SESSION HANDOFF (from GENESIS_BLUEPRINT)

  Completed:
    ✅ Core module architecture defined
    ✅ Extension modules scoped

  Your TODOs:
    → 1. Implement authentication module (core_modules/auth.py)
    → 2. Write unit tests (tests/test_auth.py)
    → 3. Update feature_spec.json with implementation status

  ════════════════════════════════════════════════════════

[INTERACTIVE PROMPT]
(prabhupad_os | CODING | ✅ clean) ➜ _

# Commands available:
#   run <task>        - Execute a workflow task
#   status            - Show system status
#   handoff           - Show session handoff
#   exit              - Exit session shell
```

#### 3.1.3. Architecture

**File:** `vibe-cli` (refactored)

```python
class SessionShell:
    """Persistent REPL with ambient awareness"""

    def __init__(self):
        self.context = self._load_session_context()
        self.status = self._run_health_checks()

    def _run_health_checks(self) -> Dict:
        """Boot-up sequence: validate system health"""
        # Run update-system-status.sh
        # Parse .system_status.json
        # Return dict of health status
        pass

    def _load_session_context(self) -> Dict:
        """Load all context files"""
        # Read .session_handoff.json
        # Read project_manifest.json
        # Read current git state
        pass

    def _render_motd(self) -> str:
        """Render Message of the Day"""
        # Synthesize critical info into single screen
        # Prioritize: session handoff TODOs, test failures, uncommitted changes
        pass

    def _get_prompt(self) -> str:
        """Dynamic prompt showing critical state"""
        project = self.context.get('project_name', 'unknown')
        phase = self.context.get('phase', 'unknown')
        clean = '✅' if self.status['git']['clean'] else '⚠️'
        return f"({project} | {phase} | {clean}) ➜ "

    def run_repl(self):
        """Main REPL loop"""
        print(self._render_motd())

        while True:
            try:
                user_input = input(self._get_prompt())
                self._handle_command(user_input)
            except KeyboardInterrupt:
                break
```

**Key Features:**

1. **Auto-Boot Health Checks** - Runs `./bin/update-system-status.sh` on startup
2. **Synthesized MOTD** - Shows session handoff + system status in one view
3. **Dynamic Prompt** - Always displays: project, phase, git status
4. **Persistent Session** - Doesn't exit until user types `exit`

---

### 3.2. Component B: Pre-Action Kernel

#### 3.2.1. Current State (No Internal Checks)

```python
# Current orchestrator behavior
def save_artifact(self, artifact_name: str, content: str):
    """Save artifact to workspace"""
    # Problem: No checks before mutation!
    path = self.workspace / artifact_name
    path.write_text(content)  # ← Can overwrite critical files
```

#### 3.2.2. Target State (Circuit Breaker)

```python
# New orchestrator behavior
def save_artifact(self, artifact_name: str, content: str):
    """Save artifact to workspace"""
    # Pre-action kernel check (MANDATORY)
    self._pre_action_check(
        action="save_artifact",
        params={"artifact_name": artifact_name}
    )

    # Now safe to proceed
    path = self.workspace / artifact_name
    path.write_text(content)
```

#### 3.2.3. Kernel Rules Engine (Declarative)

**File:** `agency_os/00_system/orchestrator/kernel_rules.yaml`

```yaml
# Declarative rules for Pre-Action Kernel
# Updated without code changes

rules:
  save_artifact:
    description: "Validate artifact save operations"
    checks:
      - name: "no_overwrite_critical_files"
        condition: "artifact_name not in ['project_manifest.json', '.session_handoff.json']"
        severity: "critical"
        blocking: true
        message: "Cannot overwrite critical file: {artifact_name}"
        remediation: "Use update_manifest() or create_session_handoff() instead"

      - name: "git_working_directory_clean"
        condition: "git.status.clean == true"
        severity: "high"
        blocking: false  # Warning only
        message: "Working directory has uncommitted changes"
        remediation: "Commit or stash changes before generating new artifacts"

  transition_state:
    description: "Validate state transitions"
    checks:
      - name: "quality_gates_passed"
        condition: "manifest.status.qualityGates[transition_name].status == 'PASS'"
        severity: "critical"
        blocking: true
        message: "Quality gates failed for transition: {transition_name}"
        remediation: "Fix quality gate failures before transitioning"

      - name: "required_artifacts_exist"
        condition: "all(artifact in manifest.artifacts for artifact in transition.required_artifacts)"
        severity: "critical"
        blocking: true
        message: "Missing required artifacts: {missing_artifacts}"
        remediation: "Generate missing artifacts before transitioning"

  git_commit:
    description: "Validate git commit operations"
    checks:
      - name: "linting_passed"
        condition: "system_status.linting.status == 'passing'"
        severity: "critical"
        blocking: true
        message: "Linting errors detected ({system_status.linting.errors_count} errors)"
        remediation: "Run: uv run ruff check . --fix"

      - name: "tests_passing"
        condition: "system_status.tests.planning_workflow == 'passing'"
        severity: "high"
        blocking: true
        message: "Tests failing"
        remediation: "Fix test failures before committing"
```

#### 3.2.4. Kernel Implementation

**File:** `agency_os/00_system/orchestrator/pre_action_kernel.py` (new)

```python
import yaml
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class KernelCheckResult:
    """Result of a single kernel check"""
    check_name: str
    passed: bool
    severity: str
    blocking: bool
    message: str
    remediation: str

class PreActionKernel:
    """
    Internal circuit breaker for CoreOrchestrator.

    Implements declarative rule engine for runtime self-checks.
    Rules defined in kernel_rules.yaml.
    """

    def __init__(self, rules_path: Path):
        self.rules_path = rules_path
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        """Load kernel rules from YAML"""
        with open(self.rules_path) as f:
            return yaml.safe_load(f)

    def check(self, action: str, context: Dict[str, Any]) -> List[KernelCheckResult]:
        """
        Run pre-action checks for given action.

        Args:
            action: Action name (e.g., 'save_artifact')
            context: Runtime context (system_status, manifest, params)

        Returns:
            List of check results

        Raises:
            KernelViolationError: If blocking check fails
        """
        if action not in self.rules['rules']:
            # No rules defined for this action
            return []

        action_rules = self.rules['rules'][action]
        results = []

        for check in action_rules['checks']:
            result = self._evaluate_check(check, context)
            results.append(result)

            # If blocking check failed, raise immediately
            if not result.passed and result.blocking:
                raise KernelViolationError(
                    f"Kernel check '{result.check_name}' FAILED\n"
                    f"Severity: {result.severity}\n"
                    f"Message: {result.message}\n"
                    f"Remediation: {result.remediation}"
                )

        return results

    def _evaluate_check(self, check: Dict, context: Dict) -> KernelCheckResult:
        """
        Evaluate a single check condition.

        Uses simple expression evaluation (safe subset).
        """
        try:
            # Evaluate condition (simplified - use safe eval or expression parser)
            condition_result = self._safe_eval(check['condition'], context)

            return KernelCheckResult(
                check_name=check['name'],
                passed=condition_result,
                severity=check['severity'],
                blocking=check['blocking'],
                message=check['message'].format(**context.get('params', {})),
                remediation=check['remediation']
            )

        except Exception as e:
            # If evaluation fails, treat as check failure
            return KernelCheckResult(
                check_name=check['name'],
                passed=False,
                severity='critical',
                blocking=True,
                message=f"Kernel check evaluation failed: {e}",
                remediation="Contact system administrator"
            )

    def _safe_eval(self, condition: str, context: Dict) -> bool:
        """
        Safely evaluate condition expression.

        TODO: Implement safe expression evaluator (not Python eval!)
        Consider using: simpleeval library or custom parser
        """
        # Placeholder - implement safe expression evaluation
        # For MVP: can use simple string matching or jq-like syntax
        pass


class KernelViolationError(Exception):
    """Raised when blocking kernel check fails"""
    pass
```

#### 3.2.5. Integration with CoreOrchestrator

**File:** `agency_os/00_system/orchestrator/core_orchestrator.py`

**Add initialization:**

```python
class CoreOrchestrator:
    def __init__(self, repo_root: Path, execution_mode: str = "delegated"):
        # ... existing code ...

        # NEW: Initialize Pre-Action Kernel
        kernel_rules_path = repo_root / "agency_os/00_system/orchestrator/kernel_rules.yaml"
        self.kernel = PreActionKernel(kernel_rules_path)
```

**Add to all mutation methods:**

```python
def save_artifact(self, manifest: ProjectManifest, artifact_name: str, content: str) -> None:
    """Save artifact to workspace"""

    # PRE-ACTION KERNEL CHECK (mandatory first line)
    self.kernel.check(
        action="save_artifact",
        context={
            "params": {"artifact_name": artifact_name},
            "manifest": manifest.to_dict(),
            "system_status": self._get_system_status(),
            "git": self._get_git_status()
        }
    )

    # Now safe to proceed
    artifact_path = self.workspace_root / artifact_name
    artifact_path.write_text(content)
    logger.info(f"✓ Saved artifact: {artifact_name}")

def transition_state(self, manifest: ProjectManifest, transition_name: str) -> None:
    """Transition project to new state"""

    # PRE-ACTION KERNEL CHECK
    self.kernel.check(
        action="transition_state",
        context={
            "params": {"transition_name": transition_name},
            "manifest": manifest.to_dict(),
            "transition": self._get_transition_config(transition_name)
        }
    )

    # Now safe to proceed
    # ... existing transition logic ...
```

---

### 3.3. Integration: How Components Work Together

```
┌─────────────────────────────────────────────────────────┐
│ AGENT (Claude Code)                                      │
│                                                           │
│  $ vibe-cli                                              │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ LAYER 1: Session Shell (GAD-005 Component A)            │
│━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  Boot Sequence:                                          │
│    1. Run health checks (./bin/update-system-status.sh) │
│    2. Load session context (.session_handoff.json)      │
│    3. Display MOTD (synthesized critical info)          │
│                                                           │
│  Interactive REPL:                                       │
│    (project | phase | ✅) ➜ run coding_task            │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ LAYER 2: Pre-Action Kernel (GAD-005 Component B)       │
│━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  Before every orchestrator action:                       │
│    kernel.check("save_artifact", context)               │
│    kernel.check("transition_state", context)            │
│    kernel.check("git_commit", context)                  │
│                                                           │
│  Rules Engine (kernel_rules.yaml):                      │
│    - No overwrite critical files                         │
│    - Git working directory clean                         │
│    - Quality gates passed                                │
│    - Required artifacts exist                            │
│    - Linting passed                                      │
│    - Tests passing                                       │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ LAYER 3: CI/CD Validation (GAD-004 Phase 3)            │
│━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  Post-merge checks (already implemented):                │
│    - E2E tests (tests/e2e/)                             │
│    - Performance tests (tests/performance/)             │
│    - GitHub Actions workflow                             │
└─────────────────────────────────────────────────────────┘

Result: 3-layer defense in depth, fully self-regulating
```

**Key Insight:** GAD-005 doesn't replace GAD-004. It makes Layers 1 & 2 **active enforcers** instead of passive documentation.

---

## 4. IMPLEMENTATION: Concrete Code

### 4.1. Phase 1: Session Shell (Week 1)

#### 4.1.1. Refactor vibe-cli

**File:** `vibe-cli` (lines 1-50, add new imports)

```python
#!/usr/bin/env python3
"""
vibe-cli - Session Shell for VIBE Agency

GAD-005: Runtime Engineering - Self-Regulating Execution Environment
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

class SessionShell:
    """Persistent REPL with ambient awareness"""
    # ... (full implementation as shown in Section 3.1.3)
```

#### 4.1.2. Health Check Integration

**File:** `vibe-cli` (add method)

```python
def _run_health_checks(self) -> Dict[str, Any]:
    """
    Run system health checks on boot.

    Returns:
        Dict with health status
    """
    # Run update-system-status.sh
    repo_root = Path(__file__).parent
    status_script = repo_root / "bin/update-system-status.sh"

    try:
        subprocess.run([str(status_script)], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: System status update failed: {e}")

    # Load .system_status.json
    status_file = repo_root / ".system_status.json"
    if status_file.exists():
        with open(status_file) as f:
            return json.load(f)
    else:
        return {"error": "System status file not found"}
```

#### 4.1.3. MOTD Renderer

**File:** `vibe-cli` (add method)

```python
def _render_motd(self) -> str:
    """
    Render Message of the Day.

    Synthesizes:
    - Session handoff (if exists)
    - System health status
    - Git status
    - Next priority task
    """
    lines = []
    lines.append("═" * 60)
    lines.append("🚀 VIBE AGENCY - RUNTIME ENGINEERING SESSION")
    lines.append("═" * 60)
    lines.append("")

    # Health Status
    lines.append("📊 SYSTEM HEALTH")
    lines.append(f"  Git: {self._format_git_status()}")
    lines.append(f"  Linting: {self._format_linting_status()}")
    lines.append(f"  Tests: {self._format_test_status()}")
    lines.append("")

    # Session Handoff
    if self._has_session_handoff():
        handoff = self._load_session_handoff()
        lines.append("📋 SESSION HANDOFF")
        lines.append(f"  From: {handoff.get('from_agent', 'Unknown')}")
        lines.append("")
        lines.append("  Your TODOs:")
        for todo in handoff.get('next_session_todos', [])[:3]:  # Top 3
            lines.append(f"    → {todo}")
        lines.append("")

    # Quick Commands
    lines.append("💡 QUICK COMMANDS")
    lines.append("  run <task>   - Execute workflow task")
    lines.append("  status       - Show full system status")
    lines.append("  handoff      - Show complete session handoff")
    lines.append("  exit         - Exit session shell")
    lines.append("")
    lines.append("═" * 60)

    return "\n".join(lines)
```

#### 4.1.4. Update main() entry point

**File:** `vibe-cli` (modify main function)

```python
def main():
    """Main entry point"""

    # If no arguments, start Session Shell
    if len(sys.argv) == 1:
        shell = SessionShell()
        shell.run_repl()
        return

    # Otherwise, fall back to legacy one-shot mode
    # ... existing code ...
```

---

### 4.2. Phase 2: Pre-Action Kernel (Week 2)

#### 4.2.1. Create kernel_rules.yaml

**File:** `agency_os/00_system/orchestrator/kernel_rules.yaml` (new file)

```yaml
# Pre-Action Kernel Rules
# GAD-005: Runtime Engineering
# Version: 1.0

rules:
  # Full rules as shown in Section 3.2.3
  save_artifact:
    # ... (copy from Section 3.2.3)

  transition_state:
    # ... (copy from Section 3.2.3)

  git_commit:
    # ... (copy from Section 3.2.3)
```

#### 4.2.2. Implement PreActionKernel

**File:** `agency_os/00_system/orchestrator/pre_action_kernel.py` (new file)

```python
# Full implementation as shown in Section 3.2.4
```

#### 4.2.3. Integrate with CoreOrchestrator

**File:** `agency_os/00_system/orchestrator/core_orchestrator.py`

**Add import (line 10):**
```python
from .pre_action_kernel import PreActionKernel, KernelViolationError
```

**Modify __init__ (after line 150):**
```python
# Initialize Pre-Action Kernel (GAD-005)
kernel_rules_path = repo_root / "agency_os/00_system/orchestrator/kernel_rules.yaml"
if kernel_rules_path.exists():
    self.kernel = PreActionKernel(kernel_rules_path)
    logger.info("✓ Pre-Action Kernel initialized")
else:
    self.kernel = None
    logger.warning("⚠️  Pre-Action Kernel disabled (kernel_rules.yaml not found)")
```

**Modify save_artifact (before line 200):**
```python
def save_artifact(self, manifest: ProjectManifest, artifact_name: str, content: str) -> None:
    """Save artifact to workspace"""

    # PRE-ACTION KERNEL CHECK (GAD-005)
    if self.kernel:
        try:
            self.kernel.check(
                action="save_artifact",
                context={
                    "params": {"artifact_name": artifact_name},
                    "manifest": manifest.to_dict() if hasattr(manifest, 'to_dict') else manifest,
                    "system_status": self._get_system_status(),
                    "git": self._get_git_status()
                }
            )
        except KernelViolationError as e:
            logger.error(f"❌ Kernel check failed: {e}")
            raise

    # Existing code...
```

---

### 4.3. Phase 3: Integration & Polish (Week 3)

#### 4.3.1. Add helper methods to CoreOrchestrator

**File:** `agency_os/00_system/orchestrator/core_orchestrator.py`

```python
def _get_system_status(self) -> Dict[str, Any]:
    """
    Get current system status.

    Returns:
        Parsed .system_status.json
    """
    status_file = self.repo_root / ".system_status.json"
    if status_file.exists():
        with open(status_file) as f:
            return json.load(f)
    return {}

def _get_git_status(self) -> Dict[str, Any]:
    """
    Get git working directory status.

    Returns:
        Dict with git state
    """
    try:
        # Check if working directory is clean
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=self.repo_root
        )
        clean = len(result.stdout.strip()) == 0

        return {
            "status": {"clean": clean},
            "uncommitted_changes": result.stdout.strip().split("\n") if not clean else []
        }
    except Exception as e:
        return {"status": {"clean": False}, "error": str(e)}
```

---

## 5. HARNESS: Testing & Verification

### 5.1. Session Shell Tests

#### 5.1.1. Manual Verification

```bash
# Test 1: Boot sequence
./vibe-cli
# Expected:
#   - System health checks run
#   - MOTD displayed
#   - Interactive prompt shown

# Test 2: Health check detection
# Create linting error
echo "import unused" >> temp_test.py

./vibe-cli
# Expected:
#   - MOTD shows "Linting: ❌ Failing (1 error)"

# Cleanup
rm temp_test.py
```

#### 5.1.2. Automated Test

**File:** `tests/test_session_shell.py` (new)

```python
#!/usr/bin/env python3
"""
Tests for Session Shell (GAD-005 Component A)
"""
import subprocess
from pathlib import Path

def test_session_shell_boots():
    """Verify Session Shell can start without errors"""
    result = subprocess.run(
        ["./vibe-cli"],
        input="exit\n",  # Send exit command
        capture_output=True,
        text=True,
        timeout=5
    )

    # Should exit cleanly
    assert result.returncode == 0

    # Should display MOTD
    assert "VIBE AGENCY" in result.stdout
    assert "SYSTEM HEALTH" in result.stdout

def test_session_shell_shows_handoff():
    """Verify Session Shell displays session handoff if exists"""
    # Ensure handoff exists
    handoff_file = Path(".session_handoff.json")
    assert handoff_file.exists(), "Session handoff file missing"

    result = subprocess.run(
        ["./vibe-cli"],
        input="exit\n",
        capture_output=True,
        text=True,
        timeout=5
    )

    # Should show handoff section
    assert "SESSION HANDOFF" in result.stdout

if __name__ == "__main__":
    try:
        test_session_shell_boots()
        print("✅ test_session_shell_boots")

        test_session_shell_shows_handoff()
        print("✅ test_session_shell_shows_handoff")

        print("\n✅ ALL SESSION SHELL TESTS PASSED")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
```

---

### 5.2. Pre-Action Kernel Tests

#### 5.2.1. Unit Tests

**File:** `tests/test_pre_action_kernel.py` (new)

```python
#!/usr/bin/env python3
"""
Tests for Pre-Action Kernel (GAD-005 Component B)
"""
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agency_os/00_system/orchestrator"))

from pre_action_kernel import PreActionKernel, KernelViolationError

def test_kernel_loads_rules():
    """Verify kernel can load rules from YAML"""
    kernel = PreActionKernel(
        Path("agency_os/00_system/orchestrator/kernel_rules.yaml")
    )

    assert kernel.rules is not None
    assert 'rules' in kernel.rules
    assert 'save_artifact' in kernel.rules['rules']

    print("✅ Kernel loaded rules successfully")

def test_kernel_blocks_critical_file_overwrite():
    """Verify kernel prevents overwriting critical files"""
    kernel = PreActionKernel(
        Path("agency_os/00_system/orchestrator/kernel_rules.yaml")
    )

    context = {
        "params": {"artifact_name": "project_manifest.json"},
        "manifest": {},
        "system_status": {},
        "git": {"status": {"clean": True}}
    }

    # Should raise KernelViolationError
    try:
        kernel.check("save_artifact", context)
        assert False, "Should have raised KernelViolationError"
    except KernelViolationError as e:
        assert "Cannot overwrite critical file" in str(e)
        print("✅ Kernel correctly blocked critical file overwrite")

def test_kernel_allows_safe_operations():
    """Verify kernel allows safe operations"""
    kernel = PreActionKernel(
        Path("agency_os/00_system/orchestrator/kernel_rules.yaml")
    )

    context = {
        "params": {"artifact_name": "feature_spec.json"},  # Safe file
        "manifest": {},
        "system_status": {},
        "git": {"status": {"clean": True}}
    }

    # Should not raise
    results = kernel.check("save_artifact", context)
    assert results is not None
    print("✅ Kernel allowed safe operation")

if __name__ == "__main__":
    try:
        test_kernel_loads_rules()
        test_kernel_blocks_critical_file_overwrite()
        test_kernel_allows_safe_operations()

        print("\n✅ ALL KERNEL TESTS PASSED")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
```

---

### 5.3. Integration Test

**File:** `tests/test_runtime_engineering_integration.py` (new)

```python
#!/usr/bin/env python3
"""
Integration test for GAD-005: Runtime Engineering
Tests both Session Shell + Pre-Action Kernel working together
"""
import subprocess
import json
from pathlib import Path

def test_complete_runtime_enforcement():
    """
    End-to-end test: Session Shell + Pre-Action Kernel
    """
    print("🧪 Testing Runtime Engineering integration...")

    # COMPONENT A: Session Shell
    print("\n1️⃣  Testing Session Shell...")

    result = subprocess.run(
        ["./vibe-cli"],
        input="exit\n",
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0, "Session Shell failed to start"
    assert "SYSTEM HEALTH" in result.stdout, "MOTD not displayed"
    print("   ✅ Session Shell working")

    # COMPONENT B: Pre-Action Kernel
    print("\n2️⃣  Testing Pre-Action Kernel...")

    # Import kernel
    import sys
    sys.path.insert(0, "agency_os/00_system/orchestrator")
    from pre_action_kernel import PreActionKernel

    kernel = PreActionKernel(
        Path("agency_os/00_system/orchestrator/kernel_rules.yaml")
    )
    assert kernel.rules is not None, "Kernel rules not loaded"
    print("   ✅ Pre-Action Kernel working")

    # INTEGRATION: Both components integrated
    print("\n3️⃣  Testing integration...")

    # Verify both components can access .system_status.json
    status_file = Path(".system_status.json")
    assert status_file.exists(), "System status file missing"

    with open(status_file) as f:
        status = json.load(f)

    assert "linting" in status, "System status incomplete"
    assert "git" in status, "System status incomplete"
    print("   ✅ Integration working")

    print("\n✅ RUNTIME ENGINEERING INTEGRATION COMPLETE")

if __name__ == "__main__":
    try:
        test_complete_runtime_enforcement()
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
```

---

## 6. Rollout Plan

### 6.1. Week 1: Session Shell Implementation

**Tasks:**
1. Refactor `vibe-cli` with `SessionShell` class
2. Implement boot sequence (health checks)
3. Implement MOTD rendering
4. Implement interactive REPL
5. Write tests (`tests/test_session_shell.py`)
6. Manual testing
7. Update CLAUDE.md with new workflow

**Success Criteria:**
- `./vibe-cli` starts Session Shell
- MOTD displays system health + session handoff
- Interactive prompt works
- Tests pass

---

### 6.2. Week 2: Pre-Action Kernel Implementation

**Tasks:**
1. Create `kernel_rules.yaml`
2. Implement `PreActionKernel` class
3. Add `_safe_eval()` expression evaluator
4. Integrate with `CoreOrchestrator`
5. Add kernel checks to mutation methods
6. Write tests (`tests/test_pre_action_kernel.py`)
7. Manual testing

**Success Criteria:**
- Kernel loads rules from YAML
- Kernel blocks critical violations
- Kernel allows safe operations
- Tests pass

---

### 6.3. Week 3: Integration & Documentation

**Tasks:**
1. Write integration test (`tests/test_runtime_engineering_integration.py`)
2. Create usage guide (`docs/guides/RUNTIME_ENGINEERING_GUIDE.md`)
3. Update CLAUDE.md with verification commands
4. Update session handoff
5. Mark GAD-005 as ✅ Complete

**Success Criteria:**
- All tests pass (unit + integration)
- Documentation complete
- System battle-tested for 1+ week
- No regressions

---

## 7. Success Metrics

### 7.1. Session Shell Metrics

**Effectiveness:**
- Agent session start rate: **Target 100% via Session Shell** (not manual commands)
- Context visibility: **Target agents see critical info in <5 seconds** (MOTD)
- Handoff compliance: **Target 95%+ agents read session handoff** (shown at boot)

**Monitoring:**
```bash
# Count Session Shell usage (from logs)
grep "Session Shell started" logs/*.log | wc -l
```

---

### 7.2. Pre-Action Kernel Metrics

**Enforcement:**
- Kernel checks executed: **Target 100% of mutation operations**
- Violations blocked: **Target catch 100% of critical violations**
- False positive rate: **Target < 1%**

**Monitoring:**
```bash
# Count kernel checks from orchestrator logs
grep "Kernel check:" logs/orchestrator.log | wc -l

# Count violations blocked
grep "KernelViolationError" logs/orchestrator.log | wc -l
```

---

### 7.3. Integration Metrics

**System Reliability:**
- Incorrect state mutations: **Target 0 incidents/week**
- Agent confusion rate: **Target < 5% sessions require clarification**
- Documentation lookups: **Target 50% reduction** (info now ambient)

**Monitoring:**
```bash
# Incidents (manual tracking)
# Track: "Agent tried to do X but system blocked it correctly"
```

---

## 8. Appendix: Rejected Alternatives

### 8.1. Hardcoded Kernel Rules in Python

**Proposal:** Implement kernel checks as Python if-statements in `CoreOrchestrator`

**Rejection Reasons:**
1. **Not maintainable:** Changing rules requires code changes + redeployment
2. **Not auditable:** Rules hidden in code, not visible in git history
3. **Not flexible:** Can't enable/disable rules without code changes
4. **Violates separation of concerns:** Policy (rules) mixed with mechanism (orchestrator)

**What we chose:** Declarative `kernel_rules.yaml` (policy separated from code)

---

### 8.2. One-Shot vibe-cli with Auto-Displayed Context

**Proposal:** Keep one-shot `vibe-cli` but auto-display context before execution

**Rejection Reasons:**
1. **Scrolls off screen:** Context shown, then buried by output
2. **Easy to ignore:** Agents can skip reading if in a hurry
3. **No ambient awareness:** State not continuously visible during execution
4. **No interactive commands:** Can't run `status` or `handoff` mid-session

**What we chose:** Persistent REPL with dynamic prompt

---

### 8.3. Git Hooks for All Enforcement

**Proposal:** Move all enforcement to git hooks (`.githooks/pre-commit`, etc.)

**Rejection Reasons:**
1. **Setup friction:** Requires `git config core.hooksPath .githooks`
2. **Agent limitations:** Claude Code agents can't run git config
3. **Environment-specific:** Doesn't work in CI/CD consistently
4. **Late enforcement:** Only runs at commit time (too late for runtime errors)

**What we chose:** Session Shell (boot-time) + Pre-Action Kernel (runtime)

---

### 8.4. No Kernel, Only External Quality Gates

**Proposal:** Rely solely on AUDITOR agent for quality enforcement

**Rejection Reasons:**
1. **Wrong layer:** AUDITOR runs at workflow transitions (too late for internal bugs)
2. **External dependency:** If AUDITOR breaks, entire enforcement fails
3. **No fail-fast:** Errors discovered late in execution
4. **Async only:** Doesn't prevent immediate violations

**What we chose:** Internal Pre-Action Kernel + External AUDITOR (defense in depth)

---

## 9. References

- **GAD-004:** Multi-Layered Quality Enforcement (3-layer strategy)
- **GAD-003:** File-Based Delegation (session handoff foundation)
- **ADR-003:** Delegated Execution Architecture (brain-arm model)
- **CLAUDE.md:** Operational truth (verification commands)

---

## 10. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-16 | Claude Code (System Architect), Gemini (Co-Architect) | Initial draft |

---

## 11. Acknowledgments

**Co-Architect:** Gemini (Google)
- Identified critical need for declarative `kernel_rules.yaml`
- Recommended acknowledging Layer 3 context
- Provided design critique for architectural completeness

---

**STATUS: 🔲 DRAFT (Pending Review)**

**Next Steps:**
1. Review GAD-005 with stakeholders
2. Get approval for implementation
3. Begin Week 1: Session Shell implementation
