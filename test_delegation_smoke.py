#!/usr/bin/env python3
"""
ARCH-038: Smoke Test for Delegation
====================================

Manual test: Boot system, fire DelegateTool directly, observe crash/success.

This is NOT a unit test. This is a MANUAL verification that:
1. DelegateTool can be called
2. Kernel routes to specialist-planning
3. SpecialistFactory creates PlanningSpecialist
4. PlanningSpecialist either works or crashes

Expected outcome: Will probably crash at PlanningSpecialist.__init__
because it needs orchestrator (legacy dependency).

That's EXACTLY what we want to see.
"""

import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from apps.agency.cli import boot_kernel


def main():
    print("=" * 70)
    print("🧪 ARCH-038: SMOKE TEST - Manual Delegation")
    print("=" * 70)
    print()

    # Boot the system (no API key = MockProvider)
    print("Step 1: Booting kernel...")
    kernel = boot_kernel()
    print()

    # Find DelegateTool
    delegate_tool = None
    operator = kernel.agent_registry["vibe-operator"]

    if hasattr(operator, "tool_registry"):
        for tool_name, tool in operator.tool_registry.tools.items():
            if tool_name == "delegate_task":
                delegate_tool = tool
                break

    if not delegate_tool:
        print("❌ FATAL: DelegateTool not found in operator's tool registry!")
        return 1

    print(f"✅ Found DelegateTool: {delegate_tool}")
    print()

    # Prepare delegation payload (simulate what LLM would send)
    print("Step 2: Preparing delegation payload...")
    delegation_params = {
        "agent_id": "specialist-planning",
        "payload": {
            "mission_id": 1,
            "mission_uuid": "smoke-test-uuid",
            "phase": "PLANNING",
            "project_root": str(PROJECT_ROOT / "test_project"),
            "metadata": {"test": "smoke_test"},
        },
    }
    print(f"   Agent: {delegation_params['agent_id']}")
    print(f"   Mission ID: {delegation_params['payload']['mission_id']}")
    print()

    # Fire DelegateTool directly
    print("Step 3: Firing DelegateTool.execute()...")
    print("   🔥 THIS IS WHERE IT WILL CRASH OR SUCCEED 🔥")
    print()

    try:
        result = delegate_tool.execute(delegation_params)

        print("=" * 70)
        print("✅ DELEGATION SUCCEEDED!")
        print("=" * 70)
        print(f"Success: {result.success}")
        print(f"Output: {result.output}")
        print(f"Error: {result.error}")
        print()

        if result.success:
            print("🎉 PHASE 1 PASSED: Delegation Succeeded!")
            print("   - DelegateTool executed without crashing")
            print("   - Task submitted to kernel")
            print(f"   - Task ID: {result.output.get('task_id')}")
            print()

            # PHASE 2: Execute the task via kernel.tick()
            print("=" * 70)
            print("PHASE 2: Executing delegated task (kernel.tick())")
            print("=" * 70)
            print("   🔥 THIS IS WHERE SPECIALIST GETS CREATED 🔥")
            print()

            try:
                # Execute the task
                print("Calling kernel.tick()...")
                kernel.tick()
                print("✅ kernel.tick() completed without crashing!")
                print()
                print("🎉 PHASE 2 PASSED: Specialist Factory worked!")
                print("   The specialist was created and executed.")
                print()
                return 0

            except Exception as tick_error:
                print("💥 PHASE 2 CRASH: Specialist creation/execution failed")
                print(f"Exception: {type(tick_error).__name__}")
                print(f"Message: {tick_error}")
                print()
                print("Stack trace:")
                import traceback
                traceback.print_exc()
                print()
                print("🔍 DIAGNOSIS:")
                print("   The Factory tried to create the Specialist but crashed.")
                print("   This shows us the exact legacy dependency that's missing.")
                return 1
        else:
            print("⚠️  DELEGATION FAILED (but didn't crash)")
            print(f"   Error: {result.error}")
            return 1

    except Exception as e:
        print("=" * 70)
        print("💥 CRASH DETECTED!")
        print("=" * 70)
        print(f"Exception: {type(e).__name__}")
        print(f"Message: {e}")
        print()
        print("Stack trace:")
        import traceback
        traceback.print_exc()
        print()
        print("🔍 DIAGNOSIS:")
        print("   This crash shows us EXACTLY where the legacy dependencies are.")
        print("   Now we know what to fix.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
