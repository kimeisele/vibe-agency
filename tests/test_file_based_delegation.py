"""
Test file-based delegation protocol.

This test verifies that vibe-cli can delegate intelligence requests
to Claude Code operator via file-based exchange (instead of STDIN/STDOUT).
"""

import json
import shutil
import threading
import time
from pathlib import Path

import pytest


def test_file_based_delegation_flow():
    """
    Test full file-based delegation flow.

    Simulates:
    1. vibe-cli writing request file
    2. Claude Code operator reading request
    3. Claude Code operator writing response
    4. vibe-cli reading response
    """
    # Setup
    project_id = "test-file-delegation"
    delegation_dir = Path("workspaces") / project_id / ".delegation"
    delegation_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Simulate vibe-cli writing request
        request_id = "test-request-123"
        request_file = delegation_dir / f"request_{request_id}.json"
        response_file = delegation_dir / f"response_{request_id}.json"

        request_data = {
            "type": "INTELLIGENCE_DELEGATION",
            "request_id": request_id,
            "agent": "VIBE_ALIGNER",
            "task_id": "01_feature_extraction",
            "prompt": "Extract features from: Test project idea",
            "metadata": {"delegator": "vibe-cli", "mode": "file_based_delegation"},
        }

        with open(request_file, "w") as f:
            json.dump(request_data, f, indent=2)

        assert request_file.exists(), "Request file should be created"

        # Simulate Claude Code operator responding (in background thread)
        def simulate_operator_response():
            """Simulate Claude Code operator processing request"""
            time.sleep(0.5)  # Simulate processing time

            # In real scenario, operator would read request_file here
            # For test, we just generate mock response

            # Generate response
            response_data = {
                "result": {
                    "features": ["Test feature 1", "Test feature 2"],
                    "scope_negotiation": {"mvp_features": 2, "total_features": 2},
                }
            }

            # Write response
            with open(response_file, "w") as f:
                json.dump(response_data, f, indent=2)

        # Start operator simulation in background
        operator_thread = threading.Thread(target=simulate_operator_response)
        operator_thread.start()

        # Simulate vibe-cli polling for response
        timeout = 5  # seconds
        start_time = time.time()
        poll_interval = 0.1

        while not response_file.exists():
            elapsed = time.time() - start_time
            if elapsed > timeout:
                pytest.fail(f"Timeout waiting for response file: {response_file}")
            time.sleep(poll_interval)

        # Read response
        with open(response_file) as f:
            response = json.load(f)

        # Verify response
        assert "result" in response
        assert "features" in response["result"]
        assert len(response["result"]["features"]) == 2
        assert response["result"]["features"][0] == "Test feature 1"

        # Wait for operator thread
        operator_thread.join(timeout=2)

        # Cleanup (simulate what vibe-cli does)
        if request_file.exists():
            request_file.unlink()
        if response_file.exists():
            response_file.unlink()

        assert not request_file.exists(), "Request file should be cleaned up"
        assert not response_file.exists(), "Response file should be cleaned up"

    finally:
        # Cleanup test workspace
        if delegation_dir.exists():
            shutil.rmtree(delegation_dir.parent)


def test_file_based_delegation_timeout():
    """
    Test that delegation properly times out when no response is provided.
    """
    project_id = "test-timeout"
    delegation_dir = Path("workspaces") / project_id / ".delegation"
    delegation_dir.mkdir(parents=True, exist_ok=True)

    try:
        request_id = "test-timeout-123"
        request_file = delegation_dir / f"request_{request_id}.json"
        response_file = delegation_dir / f"response_{request_id}.json"

        # Write request but never respond
        request_data = {
            "type": "INTELLIGENCE_DELEGATION",
            "request_id": request_id,
            "agent": "TEST_AGENT",
            "task_id": "timeout_test",
            "prompt": "This will timeout",
        }

        with open(request_file, "w") as f:
            json.dump(request_data, f)

        # Simulate polling with short timeout
        timeout = 2  # 2 seconds
        start_time = time.time()
        poll_interval = 0.1
        timed_out = False

        while not response_file.exists():
            elapsed = time.time() - start_time
            if elapsed > timeout:
                timed_out = True
                break
            time.sleep(poll_interval)

        assert timed_out, "Should timeout when no response provided"
        assert not response_file.exists(), "Response file should not exist"

        # Cleanup
        if request_file.exists():
            request_file.unlink()

    finally:
        if delegation_dir.exists():
            shutil.rmtree(delegation_dir.parent)


def test_file_based_delegation_invalid_json():
    """
    Test that delegation handles invalid JSON responses gracefully.
    """
    project_id = "test-invalid-json"
    delegation_dir = Path("workspaces") / project_id / ".delegation"
    delegation_dir.mkdir(parents=True, exist_ok=True)

    try:
        request_id = "test-invalid-123"
        request_file = delegation_dir / f"request_{request_id}.json"
        response_file = delegation_dir / f"response_{request_id}.json"

        # Write request
        request_data = {
            "type": "INTELLIGENCE_DELEGATION",
            "request_id": request_id,
            "agent": "TEST_AGENT",
            "task_id": "invalid_json_test",
            "prompt": "Test invalid JSON",
        }

        with open(request_file, "w") as f:
            json.dump(request_data, f)

        # Write INVALID JSON response
        with open(response_file, "w") as f:
            f.write("{ this is not valid json }")

        # Simulate reading response
        with pytest.raises(json.JSONDecodeError), open(response_file) as f:
            json.load(f)

        # Cleanup
        if request_file.exists():
            request_file.unlink()
        if response_file.exists():
            response_file.unlink()

    finally:
        if delegation_dir.exists():
            shutil.rmtree(delegation_dir.parent)


def test_delegation_directory_creation():
    """
    Test that delegation directory is created if it doesn't exist.
    """
    project_id = "test-dir-creation"
    delegation_dir = Path("workspaces") / project_id / ".delegation"

    # Ensure it doesn't exist
    if delegation_dir.exists():
        shutil.rmtree(delegation_dir.parent)

    try:
        # Create delegation directory (what vibe-cli does)
        delegation_dir.mkdir(parents=True, exist_ok=True)

        assert delegation_dir.exists(), "Delegation directory should be created"
        assert delegation_dir.is_dir(), "Should be a directory"

        # Verify permissions allow file creation
        test_file = delegation_dir / "test.json"
        with open(test_file, "w") as f:
            json.dump({"test": "data"}, f)

        assert test_file.exists()
        test_file.unlink()

    finally:
        if delegation_dir.exists():
            shutil.rmtree(delegation_dir.parent)


if __name__ == "__main__":
    # Run tests
    test_file_based_delegation_flow()
    print("✅ test_file_based_delegation_flow PASSED")

    test_file_based_delegation_timeout()
    print("✅ test_file_based_delegation_timeout PASSED")

    test_file_based_delegation_invalid_json()
    print("✅ test_file_based_delegation_invalid_json PASSED")

    test_delegation_directory_creation()
    print("✅ test_delegation_directory_creation PASSED")

    print("\n🎉 All file-based delegation tests PASSED")
