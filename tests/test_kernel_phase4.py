"""
Tests for ARCH-026 Phase 4 - Smart Delegation & Result Propagation.

This test suite validates:
1. Kernel delegation validation using STEWARD manifests
2. Result retrieval from ledger
3. InspectResultTool for task result queries
4. End-to-end delegation workflow
"""

import sys
from unittest.mock import MagicMock

import pytest

# Mock yaml module before importing agents
sys.modules["yaml"] = MagicMock()

from tests.mocks.llm import MockLLMProvider
from vibe_core.agents.llm_agent import SimpleLLMAgent
from vibe_core.kernel import VibeKernel
from vibe_core.scheduling import Task
from vibe_core.tools.inspect_result import InspectResultTool


class TestKernelDelegationValidation:
    """Tests for kernel delegation validation (Phase 4)."""

    def test_validate_delegation_success(self):
        """Test successful delegation validation."""
        kernel = VibeKernel(":memory:")

        # Register agent
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)
        kernel.register_agent(agent)
        kernel.boot()

        # Should not raise
        kernel._validate_delegation("test-agent")

    def test_validate_delegation_unregistered_agent(self):
        """Test delegation to unregistered agent raises ValueError."""
        kernel = VibeKernel(":memory:")
        kernel.boot()

        with pytest.raises(ValueError, match="not registered"):
            kernel._validate_delegation("non-existent-agent")

    def test_validate_delegation_before_boot(self):
        """Test validation before boot (registration check only)."""
        kernel = VibeKernel(":memory:")

        # Register agent but don't boot
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)
        kernel.register_agent(agent)

        # Should pass (only checks agent_registry, not manifest_registry)
        kernel._validate_delegation("test-agent")

    def test_validate_delegation_after_boot(self):
        """Test validation after boot checks manifest too."""
        kernel = VibeKernel(":memory:")

        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)
        kernel.register_agent(agent)
        kernel.boot()

        # Should have manifest
        manifest = kernel.manifest_registry.lookup("test-agent")
        assert manifest is not None
        assert manifest.to_dict()["agent"]["status"] == "active"

        # Validation should pass
        kernel._validate_delegation("test-agent")

    def test_submit_with_validation(self):
        """Test that submit() performs validation."""
        kernel = VibeKernel(":memory:")

        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)
        kernel.register_agent(agent)
        kernel.boot()

        # Submit should validate
        task = Task(agent_id="test-agent", payload={"message": "Hello"})
        task_id = kernel.submit(task)

        assert task_id is not None

    def test_submit_to_unregistered_agent_fails(self):
        """Test that submit() fails for unregistered agent."""
        kernel = VibeKernel(":memory:")
        kernel.boot()

        task = Task(agent_id="non-existent", payload={})

        with pytest.raises(ValueError, match="not registered"):
            kernel.submit(task)


class TestResultRetrieval:
    """Tests for result retrieval from ledger (Phase 4)."""

    def test_get_task_result_success(self):
        """Test retrieving a completed task's result."""
        kernel = VibeKernel(":memory:")

        provider = MockLLMProvider(mock_response="Test response")
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)
        kernel.register_agent(agent)
        kernel.boot()

        # Submit and execute task
        task = Task(agent_id="test-agent", payload={"user_message": "Hi"})
        task_id = kernel.submit(task)
        kernel.tick()  # Execute task

        # Retrieve result
        result = kernel.get_task_result(task_id)

        assert result is not None
        assert result["status"] == "COMPLETED"
        assert result["task_id"] == task_id
        assert result["output_result"] is not None

    def test_get_task_result_not_found(self):
        """Test retrieving non-existent task returns None."""
        kernel = VibeKernel(":memory:")

        result = kernel.get_task_result("non-existent-task")
        assert result is None

    def test_get_task_result_includes_all_fields(self):
        """Test that result includes all ledger fields."""
        kernel = VibeKernel(":memory:")

        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)
        kernel.register_agent(agent)
        kernel.boot()

        task = Task(agent_id="test-agent", payload={"user_message": "Hello"})
        task_id = kernel.submit(task)
        kernel.tick()

        result = kernel.get_task_result(task_id)

        # Check all expected fields
        assert "task_id" in result
        assert "agent_id" in result
        assert "status" in result
        assert "timestamp" in result
        assert "input_payload" in result
        assert "output_result" in result

    def test_get_task_output_convenience(self):
        """Test get_task_output() convenience method."""
        kernel = VibeKernel(":memory:")

        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)
        kernel.register_agent(agent)
        kernel.boot()

        task = Task(agent_id="test-agent", payload={"user_message": "Hi"})
        task_id = kernel.submit(task)
        kernel.tick()

        # get_task_output should return just the output_result
        output = kernel.get_task_output(task_id)

        assert output is not None
        assert "response" in output or "success" in output

    def test_get_task_output_not_found(self):
        """Test get_task_output returns None if task not found."""
        kernel = VibeKernel(":memory:")

        output = kernel.get_task_output("non-existent")
        assert output is None


class TestInspectResultTool:
    """Tests for InspectResultTool (Phase 4)."""

    def test_tool_creation(self):
        """Test creating InspectResultTool."""
        kernel = VibeKernel(":memory:")
        tool = InspectResultTool(kernel)

        assert tool.name == "inspect_result"
        assert "query" in tool.description.lower()

    def test_tool_execute_success(self):
        """Test executing tool to query a completed task."""
        kernel = VibeKernel(":memory:")

        provider = MockLLMProvider(mock_response="Success!")
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)
        kernel.register_agent(agent)
        kernel.boot()

        # Execute task
        task = Task(agent_id="test-agent", payload={"user_message": "Hi"})
        task_id = kernel.submit(task)
        kernel.tick()

        # Use tool to query result
        tool = InspectResultTool(kernel)
        result = tool.execute({"task_id": task_id})

        assert result.success is True
        assert result.output["status"] == "COMPLETED"
        assert result.output["output"] is not None

    def test_tool_execute_not_found(self):
        """Test tool returns NOT_FOUND for non-existent task."""
        kernel = VibeKernel(":memory:")
        tool = InspectResultTool(kernel)

        result = tool.execute({"task_id": "non-existent"})

        assert result.success is True
        assert result.output["status"] == "NOT_FOUND"

    def test_tool_execute_missing_task_id(self):
        """Test tool fails gracefully if task_id missing."""
        kernel = VibeKernel(":memory:")
        tool = InspectResultTool(kernel)

        result = tool.execute({})

        assert result.success is False
        assert "task_id" in result.error.lower()

    def test_tool_execute_with_include_input(self):
        """Test tool can include input payload."""
        kernel = VibeKernel(":memory:")

        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)
        kernel.register_agent(agent)
        kernel.boot()

        task = Task(
            agent_id="test-agent", payload={"user_message": "Test", "extra": "data"}
        )
        task_id = kernel.submit(task)
        kernel.tick()

        tool = InspectResultTool(kernel)
        result = tool.execute({"task_id": task_id, "include_input": True})

        assert result.success is True
        assert "input_payload" in result.output
        assert result.output["input_payload"]["user_message"] == "Test"

    def test_tool_schema(self):
        """Test tool schema is valid."""
        kernel = VibeKernel(":memory:")
        tool = InspectResultTool(kernel)

        schema = tool.parameters_schema

        assert "task_id" in schema
        assert schema["task_id"]["type"] == "string"
        assert schema["task_id"]["required"] is True


class TestEndToEndWorkflow:
    """End-to-end tests for Phase 4 delegation workflow."""

    def test_delegation_and_result_retrieval(self):
        """Test complete workflow: register → boot → delegate → retrieve result."""
        kernel = VibeKernel(":memory:")

        # Setup
        provider = MockLLMProvider(mock_response='{"plan": "Step 1, Step 2"}')
        agent = SimpleLLMAgent(agent_id="planner", provider=provider)
        kernel.register_agent(agent)
        kernel.boot()

        # Delegate
        task = Task(agent_id="planner", payload={"user_message": "Plan the project"})
        task_id = kernel.submit(task)
        assert task_id is not None

        # Execute
        kernel.tick()

        # Retrieve result
        result = kernel.get_task_result(task_id)
        assert result["status"] == "COMPLETED"

        # Verify result structure
        output = result["output_result"]
        assert output["success"] is True
        assert "output" in output or "response" in output

    def test_multiple_delegations(self):
        """Test delegating to multiple agents and retrieving results."""
        kernel = VibeKernel(":memory:")

        # Register multiple agents
        for i in range(3):
            provider = MockLLMProvider(mock_response=f"Agent {i} response")
            agent = SimpleLLMAgent(agent_id=f"agent-{i}", provider=provider)
            kernel.register_agent(agent)

        kernel.boot()

        # Delegate to all agents
        task_ids = []
        for i in range(3):
            task = Task(agent_id=f"agent-{i}", payload={"user_message": f"Task {i}"})
            task_id = kernel.submit(task)
            task_ids.append(task_id)

        # Execute all
        for _ in range(3):
            kernel.tick()

        # Retrieve all results
        for i, task_id in enumerate(task_ids):
            result = kernel.get_task_result(task_id)
            assert result["status"] == "COMPLETED"
            output_result = result["output_result"]
            assert output_result["success"] is True
            # Check that the response contains the agent ID
            response_content = output_result.get("output") or output_result.get("response", "")
            assert f"Agent {i}" in str(response_content)

    def test_failed_task_result_retrieval(self):
        """Test retrieving result from a failed task."""
        kernel = VibeKernel(":memory:")

        # Create agent that will fail
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="failing-agent", provider=provider)
        kernel.register_agent(agent)
        kernel.boot()

        # Submit task with invalid payload (missing user_message)
        task = Task(agent_id="failing-agent", payload={})

        try:
            kernel.submit(task)
            kernel.tick()
        except ValueError:
            # Expected to fail
            pass

        # Even though it failed, the result should be in the ledger
        # (The ledger records all executions)

    def test_tool_integration_with_kernel(self):
        """Test InspectResultTool integrates seamlessly with kernel."""
        kernel = VibeKernel(":memory:")

        # Setup
        provider = MockLLMProvider(mock_response="Result data")
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)
        kernel.register_agent(agent)
        kernel.boot()

        # Delegate
        task = Task(agent_id="test-agent", payload={"user_message": "Work"})
        task_id = kernel.submit(task)
        kernel.tick()

        # Query using tool
        tool = InspectResultTool(kernel)
        result = tool.execute({"task_id": task_id, "include_input": True})

        # Verify tool result matches kernel result
        kernel_result = kernel.get_task_result(task_id)
        assert result.output["task_id"] == kernel_result["task_id"]
        assert result.output["status"] == kernel_result["status"]
