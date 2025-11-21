# ARCH-033: The Brain Transplant (Real LLM Integration)

**Status:** ✅ Implemented
**Version:** 1.0
**Date:** 2025-11-21
**Related:** ARCH-032 (Unified Entry Point), GAD-511 (Google Provider)

---

## Problem

ARCH-032 gave us a working entry point with two modes (interactive + mission),
but the operator agent was using `MockLLMProvider` - a dummy brain that just
returns static responses.

**This is like having a Ferrari with a rubber engine.**

To enable real missions (Phase 4), we need:
- **Real intelligence** (actual LLM, not mock responses)
- **Automatic fallback** (graceful degradation if no API key)
- **Provider flexibility** (easy to swap between Google, Anthropic, OpenAI)

---

## Solution

**Smart Provider Selection with Graceful Fallback**

```python
if GOOGLE_API_KEY:
    provider = GoogleProvider(api_key)  # REAL BRAIN 🧠
else:
    provider = MockLLMProvider()       # FALLBACK (for testing)
```

### Architecture

```
apps/agency/cli.py
    ↓
Check GOOGLE_API_KEY env var
    ↓
┌─────────────────────┬──────────────────────┐
│ API Key Found?      │ No API Key           │
├─────────────────────┼──────────────────────┤
│ GoogleProvider      │ MockLLMProvider      │
│ (Real Gemini AI)    │ (Static responses)   │
│ - Gemini 2.5 Flash  │ - No API calls       │
│ - FREE (preview)    │ - For testing        │
│ - Real intelligence │ - Predictable        │
└─────────────────────┴──────────────────────┘
    ↓
SimpleLLMAgent
    ↓
VibeKernel
```

---

## Implementation

### 1. GoogleProvider Adapter

**Problem:** GoogleProvider (from `vibe_core.runtime.providers.google`) uses:
```python
def invoke(prompt: str) -> LLMResponse
```

But SimpleLLMAgent expects:
```python
def chat(messages: list[dict]) -> str
```

**Solution:** Create `vibe_core/llm/google_adapter.py` that bridges the two:

```python
class GoogleProvider(LLMProvider):
    """Adapter for runtime.GoogleProvider -> SimpleLLMAgent interface."""

    def __init__(self, api_key, model="gemini-2.5-flash-exp"):
        self._provider = RuntimeGoogleProvider(api_key)
        self._default_model = model

    def chat(self, messages: list[dict], model=None) -> str:
        # Convert messages to prompt
        prompt = self._messages_to_prompt(messages)

        # Call runtime provider
        response = self._provider.invoke(prompt, model)

        # Extract text
        return response.content
```

### 2. Smart Selection in cli.py

```python
# Step 4.5: Choose Provider
api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    # REAL BRAIN
    try:
        provider = GoogleProvider(api_key, model="gemini-2.5-flash-exp")
        logger.info("🧠 CONNECTED TO GOOGLE GEMINI")
    except ProviderNotAvailableError as e:
        logger.warning(f"⚠️  Fallback to Mock: {e}")
        provider = MockLLMProvider()
else:
    # MOCK BRAIN
    logger.info("ℹ️  No API key, using MockProvider")
    provider = MockLLMProvider()

operator_agent = SimpleLLMAgent(
    agent_id="vibe-operator",
    provider=provider,  # Either real or mock
    tool_registry=registry,
)
```

---

## Usage

### With Google API Key (Real AI)

1. Set environment variable:
```bash
export GOOGLE_API_KEY="your-key-here"
```

Or create `.env` file:
```
GOOGLE_API_KEY=your-key-here
```

2. Run mission:
```bash
uv run python apps/agency/cli.py --mission "Write a poem about clean code"
```

Expected output:
```
🧠 CONNECTED TO GOOGLE GEMINI (gemini-2.5-flash-exp)
🤖 VIBE OPERATOR STARTED MISSION
...
[Real AI-generated response]
✅ MISSION COMPLETE
```

### Without API Key (Mock Fallback)

```bash
# No GOOGLE_API_KEY set
uv run python apps/agency/cli.py --mission "Test mission"
```

Expected output:
```
ℹ️  No GOOGLE_API_KEY found, using MockProvider
🤖 VIBE OPERATOR STARTED MISSION
...
[Mock response: "I am the Vibe Operator..."]
✅ MISSION COMPLETE
```

---

## Provider Details

### Google Gemini 2.5 Flash (Experimental)

**Model:** `gemini-2.5-flash-exp`

**Why this model:**
- ✅ **FREE** during preview period ($0.00/MTok)
- ✅ **FAST** (optimized for low latency)
- ✅ **LATEST** (most capable Gemini model as of 2025-11)
- ✅ **128K context** (can handle large codebases)

**Pricing (when preview ends):**
- Input: ~$0.075/MTok
- Output: ~$0.30/MTok
- Still very cheap compared to GPT-4

**Alternative models:**
- `gemini-1.5-flash`: Stable, production-ready
- `gemini-1.5-pro`: More capable, higher cost
- `gemini-2.0-flash-exp`: Also free in preview

To change model:
```python
provider = GoogleProvider(api_key, model="gemini-1.5-flash")
```

---

## Architecture Benefits

### 1. Graceful Degradation
System works with or without API key:
- **With key:** Real AI intelligence
- **Without key:** Predictable mock for testing

### 2. Provider Flexibility
Easy to add more providers:

```python
# In cli.py:
if os.getenv("ANTHROPIC_API_KEY"):
    provider = AnthropicProvider()
elif os.getenv("OPENAI_API_KEY"):
    provider = OpenAIProvider()
elif os.getenv("GOOGLE_API_KEY"):
    provider = GoogleProvider()
else:
    provider = MockLLMProvider()
```

### 3. Separation of Concerns
- `apps/agency/cli.py`: Application logic
- `vibe_core/llm/google_adapter.py`: Protocol adapter
- `vibe_core/runtime/providers/google.py`: Google API client
- `vibe_core/agents/llm_agent.py`: Agent behavior

Each layer has one job.

### 4. Testability
Tests can use MockProvider without API keys:

```python
def test_operator():
    kernel = boot_kernel()  # Uses Mock if no API key
    # Test logic without API costs
```

---

## Testing

### Boot Test
```bash
uv run python apps/agency/cli.py --help
```

Should show no errors, log provider selection.

### Mock Mission Test
```bash
# Ensure no GOOGLE_API_KEY
unset GOOGLE_API_KEY

uv run python apps/agency/cli.py --mission "Test"
```

Should complete with mock response.

### Real Mission Test (if you have API key)
```bash
export GOOGLE_API_KEY="your-key"

uv run python apps/agency/cli.py --mission "Write a haiku about Python"
```

Should get real AI-generated haiku.

---

## Real World Mission Example

```bash
export GOOGLE_API_KEY="..."

uv run python apps/agency/cli.py --mission "Analyze the files in vibe_core/ and write a summary report to ANALYSIS.md"
```

Expected behavior:
1. Agent uses `read_file` tool to explore vibe_core/
2. Agent synthesizes understanding
3. Agent uses `write_file` tool to create ANALYSIS.md
4. All operations logged to ledger
5. Soul governance ensures safety (.git is protected)

---

## Files Created

```
+ vibe_core/llm/google_adapter.py (200 lines)
  - GoogleProvider adapter class
  - Messages-to-prompt conversion
  - Error handling

~ apps/agency/cli.py (modified)
  - Smart provider selection
  - Graceful fallback logic
  - Logging for observability

+ docs/architecture/ARCH-033_REAL_BRAIN.md
  - This document
```

---

## Dependencies

- **google-generativeai** package (already in pyproject.toml)
- **GOOGLE_API_KEY** environment variable (optional, for real AI)
- **ARCH-032** (Unified Entry Point)
- **GAD-511** (Google Provider implementation)

---

## Future Enhancements

1. **Multi-Provider Support:** Try multiple providers in priority order
2. **Cost Tracking:** Log cumulative API costs per session
3. **Conversation Memory:** Maintain multi-turn conversations
4. **Streaming Responses:** Real-time token streaming for long outputs
5. **Provider Health Check:** Auto-switch if primary provider fails

---

## Key Insight

**The system is now REAL.**

Before ARCH-033:
- Operator was a puppet (MockProvider)
- Could demonstrate flow, but not useful work

After ARCH-033:
- Operator has real intelligence (Gemini 2.5)
- Can actually analyze, write, reason
- Free during preview (no API costs)
- Falls back gracefully without key

**This is the moment vibe-agency becomes useful, not just interesting.**

---

## Verification

```bash
# Test 1: No API key (should use mock)
unset GOOGLE_API_KEY
echo "exit" | uv run python apps/agency/cli.py
# Should log: "ℹ️  No GOOGLE_API_KEY found, using MockProvider"

# Test 2: With API key (should use Gemini)
export GOOGLE_API_KEY="your-key"
echo "exit" | uv run python apps/agency/cli.py
# Should log: "🧠 CONNECTED TO GOOGLE GEMINI"

# Test 3: Real mission
uv run python apps/agency/cli.py --mission "Say hello in 3 words"
# Should get real AI response
```

Success criteria: All three tests pass without errors.
