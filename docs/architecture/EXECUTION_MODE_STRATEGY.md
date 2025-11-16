# EXECUTION MODE STRATEGY

**Version:** 1.0
**Date:** 2025-11-15
**Status:** ✅ DEFINITIVE
**Purpose:** Eliminate ambiguity in execution architecture

---

## 🎯 THE PROBLEM

**Root Cause:** ADR-003 created architectural ambiguity that leads to recurring regression.

**The Ambiguity:**
```
ADR-003: "vibe-cli executes prompts via Anthropic API OR delegates to Claude Code"
                                                        ^^
                                                      UNCLEAR!
```

**Results in:**
- ❌ vibe-cli has Anthropic SDK imports
- ❌ Nested API calls (Claude → vibe-cli → Anthropic API)
- ❌ No tests for "delegation mode"
- ❌ Developers don't know WHICH mode to implement

---

## ✅ THE SOLUTION: SINGLE MODE FOR MVP

**RULE:** MVP = **DELEGATION ONLY**

### What This Means

```
┌─────────────────────────────────────────────┐
│ CLAUDE CODE (The ONLY Operator in MVP)     │
│ - Executes ALL prompts                      │
│ - Makes ALL intelligence decisions          │
│ - Uses vibe-cli as TOOL                     │
└─────────────────┬───────────────────────────┘
                  │ uses
                  ▼
┌─────────────────────────────────────────────┐
│ vibe-cli (BRIDGE ONLY - NO INTELLIGENCE)   │
│ - Launches orchestrator subprocess          │
│ - Reads INTELLIGENCE_REQUEST from STDOUT    │
│ - Prints to Claude Code session             │
│ - Reads Claude Code response from session   │
│ - Sends response to STDIN                   │
│ - NO Anthropic API calls                    │
│ - NO anthropic SDK imports                  │
└─────────────────┬───────────────────────────┘
                  │ launches
                  ▼
┌─────────────────────────────────────────────┐
│ core_orchestrator (ARM - NO INTELLIGENCE)  │
│ - Composes prompts                          │
│ - Manages state                             │
│ - Saves artifacts                           │
│ - NO LLM calls                              │
└─────────────────────────────────────────────┘
```

---

## 📋 EXPLICIT RULES FOR MVP

### ✅ ALLOWED in vibe-cli

```python
# File operations
with open('artifact.json') as f:
    data = json.load(f)

# STDIN/STDOUT bridge
print(json.dumps(intelligence_request))
response = sys.stdin.readline()

# Process management
process = subprocess.Popen(['orchestrator', ...])

# JSON formatting
result = json.loads(response_text)
```

### ❌ FORBIDDEN in vibe-cli (MVP)

```python
# NO Anthropic SDK imports
import anthropic  # ❌ FORBIDDEN

# NO API clients
self.client = anthropic.Anthropic(api_key=...)  # ❌ FORBIDDEN

# NO prompt execution
response = client.messages.create(...)  # ❌ FORBIDDEN

# NO tool use loops
if response.stop_reason == "tool_use":  # ❌ FORBIDDEN (for MVP)
```

**Why Forbidden:**
- Claude Code (the operator) IS the intelligence layer
- Nested API calls = architecture violation
- Tool use loop belongs in Claude Code session, not vibe-cli

---

## 🔄 EXECUTION FLOW (MVP - FILE-BASED)

**Changed:** Nov 16, 2025 - Switched from STDIN/STDOUT to file-based delegation
**Reason:** Browser environment compatibility (see ARCHITECTURE_BREAKDOWN_REPORT.md)

### Step 1: Claude Code Launches vibe-cli

```bash
# Claude Code executes this
./vibe-cli run my-project
```

### Step 2: vibe-cli Launches Orchestrator

```python
# vibe-cli does NOT make API calls
# It only launches subprocess
process = subprocess.Popen([
    'python', 'core_orchestrator.py',
    repo_root,
    project_id,
    '--mode=delegated'
])
```

### Step 3: Orchestrator Requests Intelligence

```python
# core_orchestrator.py
print(json.dumps({
    "type": "INTELLIGENCE_REQUEST",
    "prompt": "You are VIBE_ALIGNER. Extract features from: ..."
}))
```

### Step 4: vibe-cli Writes Request to File

```python
# vibe-cli reads STDOUT from orchestrator
intelligence_request = parse_stdout(process.stdout)

# vibe-cli writes request to file (NEW - file-based delegation)
request_file = Path(f"workspaces/{project_id}/.delegation/request_{uuid}.json")
with open(request_file, 'w') as f:
    json.dump(intelligence_request, f)

logger.info(f"📤 Delegation request written: {request_file}")
logger.info("⏳ Waiting for response file...")
```

### Step 5: Claude Code (Operator) Reads Request & Responds

```python
# Claude Code session (me!) reads request file
with open("workspaces/my-project/.delegation/request_abc123.json") as f:
    request = json.load(f)

# Execute prompt via Anthropic API
response = anthropic.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4000,
    messages=[{"role": "user", "content": request["prompt"]}]
)

# Write response file
response_file = "workspaces/my-project/.delegation/response_abc123.json"
with open(response_file, 'w') as f:
    json.dump({"result": parse_response(response)}, f)
```

### Step 6: vibe-cli Polls for Response File

```python
# vibe-cli polls for response (500ms intervals)
response_file = Path(f"workspaces/{project_id}/.delegation/response_{uuid}.json")

timeout = 600  # 10 minutes
while not response_file.exists():
    if timeout_exceeded:
        raise TimeoutError()
    time.sleep(0.5)

# Read response
with open(response_file) as f:
    response = json.load(f)

# Cleanup
request_file.unlink()
response_file.unlink()
```

### Step 7: vibe-cli Sends Response to Orchestrator

```python
# vibe-cli forwards response to orchestrator via STDIN
process.stdin.write(json.dumps({
    "type": "INTELLIGENCE_RESPONSE",
    "result": response["result"]
}))
```

### Step 8: Orchestrator Processes Result

```python
# core_orchestrator.py
response = json.loads(sys.stdin.readline())
result = response['result']
# Update manifest, save artifacts, etc.
```

---

## 📁 FILE-BASED DELEGATION DETAILS

### Request File Format

**Location:** `workspaces/{project_id}/.delegation/request_{uuid}.json`

**Schema:**
```json
{
  "type": "INTELLIGENCE_DELEGATION",
  "request_id": "abc123-uuid",
  "agent": "VIBE_ALIGNER",
  "task_id": "01_feature_extraction",
  "prompt": "Full composed prompt text...",
  "timestamp": "2025-11-16T00:30:00Z",
  "metadata": {
    "delegator": "vibe-cli",
    "mode": "file_based_delegation",
    "request_file": "workspaces/my-project/.delegation/request_abc123.json",
    "response_file": "workspaces/my-project/.delegation/response_abc123.json"
  }
}
```

### Response File Format

**Location:** `workspaces/{project_id}/.delegation/response_{uuid}.json`

**Schema:**
```json
{
  "result": {
    "features": [...],
    "scope_negotiation": {...},
    ...
  }
}
```

### Cleanup Strategy

- **Success:** Both files deleted after response read
- **Timeout:** Request file deleted, no response file created
- **Error:** Both files deleted to prevent stale data

### Compatibility

✅ **Works in:**
- Claude Code Browser
- Claude Code CLI
- GitHub Codespaces
- Local terminal
- CI/CD environments

✅ **No dependencies on:**
- STDIN/STDOUT interactivity
- Subprocess communication
- Terminal features

---

## 🚫 WHAT THIS ELIMINATES

### Problem: Nested API Calls

**Before (WRONG):**
```
Claude Code (operator)
  → vibe-cli
    → anthropic.Anthropic().messages.create()  ← NESTED!
      → Claude API (different session)
```

**After (CORRECT):**
```
Claude Code (operator)
  → vibe-cli (bridge only)
    → Orchestrator
      → Prints prompt to Claude Code
        → Claude Code responds
```

### Problem: Ambiguous Execution Mode

**Before (AMBIGUOUS):**
```yaml
execution_modes:
  - delegated: "?"
  - autonomous: "?"
  - standalone: "?"
# Which one when???
```

**After (CLEAR):**
```yaml
mvp_execution_mode: "DELEGATION_ONLY"
operator: "Claude Code"
vibe_cli_role: "STDOUT/STDIN bridge"
api_calls: "FORBIDDEN"
```

---

## 🧪 VALIDATION STRATEGY

### Test 1: No Anthropic Imports

```python
# tests/anti_regression/test_no_anthropic_in_vibe_cli.py

def test_vibe_cli_no_anthropic_imports():
    """vibe-cli MUST NOT import anthropic SDK in MVP"""
    with open('vibe-cli') as f:
        content = f.read()

    assert 'import anthropic' not in content, \
        "REGRESSION: vibe-cli imports anthropic SDK (FORBIDDEN in MVP)"

    assert 'anthropic.Anthropic' not in content, \
        "REGRESSION: vibe-cli uses Anthropic client (FORBIDDEN in MVP)"
```

### Test 2: No API Calls

```python
def test_vibe_cli_no_api_calls():
    """vibe-cli MUST NOT make API calls in MVP"""
    with open('vibe-cli') as f:
        content = f.read()

    forbidden_patterns = [
        'messages.create',
        'client.messages',
        'anthropic.Anthropic('
    ]

    for pattern in forbidden_patterns:
        assert pattern not in content, \
            f"REGRESSION: vibe-cli contains '{pattern}' (API call in MVP)"
```

### Test 3: Delegation Flow Works

```python
def test_delegation_flow_end_to_end():
    """Test full delegation flow without API calls"""
    # Mock Claude Code operator
    with mock_claude_code_session():
        # Run vibe-cli
        result = run_vibe_cli('test-project')

        # Assert: No Anthropic API calls made
        assert mock_anthropic_api.call_count == 0, \
            "REGRESSION: API calls detected in delegated mode"

        # Assert: Prompts were shown to operator
        assert mock_claude_code_session.prompts_received > 0, \
            "vibe-cli didn't delegate to Claude Code"
```

---

## 📊 MIGRATION PLAN

### Phase 1: Documentation (TODAY)

- ✅ Write this document (EXECUTION_MODE_STRATEGY.md)
- ✅ Create ADR-003 Amendment
- ✅ Update ARCHITECTURE_V2.md (clarify "delegated mode")
- ✅ Update SSOT.md (mark vibe-cli API calls as "to be removed")

### Phase 2: Tests (TODAY)

- ✅ Write `test_no_anthropic_in_vibe_cli.py`
- ✅ Write `test_vibe_cli_no_api_calls.py`
- ✅ Add to CI pipeline

### Phase 3: Code Removal (NEXT SESSION)

**Why next session:** Need user confirmation before deleting working code.

Changes needed in vibe-cli:
```python
# REMOVE:
import anthropic  # Line 23
self.anthropic_api_key = ...  # Line 49
self.client = anthropic.Anthropic(...)  # Line 54
def _execute_prompt(self, ...):  # Lines 394-520 (entire method!)
def _load_tools_for_agent(self, ...):  # Tool loading logic

# REPLACE WITH:
def _delegate_to_operator(self, intelligence_request):
    """Print request to Claude Code, wait for typed response"""
    print("\n" + "="*70)
    print("INTELLIGENCE REQUEST")
    print("="*70)
    print(intelligence_request['prompt'])
    print("="*70)
    print("Respond with JSON:")

    # Read operator's response
    response_json = input("> ")
    return json.loads(response_json)
```

### Phase 4: Governance (NEXT SESSION)

Add to `system_steward_framework/knowledge/guardian_directives.yaml`:

```yaml
- id: "GD-010"
  name: "No Nested Intelligence"
  description: "vibe-cli MUST NOT make Anthropic API calls (delegation only)"
  rationale: "Intelligence lives in Claude Code operator, not in tools"
  enforcement: "code"  # Enforced by tests
  applies_to: "vibe-cli"
  examples:
    - "vibe-cli reads INTELLIGENCE_REQUEST from orchestrator"
    - "vibe-cli delegates to Claude Code operator (prints prompt)"
    - "vibe-cli sends operator's response back to orchestrator"
  violations:
    - "import anthropic in vibe-cli"
    - "client.messages.create() in vibe-cli"
    - "Nested API calls"
```

---

## 🔮 FUTURE: Standalone Mode (v1.1+)

**NOT IN MVP. Explicitly deferred.**

When we need vibe-cli standalone (without Claude Code operator):

```python
# vibe-cli v1.1
execution_mode = detect_execution_mode()

if execution_mode == "inside_claude_code":
    # Delegation mode (MVP)
    delegate_to_operator(intelligence_request)

elif execution_mode == "standalone":
    # Standalone mode (v1.1)
    # Requires ANTHROPIC_API_KEY
    # Makes direct API calls
    # Implements tool use loop
    response = client.messages.create(...)

else:
    raise RuntimeError("Cannot detect execution mode")
```

**How to detect:**
```python
def detect_execution_mode():
    # Check if running inside Claude Code
    if os.getenv('CLAUDE_CODE_SESSION'):
        return "inside_claude_code"

    # Check if API key available
    if os.getenv('ANTHROPIC_API_KEY'):
        return "standalone"

    # Cannot determine
    return "unknown"
```

**But for MVP:** This detection is NOT implemented. Only delegation mode exists.

---

## ✅ DECISION RECORD

**Decision:** MVP uses **DELEGATION ONLY** execution mode.

**Rationale:**
1. **Simplicity:** One mode = easier to test, maintain, understand
2. **Correctness:** Matches stated architecture ("Intelligence in Claude Code")
3. **No regression:** Clear rules prevent recurring bugs
4. **Testable:** Can write anti-regression tests
5. **Upgradable:** Can add standalone mode in v1.1 without breaking MVP

**Alternatives Considered:**
- **Hybrid mode now:** Rejected (too complex, enables regression)
- **Standalone mode only:** Rejected (doesn't match architecture)

**Trade-offs:**
- ✅ **Gain:** Architectural clarity, no nested API calls
- ❌ **Lose:** Can't run vibe-cli standalone (until v1.1)

**Acceptance Criteria:**
- [ ] Tests pass: `test_no_anthropic_in_vibe_cli.py`
- [ ] Tests pass: `test_vibe_cli_no_api_calls.py`
- [ ] ARCHITECTURE_V2.md updated with "MVP = delegation only"
- [ ] ADR-003 amended with clarification
- [ ] vibe-cli code cleaned (Anthropic SDK removed)

---

## 📚 Related Documents

- **[ADR-003](./ADR-003_Delegated_Execution_Architecture.md)** - Original architecture decision (to be amended)
- **[ARCHITECTURE_V2.md](../../ARCHITECTURE_V2.md)** - Conceptual model (to be updated)
- **[SSOT.md](../../SSOT.md)** - Implementation decisions (to be updated)

---

**Last Updated:** 2025-11-15
**Author:** System Steward (Claude Code)
**Status:** ✅ APPROVED - Ready for implementation
**Next Action:** Write anti-regression tests
