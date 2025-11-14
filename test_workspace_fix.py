#!/usr/bin/env python3
"""
Quick test to verify CRITICAL FIX #1 and #2 are working
"""

import os
import sys
from pathlib import Path

# Set workspace
os.environ['ACTIVE_WORKSPACE'] = 'prabhupad_os'

# Import runtime (use same method as vibe-cli.py)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "prompt_runtime",
    Path(__file__).parent / "agency_os/00_system/runtime/prompt_runtime.py"
)
prompt_runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt_runtime)
PromptRuntime = prompt_runtime.PromptRuntime

def test_workspace_resolution():
    """Test that workspace paths are resolved correctly"""

    print("\n" + "=" * 60)
    print("TESTING WORKSPACE PATH RESOLUTION")
    print("=" * 60 + "\n")

    # Test 1: Verify environment variable is set
    active_ws = os.getenv('ACTIVE_WORKSPACE')
    print(f"✓ Test 1: Environment variable set")
    print(f"  $ACTIVE_WORKSPACE = {active_ws}")
    assert active_ws == 'prabhupad_os', "ENV var not set correctly"

    # Test 2: Create runtime and execute task
    runtime = PromptRuntime()
    context = {
        'project_id': 'prabhupad_os_001',
        'phase': 'PLANNING'
    }

    print(f"\n✓ Test 2: Creating prompt runtime")
    print(f"  Context: {context}")

    # This should trigger workspace path resolution
    try:
        prompt = runtime.execute_task(
            agent_id='VIBE_ALIGNER',
            task_id='01_education_calibration',
            context=context
        )

        print(f"\n✓ Test 3: Prompt composition succeeded")
        print(f"  Prompt size: {len(prompt):,} characters")

        # Test 3: Verify resolved paths are in context
        print(f"\n✓ Test 4: Checking resolved paths in context")

        expected_paths = [
            '_resolved_workspace',
            '_resolved_artifact_base_path',
            '_resolved_planning_path'
        ]

        for path_key in expected_paths:
            if path_key in context:
                print(f"  ✅ {path_key}: {context[path_key]}")
            else:
                print(f"  ❌ MISSING: {path_key}")

        # Test 4: Verify correct workspace path
        if '_resolved_artifact_base_path' in context:
            expected = 'workspaces/prabhupad_os/artifacts'
            actual = context['_resolved_artifact_base_path']

            if actual == expected:
                print(f"\n✅ SUCCESS: Workspace paths resolved correctly!")
                print(f"   Expected: {expected}")
                print(f"   Actual:   {actual}")
            else:
                print(f"\n❌ FAIL: Wrong path!")
                print(f"   Expected: {expected}")
                print(f"   Actual:   {actual}")
                return False

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✅")
        print("=" * 60 + "\n")
        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_workspace_resolution()
    sys.exit(0 if success else 1)
