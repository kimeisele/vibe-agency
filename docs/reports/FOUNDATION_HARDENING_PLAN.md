# FOUNDATION HARDENING PLAN
## Technical Debt Remediation & Infrastructure Stabilization

**Date:** 2025-11-14
**Status:** ACTIVE
**Based On:** NFR Requirements + GRAND_SYSTEM_AUDIT.md + Gemini Analysis

---

## EXECUTIVE SUMMARY

**Problem:** The Vibe Agency system has brilliant architecture and comprehensive knowledge bases, but the Python implementation has fundamental technical gaps that prevent production use.

**Root Cause:** "Vision-Implementation Gap" - excellent design documents but minimal attention to code quality, testing, logging, and tooling.

**Goal:** Stabilize the foundation before building more features.

---

## THE FIVE PROBLEM CATEGORIES

As identified by user + Gemini analysis:

1. **Logische Probleme** - Dataflow issues, state management bugs
2. **Code Sünden** - PEP 8 violations, no error handling, complexity issues
3. **AI Slop** - Inconsistent code style, duplicated logic
4. **Inkonsistenz Probleme** - Config scattered, no standards enforced
5. **Strukturelle Probleme** - CLI is rudimentary, logging is ad-hoc

---

## ACTION ITEMS (Aggregated from NFRs)

### 🔴 CRITICAL (Week 1 - Do First)

#### C-1: Fix the Regression (Core Blocker)
**Source:** ADR-003, GRAND_SYSTEM_AUDIT Rec-001
**Problem:** orchestrator.py makes direct LLM calls (violates Brain-Arm architecture)
**Action:**
- ✅ DONE: Added delegated execution mode to core_orchestrator.py
- ✅ DONE: Fixed VIBE_AUTO_MODE (non-interactive execution)
- ⚠️ TODO: **Test delegated mode end-to-end**
- ⚠️ TODO: Archive legacy orchestrator.py

**Priority:** P0 (Blocks everything)
**Estimate:** 2 hours remaining
**Owner:** Claude Code

---

#### C-2: Run First Real Test
**Source:** GRAND_SYSTEM_AUDIT Rec-001
**Problem:** System has NEVER been tested end-to-end
**Action:**
- ✅ DONE: Created test project (test_password_generator)
- ⚠️ TODO: **Run PLANNING phase in DELEGATED mode** (not autonomous!)
- ⚠️ TODO: Document what breaks
- ⚠️ TODO: Fix critical issues found

**Priority:** P0 (Validates foundation)
**Estimate:** 4 hours
**Owner:** Claude Code

**How to test:**
```bash
# THIS is the correct way (delegated mode, not autonomous!)
# 1. I (Claude Code) start orchestrator as a TOOL
# 2. Orchestrator writes INTELLIGENCE_REQUEST to STDOUT
# 3. I read request, execute it, write INTELLIGENCE_RESPONSE
# 4. Orchestrator continues workflow
```

---

#### C-3: Code Quality Standards
**Source:** NFR_MAINTAINABILITY.yaml (action_items.immediate)

**C-3a: Create .flake8 config**
```ini
# .flake8
[flake8]
max-line-length = 100
ignore = E501  # Handled by black
exclude =
    .git,
    __pycache__,
    docs/,
    build/,
    dist/
```
**Priority:** P1
**Estimate:** 15 minutes

**C-3b: Create .yamllint config**
```yaml
# .yamllint
extends: default
rules:
  line-length:
    max: 120
  indentation:
    spaces: 2
```
**Priority:** P1
**Estimate:** 15 minutes

**C-3c: Add pre-commit hooks**
```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
# Add hooks: black, flake8, yamllint, detect-secrets
```
**Priority:** P1
**Estimate:** 1 hour

---

#### C-4: Logging Strategy
**Source:** NFR_OPERATIONS.yaml (logging section)
**Problem:** No cohesive logging - print() everywhere, no log levels
**Action:**
1. Create centralized logging config
2. Replace all print() with logger.info/warning/error
3. Implement log rotation (30 days)
4. Add context to logs (project_id, phase, agent)

**Priority:** P1
**Estimate:** 3 hours

**Implementation:**
```python
# agency_os/core_system/utils/logging_config.py
import logging
from pathlib import Path

def setup_logging(level='INFO'):
    log_dir = Path.home() / '.vibe_agency' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'vibe_agency.log'),
            logging.StreamHandler()
        ]
    )
```

---

#### C-5: CLI Refactoring
**Source:** Gemini Analysis ("CLI ist kacke")
**Problem:** vibe-cli.py is rudimentary, no proper arg parsing
**Action:**
1. Refactor to use `click` or `argparse` properly
2. Add subcommands: run, status, clean, audit
3. Add --help documentation
4. Add --version flag

**Priority:** P1
**Estimate:** 4 hours

**Example:**
```python
import click

@click.group()
@click.version_option(version='0.5.0')
def cli():
    """Vibe Agency - AI-Powered SDLC Orchestration"""
    pass

@cli.command()
@click.argument('project_id')
@click.option('--mode', type=click.Choice(['delegated', 'autonomous']), default='delegated')
def run(project_id, mode):
    """Run SDLC workflow for a project"""
    ...

if __name__ == '__main__':
    cli()
```

---

### 🟡 HIGH PRIORITY (Week 2)

#### H-1: Test Strategy Implementation
**Source:** NFR_MAINTAINABILITY.yaml (testing_requirements)
**Problem:** 0% end-to-end coverage, no test strategy
**Action:**
1. Set up pytest with coverage (pytest-cov)
2. Add unit tests for critical paths (80% coverage target)
3. Add integration tests (all agent compositions)
4. Add regression tests (one per bug fixed)

**Priority:** P2
**Estimate:** 2 weeks

**Test Pyramid:**
```
      /\
     /E2E\     ← 10% (Full SDLC workflows)
    /------\
   /Integr.\   ← 30% (Agent composition, quality gates)
  /----------\
 /Unit Tests \  ← 60% (Functions, classes, modules)
/--------------\
```

---

#### H-2: Documentation Requirements
**Source:** NFR_MAINTAINABILITY.yaml (documentation_requirements)

**H-2a: Add docstrings to all public functions**
```python
def execute_task(agent_id: str, task_id: str, context: Dict) -> str:
    """
    Compose and execute an atomized task.

    Args:
        agent_id: Agent identifier (e.g., "GENESIS_BLUEPRINT")
        task_id: Task identifier (e.g., "select_core_modules")
        context: Runtime context (project_id, artifacts, etc.)

    Returns:
        Composed prompt string ready for LLM execution

    Raises:
        ValueError: If agent_id not found in AGENT_REGISTRY
        FileNotFoundError: If required files missing
    """
```
**Priority:** P2
**Estimate:** 1 week

**H-2b: Create CONTRIBUTING.md**
**Priority:** P2
**Estimate:** 2 hours

**H-2c: Update README with honest status**
**Priority:** P2
**Estimate:** 1 hour

---

#### H-3: Dependency Management
**Source:** NFR_OPERATIONS.yaml (action_items.immediate)

**Create requirements.txt:**
```
pyyaml>=6.0.1
anthropic>=0.18.0
# Add all dependencies with pinned versions
```
**Priority:** P2
**Estimate:** 1 hour

---

#### H-4: Error Handling Pass
**Source:** Gemini Analysis ("Code Sünden")
**Problem:** Missing try/except blocks, unclear error messages
**Action:**
1. Audit all Python files for error handling
2. Add try/except for file I/O
3. Add try/except for API calls
4. Add custom exceptions (OrchestratorError, etc.)
5. Improve error messages (include context, suggest fixes)

**Priority:** P2
**Estimate:** 1 week

---

### 🟢 MEDIUM PRIORITY (Week 3-4)

#### M-1: Code Complexity Reduction
**Source:** NFR_MAINTAINABILITY.yaml (code_quality)
**Action:**
1. Run radon cc (complexity checker)
2. Refactor functions with complexity > 10
3. Extract repeated code into utilities
4. Break down large files (> 500 lines)

**Priority:** P3
**Estimate:** 1 week

---

#### M-2: Compliance & Licensing
**Source:** NFR_COMPLIANCE.yaml
**Action:**
1. Add MIT License to repository
2. Document third-party licenses
3. Add license headers to Python files
4. Implement DCO for contributions

**Priority:** P3
**Estimate:** 3 hours

---

#### M-3: Workspace Cleanup
**Source:** GRAND_SYSTEM_AUDIT Rec-007
**Action:**
1. Add .gitignore rules for artifacts
2. Implement cleanup mechanism
3. Document workspace management (SOP_008)

**Priority:** P3
**Estimate:** 2 hours

---

#### M-4: Knowledge Base Versioning
**Source:** GRAND_SYSTEM_AUDIT Rec-008
**Action:**
1. Add version headers to all YAML files
2. Track last updated date
3. Document compatibility

**Priority:** P3
**Estimate:** 3 hours

---

## IMPLEMENTATION ROADMAP

### Week 1: Critical Fixes (Foundation Stabilization)
- [x] Fix regression (delegated execution) - DONE
- [ ] Test delegated mode end-to-end - **NEXT!**
- [ ] Add .flake8, .yamllint configs
- [ ] Implement logging strategy
- [ ] Refactor CLI (vibe-cli.py)
- [ ] Add pre-commit hooks

**Goal:** System is testable and follows code standards

---

### Week 2: Testing & Documentation
- [ ] Set up pytest-cov
- [ ] Add unit tests (critical paths)
- [ ] Add integration tests (agent compositions)
- [ ] Add docstrings to public functions
- [ ] Create CONTRIBUTING.md
- [ ] Update README with honest status
- [ ] Create requirements.txt

**Goal:** 80% test coverage, clear documentation

---

### Week 3-4: Quality & Compliance
- [ ] Error handling pass (all Python files)
- [ ] Complexity reduction (refactor > 10)
- [ ] Add MIT License
- [ ] Workspace cleanup
- [ ] Knowledge base versioning

**Goal:** Production-ready code quality

---

## VALIDATION CRITERIA

**Foundation is "hardened" when:**

1. ✅ Delegated execution mode works end-to-end
2. ✅ All code follows PEP 8 (flake8 passes)
3. ✅ Test coverage > 80%
4. ✅ All public functions have docstrings
5. ✅ Logging is centralized (no more print())
6. ✅ CLI is robust (proper arg parsing, --help works)
7. ✅ Error messages are helpful (include context + suggestions)
8. ✅ Pre-commit hooks prevent regressions
9. ✅ README reflects actual status (no false claims)
10. ✅ CHANGELOG.md tracks all changes

---

## ANTI-PATTERNS TO AVOID

Based on Gemini analysis:

1. ❌ **Don't build new features** until foundation is stable
2. ❌ **Don't write more prompts** until existing prompts are tested
3. ❌ **Don't add more agents** until orchestrator works
4. ❌ **Don't claim "Production-Ready"** until tests pass
5. ❌ **Don't skip pre-commit hooks** to "save time"

**Rule:** If it's not tested, it's broken until proven otherwise.

---

## NEXT ACTION (Right Now)

**TEST DELEGATED EXECUTION MODE**

**Why:** This is the CORE architecture (Brain-Arm separation). Everything depends on it.

**How:**
1. I (Claude Code) use Bash tool to start orchestrator in delegated mode
2. Orchestrator writes INTELLIGENCE_REQUEST to STDOUT
3. I read the request from Bash output
4. I process the prompt (I AM the operator!)
5. I write INTELLIGENCE_RESPONSE back via STDIN
6. Orchestrator continues workflow

**Expected Outcome:**
- ✅ Prompt composition works (4,369 chars)
- ✅ INTELLIGENCE_REQUEST is well-formed JSON
- ✅ I can execute the prompt
- ✅ Orchestrator accepts my response
- ✅ Workflow completes (lean_canvas_summary.json generated)

**If it fails:** Document exactly where, fix regression, retry

**If it succeeds:** Foundation is VALIDATED! Move to Week 1 tasks.

---

**Ready to start?** Let's test delegated mode RIGHT NOW!
