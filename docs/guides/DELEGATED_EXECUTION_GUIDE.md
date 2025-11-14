# Delegated Execution Guide

**How to use Agency OS with Claude Code Integration**

---

## Overview

Agency OS now supports **delegated execution** - a clean architecture where:
- **core_orchestrator.py** manages state and workflow (the "Arm")
- **Claude Code** provides intelligence and executes prompts (the "Brain")

This guide shows you how to use both modes.

---

## Quick Start

### Option 1: Delegated Mode (Recommended)

Use `vibe-cli` to run with Claude Code integration:

```bash
# From vibe-agency root
./vibe-cli run test-orchestrator-003
```

This will:
1. Launch the orchestrator in delegated mode
2. Monitor for intelligence requests
3. Execute prompts via Anthropic API
4. Stream results back to the orchestrator

### Option 2: Autonomous Mode (Legacy)

Run the orchestrator directly for testing:

```bash
# From vibe-agency root
python agency_os/00_system/orchestrator/core_orchestrator.py \
  /home/user/vibe-agency \
  test-orchestrator-003 \
  --mode=autonomous
```

**Note:** Requires `ANTHROPIC_API_KEY` environment variable.

---

## Architecture: How It Works

### The "Fließband" (Conveyor Belt) Model

```
┌─────────────────────────────────────────────────────┐
│  CLAUDE CODE (You - The Brain)                      │
│  • Sees all prompts                                 │
│  • Executes intelligence operations                 │
│  • Full control and visibility                      │
└─────────────────────────────────────────────────────┘
           │ execute                      ▲ result
           ▼                              │
┌─────────────────────────────────────────────────────┐
│  vibe-cli (The Wrapper)                             │
│  • Launches orchestrator                            │
│  • Monitors STDOUT/STDERR                           │
│  • Handles intelligence requests                    │
│  • Sends responses via STDIN                        │
└─────────────────────────────────────────────────────┘
           │ launch                       ▲ prompts
           ▼                              │ via STDOUT
┌─────────────────────────────────────────────────────┐
│  core_orchestrator.py (The Arm)                     │
│  • Loads workflow YAML                              │
│  • Manages state transitions                        │
│  • Composes prompts from templates                  │
│  • Saves artifacts                                  │
│  • NO LLM calls!                                    │
└─────────────────────────────────────────────────────┘
```

### The Handoff Protocol

#### Step 1: Orchestrator needs intelligence

```python
# core_orchestrator.py
prompt = self.prompt_runtime.execute_task("VIBE_ALIGNER", "scope_negotiation", inputs)

# In delegated mode, send intelligence request to STDOUT
print(json.dumps({
    "type": "INTELLIGENCE_REQUEST",
    "agent": "VIBE_ALIGNER",
    "task_id": "scope_negotiation",
    "prompt": prompt,
    "context": {...}
}))
```

#### Step 2: vibe-cli intercepts request

```python
# vibe-cli
if "---INTELLIGENCE_REQUEST_START---" in line:
    # Parse JSON request
    request = json.loads(buffer)

    # Execute prompt via Anthropic API
    result = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=[{"role": "user", "content": request["prompt"]}]
    )

    # Send response back via STDIN
    process.stdin.write(json.dumps({
        "type": "INTELLIGENCE_RESPONSE",
        "result": json.loads(result.content[0].text)
    }))
```

#### Step 3: Orchestrator receives result

```python
# core_orchestrator.py
response_line = sys.stdin.readline()
response = json.loads(response_line)
return response["result"]
```

---

## Usage Examples

### Example 1: Run Planning Phase

```bash
# Create a test project
mkdir -p workspaces/my-project/artifacts/planning
cat > workspaces/my-project/project_manifest.json <<EOF
{
  "metadata": {
    "projectId": "my-project-001",
    "name": "My Test Project"
  },
  "status": {
    "projectPhase": "PLANNING",
    "planningSubState": "BUSINESS_VALIDATION"
  },
  "budget": {
    "max_cost_usd": 10.0,
    "current_cost_usd": 0.0
  },
  "artifacts": {}
}
EOF

# Run with vibe-cli
./vibe-cli run my-project-001
```

### Example 2: Debug with Autonomous Mode

```bash
# Set API key
export ANTHROPIC_API_KEY="sk-..."

# Run directly (no vibe-cli wrapper)
python agency_os/00_system/orchestrator/core_orchestrator.py \
  $(pwd) \
  my-project-001 \
  --mode=autonomous \
  --log-level=DEBUG
```

### Example 3: Manual Intelligence Responses

For testing, you can manually provide intelligence responses:

```bash
# Run orchestrator in delegated mode
python agency_os/00_system/orchestrator/core_orchestrator.py \
  $(pwd) \
  my-project-001 \
  --mode=delegated &

# When you see an INTELLIGENCE_REQUEST, send a response:
echo '{"type":"INTELLIGENCE_RESPONSE","result":{"features":["test"]}}' | ...
```

(This is more complex - use vibe-cli instead)

---

## Workflow States

### PLANNING Phase

Sub-states:
1. **RESEARCH** (optional)
   - Agents: MARKET_RESEARCHER, TECH_RESEARCHER, FACT_VALIDATOR
   - Output: `research_brief.json`

2. **BUSINESS_VALIDATION**
   - Agent: LEAN_CANVAS_VALIDATOR
   - Input: `research_brief.json` (optional)
   - Output: `lean_canvas_summary.json`

3. **FEATURE_SPECIFICATION**
   - Agent: VIBE_ALIGNER
   - Input: `lean_canvas_summary.json`
   - Output: `feature_spec.json`

### CODING Phase

Agent: CODE_GENERATOR
- Input: `code_gen_spec.json`
- Output: Source code + `test_plan.json`

### TESTING Phase

Agent: QA_VALIDATOR
- Input: `test_plan.json` + source code
- Output: `qa_report.json`

### DEPLOYMENT Phase

Agent: DEPLOY_MANAGER
- Input: Approved `qa_report.json`
- Output: `deploy_receipt.json`

---

## Debugging Tips

### View Intelligence Requests

```bash
# Run with stderr redirection to see markers
./vibe-cli run my-project 2> debug.log

# In another terminal
tail -f debug.log | grep "INTELLIGENCE_REQUEST"
```

### Test Prompt Composition

```bash
# Test prompt runtime directly
python -c "
from pathlib import Path
from agency_os.00_system.runtime.prompt_runtime import PromptRuntime

runtime = PromptRuntime(base_path=Path('.'))
prompt = runtime.execute_task('VIBE_ALIGNER', 'scope_negotiation', {})
print(prompt)
"
```

### Validate Project Manifest

```bash
# Check manifest schema
python agency_os/00_system/orchestrator/core_orchestrator.py \
  $(pwd) \
  my-project-001 \
  --mode=autonomous \
  --log-level=DEBUG
```

---

## Troubleshooting

### "No intelligence response received (EOF on STDIN)"

**Cause:** Orchestrator is waiting for intelligence response, but none was sent.

**Solution:**
- If using vibe-cli: Check that Anthropic API key is set
- If running manually: Send a response via STDIN

### "Agent returned non-JSON response"

**Cause:** LLM didn't return valid JSON.

**Solution:**
- Check prompt template (should specify JSON output format)
- Try with a different model
- Add JSON schema validation to prompt

### "Budget limit reached"

**Cause:** Project exceeded `max_cost_usd` in manifest.

**Solution:**
- Increase budget in `project_manifest.json`
- Or: Use a cheaper model
- Or: Reduce prompt complexity

---

## Environment Variables

- `ANTHROPIC_API_KEY` - Required for vibe-cli and autonomous mode
- `LOG_LEVEL` - Set logging level (DEBUG, INFO, WARNING, ERROR)

---

## Next Steps

1. Read [ADR-003: Delegated Execution Architecture](../architecture/ADR-003_Delegated_Execution_Architecture.md)
2. Explore example projects in `workspaces/`
3. Create your own project manifest
4. Run `vibe-cli run <project-id>`

---

## FAQ

**Q: Why two execution modes?**

A: Delegated mode is the "correct" architecture (Brain + Arm separation). Autonomous mode is kept for testing and backward compatibility.

**Q: Can I use this without Claude Code?**

A: Yes! `vibe-cli` works standalone with just an Anthropic API key. It doesn't require Claude Code to be running.

**Q: Can Claude Code intercept intelligence requests in this chat?**

A: Not yet! That requires a tighter integration. For now, use `vibe-cli` which handles the handoff autonomously. Future work: Claude MCP integration.

**Q: What if prompt_runtime doesn't exist?**

A: Then you'll get an import error. Check that `agency_os/00_system/runtime/prompt_runtime.py` exists and implements the `PromptRuntime` class.

---

## Support

- GitHub Issues: [vibe-agency/issues](https://github.com/kimeisele/vibe-agency/issues)
- Documentation: `docs/architecture/`
- Examples: `workspaces/*/`
