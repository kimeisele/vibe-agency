# ADR-003 AMENDMENT: MVP Clarification

**Amendment Date:** 2025-11-15
**Original ADR:** ADR-003 (2025-11-14)
**Status:** ✅ APPROVED
**Reason:** Clarify ambiguous "OR delegates to Claude Code" statement

---

## Problem with Original ADR-003

The original ADR-003 stated:

> "vibe-cli executes prompts via Anthropic API **OR delegates to Claude Code**"

This created **ambiguity**:
- When does it execute via API?
- When does it delegate?
- How to detect which mode?
- What's the MVP behavior?

**Result:** Developers implemented ONLY the API path, violating the architecture.

---

## Amendment

### Original Statement (AMBIGUOUS)

```
vibe-cli:
- Executes prompts via Anthropic API (or delegates to Claude Code)
```

### Amended Statement (CLEAR)

```
vibe-cli (MVP):
- Delegates to Claude Code ONLY
- NO Anthropic API calls
- Acts as STDOUT/STDIN bridge

vibe-cli (v1.1 - Future):
- MAY support standalone mode with API calls
- Detection logic required
- NOT in MVP scope
```

---

## MVP Execution Mode

### Definitive Rule

**MVP = DELEGATION ONLY**

```yaml
execution_mode:
  mvp: "DELEGATION_ONLY"
  operator: "Claude Code"
  vibe_cli_role: "BRIDGE"
  api_calls: "FORBIDDEN"
  anthropic_sdk: "NOT_IMPORTED"
```

### Architecture (Corrected)

```
┌────────────────────────────────────────────┐
│ CLAUDE CODE (The ONLY Operator)           │
│ - Executes ALL prompts                     │
│ - Provides ALL intelligence                │
│ - Uses vibe-cli as tool                    │
└────────────────┬───────────────────────────┘
                 │ uses
                 ▼
┌────────────────────────────────────────────┐
│ vibe-cli (BRIDGE - NO API CALLS)          │
│ - Launches orchestrator                    │
│ - Reads STDOUT (INTELLIGENCE_REQUEST)      │
│ - Delegates to Claude Code (prints prompt) │
│ - Sends response to STDIN                  │
│ - NO anthropic SDK imports                 │
│ - NO client.messages.create()              │
└────────────────┬───────────────────────────┘
                 │ launches
                 ▼
┌────────────────────────────────────────────┐
│ core_orchestrator (ARM)                    │
│ - Composes prompts                         │
│ - Manages state                            │
│ - NO LLM calls                             │
└────────────────────────────────────────────┘
```

---

## What Changes

### In vibe-cli (TO BE REMOVED)

```python
# ❌ REMOVE (violates MVP architecture)
import anthropic
self.client = anthropic.Anthropic(api_key=...)
response = self.client.messages.create(...)

# Tool use loop (Lines 394-520)
def _execute_prompt(self, ...):
    # This entire method makes API calls
    # REMOVE for MVP
```

### In vibe-cli (TO BE ADDED)

```python
# ✅ ADD (delegation to Claude Code)
def _delegate_to_operator(self, intelligence_request):
    """Delegate intelligence request to Claude Code operator"""
    print("\n" + "="*70)
    print("INTELLIGENCE REQUEST")
    print("="*70)
    print(intelligence_request['prompt'])
    print("="*70)
    print("Respond with JSON:")

    # Claude Code operator types response
    response_json = input("> ")
    return json.loads(response_json)
```

---

## Enforcement

### Anti-Regression Tests

```python
# tests/anti_regression/test_no_anthropic_in_vibe_cli.py

def test_vibe_cli_no_anthropic_imports():
    """vibe-cli MUST NOT import anthropic SDK"""
    # FAILS if 'import anthropic' found

def test_vibe_cli_no_api_calls():
    """vibe-cli MUST NOT make API calls"""
    # FAILS if 'client.messages.create' found

def test_vibe_cli_no_api_key():
    """vibe-cli MUST NOT use ANTHROPIC_API_KEY"""
    # FAILS if API key referenced
```

### Governance Rule

```yaml
# system_steward_framework/knowledge/guardian_directives.yaml
- id: "GD-010"
  name: "No Nested Intelligence"
  description: "vibe-cli delegates to Claude Code, no API calls"
  enforcement: "code"  # Via tests
  violations:
    - "import anthropic in vibe-cli"
    - "Anthropic API calls in vibe-cli"
```

---

## Migration Timeline

### Phase 1: Documentation ✅ (TODAY)
- [x] Write EXECUTION_MODE_STRATEGY.md
- [x] Create this amendment
- [x] Write anti-regression tests

### Phase 2: Code Cleanup (NEXT SESSION)
- [ ] Remove anthropic SDK from vibe-cli
- [ ] Implement delegation logic
- [ ] Verify tests pass

### Phase 3: Documentation Update (NEXT SESSION)
- [ ] Update ARCHITECTURE_V2.md
- [ ] Update SSOT.md
- [ ] Update DELEGATED_EXECUTION_GUIDE.md

---

## Future: Standalone Mode (v1.1+)

**EXPLICITLY DEFERRED - NOT IN MVP**

When needed:
```python
# vibe-cli v1.1
if os.getenv('CLAUDE_CODE_SESSION'):
    # Delegation mode (MVP)
    return delegate_to_operator(request)
elif os.getenv('ANTHROPIC_API_KEY'):
    # Standalone mode (v1.1)
    return execute_via_api(request)
else:
    raise RuntimeError("Cannot detect execution mode")
```

But for MVP: **Delegation only, no mode detection needed.**

---

## Rationale

### Why This Amendment?

1. **Eliminate Ambiguity**
   - Original: "OR delegates" (unclear when)
   - Amended: "DELEGATION ONLY" (clear)

2. **Prevent Regression**
   - Developers kept adding Anthropic SDK
   - No tests prevented this
   - Now: Tests FAIL if SDK added

3. **Architectural Purity**
   - Original vision: "Intelligence in Claude Code"
   - Implementation: vibe-cli made API calls (violation)
   - Corrected: vibe-cli is bridge only

4. **Simplicity**
   - One mode = easier to test
   - Clear rules = less confusion
   - Can add complexity in v1.1

### Trade-offs Accepted

- ✅ **Gain:** Architectural clarity, testability, no nested calls
- ❌ **Lose:** vibe-cli can't run standalone (until v1.1)

**Decision:** Worth it. Standalone mode deferred to v1.1.

---

## Approval

**Approved By:** System Steward (Claude Code)
**Date:** 2025-11-15
**Supersedes:** ADR-003 ambiguous statement
**Effective:** Immediately

**Acceptance Criteria:**
- [x] EXECUTION_MODE_STRATEGY.md written
- [x] Anti-regression tests created
- [ ] Tests pass (after code cleanup)
- [ ] Documentation updated

---

## Related Documents

- **[ADR-003](./ADR-003_Delegated_Execution_Architecture.md)** - Original decision
- **[EXECUTION_MODE_STRATEGY.md](./EXECUTION_MODE_STRATEGY.md)** - Detailed strategy
- **[ARCHITECTURE_V2.md](../../ARCHITECTURE_V2.md)** - Conceptual model
- **[SSOT.md](../../SSOT.md)** - Implementation truth

---

**Last Updated:** 2025-11-15
**Status:** ✅ APPROVED
**Next Action:** Code cleanup (next session)
