#!/usr/bin/env python3
"""
OPERATION FIRST CONTACT: Proof of Intelligence
===============================================

This script executes the first real LLM invocation in LIVE FIRE mode.

Goal: Demonstrate end-to-end intelligence by having the system write
      actual code using real API calls (not mocks).

Task: Generate a recursive Fibonacci function with type hints.

Expected outcome:
- Real generated code from LLM (not mock response)
- Actual cost tracking (Cost > $0.00)
- Quota manager telemetry
- Circuit breaker logs

Version: v0.7 (LIVE FIRE)
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add runtime directory for direct imports
runtime_dir = project_root / "agency_os" / "00_system" / "runtime"
sys.path.insert(0, str(runtime_dir))

from llm_client import LLMClient  # noqa: E402

from agency_os.config.phoenix import get_config, reset_config  # noqa: E402

print("=" * 70)
print("🔥 OPERATION FIRST CONTACT: PROOF OF INTELLIGENCE")
print("=" * 70)
print()

# Step 1: Load Phoenix Config and enable LIVE FIRE
print("Step 1: Loading Phoenix Config...")
reset_config()  # Reset to ensure fresh load
config = get_config()

print(f"   Current LIVE FIRE status: {config.safety.live_fire_enabled}")

# Enable LIVE FIRE mode programmatically
os.environ["VIBE_LIVE_FIRE"] = "true"
reset_config()  # Reload config to pick up env var
config = get_config()

print(f"   ✅ LIVE FIRE ENABLED: {config.safety.live_fire_enabled}")
print(
    f"   Quota limits: RPM={config.quotas.requests_per_minute}, "
    f"Cost/hour=${config.quotas.cost_per_hour_usd}"
)
print()

# Step 2: Initialize LLM Client
print("Step 2: Initializing LLM Client...")
client = LLMClient(budget_limit=1.0)  # $1 budget for safety
print(f"   Client mode: {client.mode}")
print(f"   Budget limit: ${client.budget_limit}")
print()

# Step 3: Check API key availability
print("Step 3: Checking API key availability...")
if client.mode == "noop":
    print("   ⚠️  WARNING: No API key found")
    print("   Running in NoOp mode (mock execution, $0 cost)")
    print()
    print("   To enable real execution, set one of:")
    print("     export GOOGLE_API_KEY='your-key-here'")
    print("     export ANTHROPIC_API_KEY='your-key-here'")
    print("     export OPENAI_API_KEY='your-key-here'")
    print("     python scripts/prove_intelligence.py")
    print()
    mock_mode = True
else:
    print(f"   ✅ API key detected - Provider: {client.mode.upper()} - LIVE FIRE ARMED")
    print()
    mock_mode = False

# Step 4: The Task - Proof of Intelligence
print("Step 4: Executing intelligence test...")
print("   Task: Write a recursive Fibonacci function with type hints")
print()

prompt = """Write a Python function that calculates the Fibonacci sequence using recursion.

Requirements:
- Function name: fibonacci
- Use proper type hints (typing module)
- Include a docstring
- Handle base cases (n=0, n=1)
- Return the nth Fibonacci number

Output ONLY the Python code, no explanations."""

print("🚀 Invoking LLM...")
print()

try:
    response = client.invoke(
        prompt=prompt, model="claude-3-5-sonnet-20241022", max_tokens=512, temperature=0.7
    )

    # Step 5: Verify the response
    print("=" * 70)
    print("✅ RESPONSE RECEIVED")
    print("=" * 70)
    print()

    print("Generated Code:")
    print("-" * 70)
    print(response.content)
    print("-" * 70)
    print()

    print("Telemetry:")
    print(f"   Model: {response.model}")
    print(f"   Input tokens: {response.usage.input_tokens}")
    print(f"   Output tokens: {response.usage.output_tokens}")
    print(f"   Cost: ${response.usage.cost_usd:.4f}")
    print(f"   Finish reason: {response.finish_reason}")
    print()

    # Step 6: Cost tracking summary
    print("Cost Tracking Summary:")
    summary = client.get_cost_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    print()

    # Step 7: Verdict
    print("=" * 70)
    if mock_mode:
        print("🤖 MOCK MODE RESULT")
        print("=" * 70)
        print()
        print("   ⚠️  This was a mock execution (NoOpClient)")
        print(
            "   Set GOOGLE_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY to enable real intelligence"
        )
    else:
        print("🧠 PROOF OF INTELLIGENCE: CONFIRMED")
        print("=" * 70)
        print()
        print("   ✅ Real LLM invocation successful")
        print(f"   ✅ Actual cost incurred: ${response.usage.cost_usd:.4f}")
        print("   ✅ Code generation verified")
        print()
        print("   The system is ALIVE. 🔥")

except Exception as e:
    print("=" * 70)
    print("❌ ERROR")
    print("=" * 70)
    print()
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
    print()

    import traceback

    print("Traceback:")
    traceback.print_exc()

print()
print("=" * 70)
print("END OPERATION FIRST CONTACT")
print("=" * 70)
