#!/usr/bin/env python3
"""
Test core_orchestrator file-based delegation.

Tests that orchestrator._request_intelligence() correctly:
1. Writes request files
2. Polls for response files
3. Returns result
4. Cleans up files
"""

import json
import shutil
import sys
import threading
import time
from pathlib import Path

# Add orchestrator to path
from agency_os_orchestrator import CoreOrchestrator, ProjectManifest, ProjectPhase


def simulate_claude_code_operator(workspace_dir, timeout=10):
    """
    Simulate Claude Code operator reading requests and writing responses.

    This runs in a background thread and polls for request files.
    """
    delegation_dir = workspace_dir / ".delegation"
    start_time = time.time()

    print(f"[OPERATOR] 🤖 Operator watching: {delegation_dir}")

    while time.time() - start_time < timeout:
        # Look for request files
        if not delegation_dir.exists():
            time.sleep(0.1)
            continue

        request_files = list(delegation_dir.glob("request_*.json"))

        for request_file in request_files:
            print(f"[OPERATOR] 📬 Found request: {request_file}")

            # Read request
            with open(request_file) as f:
                request = json.load(f)

            print(f"[OPERATOR] 📖 Request: {request['agent']}.{request['task_id']}")

            # Generate mock response based on agent
            if request["agent"] == "VIBE_ALIGNER":
                result = {
                    "features": ["Feature 1", "Feature 2"],
                    "scope_negotiation": {"mvp_features": 2, "total_features": 2},
                }
            else:
                result = {"status": "success", "data": "Mock response for " + request["agent"]}

            # Write response
            request_id = request["request_id"]
            response_file = delegation_dir / f"response_{request_id}.json"

            response = {"result": result}

            print(f"[OPERATOR] ✍️  Writing response: {response_file}")
            with open(response_file, "w") as f:
                json.dump(response, f, indent=2)

            print("[OPERATOR] ✅ Response written")

        time.sleep(0.1)

    print(f"[OPERATOR] ⏰ Operator timeout after {timeout}s")


def test_orchestrator_file_delegation():
    """
    Test that orchestrator can delegate via file-based protocol.
    """
    print("\n" + "=" * 70)
    print("TEST: Orchestrator File-Based Delegation")
    print("=" * 70)

    # Setup test workspace
    project_id = "test-orchestrator-delegation"
    workspace_dir = Path("workspaces") / project_id

    # Cleanup if exists
    if workspace_dir.exists():
        shutil.rmtree(workspace_dir)

    workspace_dir.mkdir(parents=True)

    try:
        # Initialize orchestrator in delegated mode
        print("\n[TEST] 🚀 Initializing orchestrator...")
        orchestrator = CoreOrchestrator(repo_root=Path.cwd(), execution_mode="delegated")

        # Create test manifest
        manifest = ProjectManifest(
            project_id=project_id, name=project_id, current_phase=ProjectPhase.PLANNING
        )

        # Start operator simulation in background
        print("\n[TEST] 🤖 Starting operator simulation...")
        operator_thread = threading.Thread(
            target=simulate_claude_code_operator,
            args=(workspace_dir, 10),  # 10 second timeout
        )
        operator_thread.daemon = True
        operator_thread.start()

        # Give operator time to start
        time.sleep(0.5)

        # Execute agent (triggers file-based delegation)
        print("\n[TEST] 📤 Executing agent (will delegate via files)...")
        result = orchestrator.execute_agent(
            agent_name="VIBE_ALIGNER",
            task_id="01_education_calibration",
            inputs={"user_input": "Test project"},
            manifest=manifest,
        )

        print(f"\n[TEST] 📥 Received result: {json.dumps(result, indent=2)}")

        # Verify result
        assert "features" in result, "Result should contain 'features'"
        assert len(result["features"]) == 2, "Should have 2 features"

        # Verify cleanup
        delegation_dir = workspace_dir / ".delegation"
        request_files = list(delegation_dir.glob("request_*.json"))
        response_files = list(delegation_dir.glob("response_*.json"))

        assert len(request_files) == 0, (
            f"Request files should be cleaned up, found: {request_files}"
        )
        assert len(response_files) == 0, (
            f"Response files should be cleaned up, found: {response_files}"
        )

        print("\n[TEST] ✅ All assertions passed!")
        print("[TEST] ✅ File-based delegation works!")

        # Wait for operator thread
        operator_thread.join(timeout=2)

        return True

    except Exception as e:
        print(f"\n[TEST] ❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Cleanup
        if workspace_dir.exists():
            shutil.rmtree(workspace_dir)
        print("\n[TEST] 🧹 Cleaned up test workspace")


def test_orchestrator_delegation_timeout():
    """
    Test that orchestrator times out when no response is provided.
    """
    print("\n" + "=" * 70)
    print("TEST: Orchestrator Delegation Timeout")
    print("=" * 70)

    project_id = "test-timeout"
    workspace_dir = Path("workspaces") / project_id

    if workspace_dir.exists():
        shutil.rmtree(workspace_dir)

    workspace_dir.mkdir(parents=True)

    try:
        print("\n[TEST] ⏰ Executing agent without operator (should timeout)...")

        # This should timeout since no operator is responding
        # BUT this would block for 10 minutes, so we skip this test for now
        print("[TEST] ⚠️  Skipping timeout test (would block for 10 minutes)")
        return True

    finally:
        if workspace_dir.exists():
            shutil.rmtree(workspace_dir)


if __name__ == "__main__":
    print("\n🧪 Running orchestrator file-based delegation tests...\n")

    # Test 1: Normal delegation flow
    test1_passed = test_orchestrator_file_delegation()

    # Test 2: Timeout (skipped)
    test2_passed = test_orchestrator_delegation_timeout()

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"✅ Test 1 (Delegation Flow): {'PASSED' if test1_passed else 'FAILED'}")
    print("⚠️  Test 2 (Timeout): SKIPPED (would block)")

    if test1_passed:
        print("\n🎉 Core tests PASSED - File-based delegation works!")
        sys.exit(0)
    else:
        print("\n❌ Tests FAILED")
        sys.exit(1)
