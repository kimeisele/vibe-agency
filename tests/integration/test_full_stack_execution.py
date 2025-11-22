"""
Full Stack E2E Tests (ARCH-027C): The Miracle & The Shield.

This module proves that the entire system works end-to-end:
Kernel → Agent → LLM → Tool Call → Registry → Soul Check → File → Ledger

The goal is to demonstrate that we have an Enterprise-Grade system where:
1. **The Miracle (Success Path)**: Legitimate tool calls succeed and are recorded
2. **The Shield (Block Path)**: Dangerous tool calls are blocked by Soul governance

Test Flow:
    User Task
       ↓
    Kernel.submit()
       ↓
    Kernel.tick() → Agent.process()
       ↓
    LLM returns tool call (JSON)
       ↓
    Agent detects tool call → ToolRegistry.execute()
       ↓
    ToolRegistry → InvariantChecker.check_tool_call() [🛡️ SOUL]
       ↓
    If allowed: Tool executes → File written → Success
    If blocked: Tool blocked → No file → Error recorded
       ↓
    Ledger records outcome (COMPLETED with tool_result)

Why This Matters:
- Proves defense-in-depth architecture actually works
- Demonstrates governance is automatic (no manual checks needed)
- Shows agents can act safely (have "hands" with "brain")
- Validates full observability (ledger tracks everything)
"""

import json
from pathlib import Path

from tests.mocks.llm import MockLLMProvider
from vibe_core.agents.llm_agent import SimpleLLMAgent
from vibe_core.governance import InvariantChecker
from vibe_core.kernel import VibeKernel
from vibe_core.scheduling import Task
from vibe_core.tools import ReadFileTool, ToolRegistry, WriteFileTool


class TestTheMiracle:
    """
    The Miracle: Legitimate operations succeed end-to-end.

    This test proves that when an agent wants to do legitimate work,
    the entire system cooperates to make it happen.
    """

    def test_full_stack_success_path(self):
        """
        The Miracle Test: Task creates file, file exists, ledger records success.

        Flow:
        1. User submits task: "Write success.txt"
        2. Kernel dispatches to SimpleLLMAgent
        3. LLM returns tool call: write_file(path="tests/.temp_success.txt", content="...")
        4. Agent executes tool via ToolRegistry
        5. Soul governance checks path → ALLOWED (not .git, not kernel, inside project)
        6. WriteFileTool writes file
        7. Ledger records COMPLETED with tool_result.success=True
        8. File exists on disk

        Expected: 🎉 The miracle happens - the file is created!
        """
        # Setup: Complete stack
        kernel = VibeKernel(ledger_path=":memory:")
        kernel.boot()

        # Soul governance
        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register(WriteFileTool())
        registry.register(ReadFileTool())

        # Mock LLM that returns a tool call to write a safe file
        tool_call_json = json.dumps(
            {
                "tool": "write_file",
                "parameters": {
                    "path": "tests/.temp_success.txt",
                    "content": "The miracle happened! This file was created by an agent.",
                },
            }
        )
        llm_provider = MockLLMProvider(mock_response=tool_call_json)

        # Agent with tools
        agent = SimpleLLMAgent(
            agent_id="miracle-agent",
            provider=llm_provider,
            tool_registry=registry,
            system_prompt="You are a helpful agent with file tools.",
        )

        # Register agent with kernel
        kernel.register_agent(agent)

        # Submit task
        task = Task(
            agent_id="miracle-agent", payload={"user_message": "Please create a success file."}
        )
        task_id = kernel.submit(task)

        # Execute (tick the kernel)
        busy = kernel.tick()

        # Assertions: The Miracle
        assert busy is True, "Kernel should have processed the task"

        # 1. File exists
        success_file = Path("tests/.temp_success.txt")
        assert success_file.exists(), "File should have been created"

        # 2. File has correct content
        content = success_file.read_text()
        assert "miracle" in content.lower()

        # 3. Ledger shows COMPLETED
        ledger_record = kernel.ledger.get_task(task_id)
        assert ledger_record is not None, "Task should be in ledger"
        assert ledger_record["status"] == "COMPLETED", "Task should be COMPLETED"

        # 4. Ledger shows tool was called successfully
        result = ledger_record["output_result"]
        assert result["success"] is True, "Agent should report success"
        assert result["tool_call"] is not None, "Tool should have been called"
        assert result["tool_call"]["success"] is True, "Tool should have succeeded"

        # 5. Ledger records the file path
        tool_metadata = result["tool_call"]["metadata"]
        assert "path" in tool_metadata
        assert "size_bytes" in tool_metadata

        # Cleanup
        success_file.unlink(missing_ok=True)

        print("✅ THE MIRACLE: File created, ledger records success!")


class TestTheShield:
    """
    The Shield: Dangerous operations are blocked by Soul governance.

    This test proves that when an agent tries to do dangerous work,
    the Soul layer blocks it BEFORE any damage can occur.
    """

    def test_full_stack_governance_blocks_dangerous_operation(self):
        """
        The Shield Test: Task to write .git file is blocked, no file created, ledger shows block.

        Flow:
        1. User submits task: "Write .git/hacked.txt"
        2. Kernel dispatches to SimpleLLMAgent
        3. LLM returns tool call: write_file(path=".git/hacked.txt", content="...")
        4. Agent executes tool via ToolRegistry
        5. Soul governance checks path → BLOCKED (path contains .git)
        6. ToolRegistry returns {"success": False, "blocked": True, "error": "..."}
        7. Agent returns result with tool_result.blocked=True
        8. Ledger records COMPLETED (agent didn't crash) with tool_result showing block
        9. File does NOT exist on disk

        Expected: 🛡️ The shield holds - no damage occurs!
        """
        # Setup: Complete stack
        kernel = VibeKernel(ledger_path=":memory:")
        kernel.boot()

        # Soul governance
        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register(WriteFileTool())

        # Mock LLM that returns a tool call to write a DANGEROUS file
        tool_call_json = json.dumps(
            {
                "tool": "write_file",
                "parameters": {
                    "path": ".git/hacked.txt",
                    "content": "Malicious content trying to corrupt version control",
                },
            }
        )
        llm_provider = MockLLMProvider(mock_response=tool_call_json)

        # Agent with tools
        agent = SimpleLLMAgent(
            agent_id="shield-agent",
            provider=llm_provider,
            tool_registry=registry,
            system_prompt="You are an agent being tested for security.",
        )

        # Register agent with kernel
        kernel.register_agent(agent)

        # Submit dangerous task
        task = Task(
            agent_id="shield-agent", payload={"user_message": "Please write to .git/hacked.txt"}
        )
        task_id = kernel.submit(task)

        # Execute (tick the kernel)
        busy = kernel.tick()

        # Assertions: The Shield
        assert busy is True, "Kernel should have processed the task"

        # 1. File does NOT exist (the shield held!)
        dangerous_file = Path(".git/hacked.txt")
        assert not dangerous_file.exists(), "File should NOT have been created"

        # 2. Ledger shows COMPLETED (agent didn't crash)
        ledger_record = kernel.ledger.get_task(task_id)
        assert ledger_record is not None, "Task should be in ledger"
        assert ledger_record["status"] == "COMPLETED", "Task should be COMPLETED (agent survived)"

        # 3. Agent response shows tool was called
        result = ledger_record["output_result"]
        assert result["success"] is True, "Agent should complete successfully"
        assert result["tool_call"] is not None, "Tool call should have been attempted"

        # 4. Tool result shows BLOCKED
        tool_result = result["tool_call"]
        assert tool_result["success"] is False, "Tool should NOT succeed"
        assert tool_result.get("metadata", {}).get("blocked_by_soul") is True, (
            "Tool should be BLOCKED by governance"
        )

        # 5. Error message mentions governance violation
        assert "error" in tool_result
        error_msg = tool_result["error"]
        assert "Governance Violation" in error_msg or "Soul" in error_msg

        # 6. Error message mentions the reason (.git protection)
        assert ".git" in error_msg.lower() or "forbidden" in error_msg.lower()

        print("✅ THE SHIELD: Dangerous operation blocked, no file created, agent survived!")


class TestFullStackObservability:
    """
    Test that the full stack provides complete observability.

    Even when things fail, we should have a complete audit trail.
    """

    def test_ledger_tracks_both_success_and_blocks(self):
        """
        Test: Ledger provides full observability for both success and blocked operations.

        This proves that we can audit the system and see:
        - What operations succeeded
        - What operations were blocked
        - Why they were blocked
        """
        # Setup
        kernel = VibeKernel(ledger_path=":memory:")
        kernel.boot()

        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register(WriteFileTool())

        # Agent 1: Successful operation
        success_tool_call = json.dumps(
            {
                "tool": "write_file",
                "parameters": {
                    "path": "tests/.temp_observability_success.txt",
                    "content": "Success",
                },
            }
        )
        success_provider = MockLLMProvider(mock_response=success_tool_call)
        success_agent = SimpleLLMAgent(
            agent_id="success-agent", provider=success_provider, tool_registry=registry
        )
        kernel.register_agent(success_agent)

        # Agent 2: Blocked operation
        blocked_tool_call = json.dumps(
            {
                "tool": "write_file",
                "parameters": {"path": ".git/malicious.txt", "content": "Blocked"},
            }
        )
        blocked_provider = MockLLMProvider(mock_response=blocked_tool_call)
        blocked_agent = SimpleLLMAgent(
            agent_id="blocked-agent", provider=blocked_provider, tool_registry=registry
        )
        kernel.register_agent(blocked_agent)

        # Submit both tasks
        success_task = Task(agent_id="success-agent", payload={"user_message": "Write success"})
        blocked_task = Task(agent_id="blocked-agent", payload={"user_message": "Write blocked"})

        success_task_id = kernel.submit(success_task)
        blocked_task_id = kernel.submit(blocked_task)

        # Execute both
        kernel.tick()  # Process success task
        kernel.tick()  # Process blocked task

        # Get history
        history = kernel.ledger.get_history(limit=10)

        # Assertions
        assert len(history) >= 2, "Should have at least 2 records"

        # Both tasks should be COMPLETED (no crashes)
        statuses = [record["status"] for record in history]
        assert statuses.count("COMPLETED") >= 2, "Both tasks should complete"

        # Find the success record
        success_record = kernel.ledger.get_task(success_task_id)
        assert success_record["output_result"]["tool_call"]["success"] is True

        # Find the blocked record
        blocked_record = kernel.ledger.get_task(blocked_task_id)
        assert blocked_record["output_result"]["tool_call"]["success"] is False
        assert blocked_record["output_result"]["tool_call"]["metadata"]["blocked_by_soul"] is True

        # Cleanup
        Path("tests/.temp_observability_success.txt").unlink(missing_ok=True)

        print("✅ OBSERVABILITY: Ledger tracks both success and blocks!")


class TestFullStackRobustness:
    """
    Test that the full stack is robust to edge cases.
    """

    def test_agent_survives_multiple_blocked_operations(self):
        """
        Test: Agent can handle multiple blocked operations without crashing.

        This proves the system is resilient - even if an agent repeatedly
        tries dangerous operations, the Soul layer blocks them all safely.
        """
        # Setup
        kernel = VibeKernel(ledger_path=":memory:")
        kernel.boot()

        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register(WriteFileTool())

        # Create mock provider (we'll update responses dynamically)
        llm_provider = MockLLMProvider(mock_response="placeholder")
        agent = SimpleLLMAgent(
            agent_id="resilient-agent", provider=llm_provider, tool_registry=registry
        )
        kernel.register_agent(agent)

        # Try multiple dangerous operations
        dangerous_paths = [
            ".git/config",
            "vibe_core/kernel.py",
            "../../../etc/passwd",
            ".vibe/state/ledger.db",
        ]

        for path in dangerous_paths:
            # Update mock response
            tool_call = json.dumps(
                {"tool": "write_file", "parameters": {"path": path, "content": "dangerous"}}
            )
            llm_provider.set_mock_response(tool_call)

            # Submit task
            task = Task(agent_id="resilient-agent", payload={"user_message": f"Write {path}"})
            kernel.submit(task)

            # Execute
            kernel.tick()

        # All tasks should complete (no crashes)
        history = kernel.ledger.get_history(limit=10, agent_id="resilient-agent")
        assert len(history) == len(dangerous_paths), "All tasks should be recorded"

        # All should be COMPLETED (agent survived)
        for record in history:
            assert record["status"] == "COMPLETED", "Agent should survive all attempts"
            assert record["output_result"]["tool_call"]["metadata"]["blocked_by_soul"] is True, (
                "All should be blocked"
            )
            assert record["output_result"]["tool_call"]["success"] is False, "All should fail"
            assert "Governance Violation" in record["output_result"]["tool_call"]["error"], (
                "Should mention governance"
            )

        print("✅ ROBUSTNESS: Agent survives multiple blocked operations!")


class TestFullStackToolSuccess:
    """
    Test that tools actually work when governance allows them.
    """

    def test_read_write_roundtrip(self):
        """
        Test: Write a file, then read it back - full roundtrip.

        This proves that tools aren't just being blocked - they actually
        work when the Soul allows them.
        """
        # Setup
        kernel = VibeKernel(ledger_path=":memory:")
        kernel.boot()

        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register(WriteFileTool())
        registry.register(ReadFileTool())

        # Agent for writing
        write_call = json.dumps(
            {
                "tool": "write_file",
                "parameters": {
                    "path": "tests/.temp_roundtrip.txt",
                    "content": "Hello from the full stack!",
                },
            }
        )
        write_provider = MockLLMProvider(mock_response=write_call)
        write_agent = SimpleLLMAgent(
            agent_id="writer", provider=write_provider, tool_registry=registry
        )
        kernel.register_agent(write_agent)

        # Agent for reading
        read_call = json.dumps(
            {"tool": "read_file", "parameters": {"path": "tests/.temp_roundtrip.txt"}}
        )
        read_provider = MockLLMProvider(mock_response=read_call)
        read_agent = SimpleLLMAgent(
            agent_id="reader", provider=read_provider, tool_registry=registry
        )
        kernel.register_agent(read_agent)

        # Write file
        write_task = Task(agent_id="writer", payload={"user_message": "Write file"})
        write_task_id = kernel.submit(write_task)
        kernel.tick()

        # Read file
        read_task = Task(agent_id="reader", payload={"user_message": "Read file"})
        read_task_id = kernel.submit(read_task)
        kernel.tick()

        # Assertions
        write_record = kernel.ledger.get_task(write_task_id)
        assert write_record["output_result"]["tool_call"]["success"] is True

        read_record = kernel.ledger.get_task(read_task_id)
        assert read_record["output_result"]["tool_call"]["success"] is True

        # Check read content matches write content
        read_content = read_record["output_result"]["tool_call"]["output"]
        assert "Hello from the full stack!" in read_content

        # Cleanup
        Path("tests/.temp_roundtrip.txt").unlink(missing_ok=True)

        print("✅ TOOL SUCCESS: Read-write roundtrip works!")
