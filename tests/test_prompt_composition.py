#!/usr/bin/env python3
"""
Integration Tests: Prompt Composition System

Tests that ALL agents can compose their prompts correctly.
No LLM calls - just validates that composition works.
"""
import sys
from pathlib import Path
import importlib.util

# Load prompt runtime
spec = importlib.util.spec_from_file_location(
    "prompt_runtime",
    "agency_os/00_system/runtime/prompt_runtime.py"
)
prompt_runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt_runtime)
PromptRuntime = prompt_runtime.PromptRuntime


def test_agent_prompt_composition(agent_id: str, task_id: str) -> bool:
    """Test if agent can compose a valid prompt"""
    runtime = PromptRuntime()

    try:
        prompt = runtime.execute_task(
            agent_id=agent_id,
            task_id=task_id,
            context={
                "project_id": "test",
                "workspace": "test",
                "user_input": "test input"
            }
        )

        # Validate prompt
        assert len(prompt) > 100, "Prompt too short"
        assert "CORE PERSONALITY" in prompt or "personality" in prompt.lower(), "Missing personality section"

        print(f"✅ {agent_id}/{task_id}: OK ({len(prompt)} chars)")
        return True

    except Exception as e:
        print(f"❌ {agent_id}/{task_id}: FAILED - {e}")
        return False


def main():
    print("=" * 60)
    print("INTEGRATION TEST: Prompt Composition")
    print("=" * 60)
    print()

    # Test cases: (agent_id, task_id)
    test_cases = [
        ("VIBE_ALIGNER", "02_feature_extraction"),
        ("VIBE_ALIGNER", "03_feasibility_validation"),
        ("GENESIS_BLUEPRINT", "01_select_core_modules"),
        ("GENESIS_BLUEPRINT", "02_design_extensions"),
    ]

    results = []
    for agent_id, task_id in test_cases:
        success = test_agent_prompt_composition(agent_id, task_id)
        results.append((agent_id, task_id, success))

    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)

    passed = sum(1 for _, _, success in results if success)
    failed = len(results) - passed

    print(f"Passed: {passed}/{len(results)}")
    print(f"Failed: {failed}/{len(results)}")

    if failed > 0:
        print("\nFailed tests:")
        for agent_id, task_id, success in results:
            if not success:
                print(f"  - {agent_id}/{task_id}")
        sys.exit(1)

    print("\n✅ All tests passed!")
    sys.exit(0)


if __name__ == "__main__":
    main()
