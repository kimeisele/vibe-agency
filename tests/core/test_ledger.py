"""
Unit tests for the vibe-agency ledger (ARCH-024).

Tests the task execution history ledger and SQLite persistence.
"""

import json
from typing import Any

import pytest

from vibe_core.agent_protocol import VibeAgent
from vibe_core.kernel import VibeKernel
from vibe_core.ledger import VibeLedger
from vibe_core.scheduling import Task


class TestAgent(VibeAgent):
    """Simple test agent for ledger integration tests."""

    def __init__(self, agent_id: str):
        self._agent_id = agent_id

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def capabilities(self) -> list[str]:
        return ["test"]

    def process(self, task: Task) -> Any:
        return {"status": "success", "data": task.payload}


class FailingTestAgent(VibeAgent):
    """Test agent that always raises an exception."""

    def __init__(self, agent_id: str):
        self._agent_id = agent_id

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def capabilities(self) -> list[str]:
        return ["fail"]

    def process(self, task: Task) -> Any:
        raise RuntimeError("Test failure")


class TestLedgerBasics:
    """Test 1: Basic ledger operations."""

    def test_ledger_initialization(self):
        """Test that ledger initializes with in-memory database."""
        ledger = VibeLedger(":memory:")
        assert ledger.db_path == ":memory:"
        assert ledger.conn is not None

        # Verify schema was created
        cursor = ledger.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='task_history'")
        assert cursor.fetchone() is not None

        ledger.close()

    def test_record_completion_creates_row(self):
        """Test that record_completion creates a row in the database."""
        ledger = VibeLedger(":memory:")
        task = Task(agent_id="test-agent", payload={"action": "test"})
        result = {"status": "success"}

        ledger.record_completion(task, result)

        # Verify row exists
        cursor = ledger.conn.cursor()
        cursor.execute("SELECT * FROM task_history WHERE task_id = ?", (task.id,))
        row = cursor.fetchone()

        assert row is not None
        assert row["task_id"] == task.id
        assert row["agent_id"] == "test-agent"
        assert row["status"] == "COMPLETED"
        assert json.loads(row["input_payload"]) == {"action": "test"}
        assert json.loads(row["output_result"]) == {"status": "success"}
        assert row["timestamp"] is not None

        ledger.close()

    def test_record_failure_creates_row(self):
        """Test that record_failure creates a FAILED row with error message."""
        ledger = VibeLedger(":memory:")
        task = Task(agent_id="test-agent", payload={"action": "fail"})
        error_msg = "Something went wrong"

        ledger.record_failure(task, error_msg)

        # Verify row exists
        cursor = ledger.conn.cursor()
        cursor.execute("SELECT * FROM task_history WHERE task_id = ?", (task.id,))
        row = cursor.fetchone()

        assert row is not None
        assert row["task_id"] == task.id
        assert row["status"] == "FAILED"
        assert row["error_message"] == error_msg
        assert row["output_result"] is None

        ledger.close()

    def test_record_start_creates_row(self):
        """Test that record_start creates a STARTED row."""
        ledger = VibeLedger(":memory:")
        task = Task(agent_id="test-agent", payload={"action": "start"})

        ledger.record_start(task)

        # Verify row exists
        cursor = ledger.conn.cursor()
        cursor.execute("SELECT * FROM task_history WHERE task_id = ?", (task.id,))
        row = cursor.fetchone()

        assert row is not None
        assert row["status"] == "STARTED"
        assert row["output_result"] is None

        ledger.close()

    def test_record_completion_handles_non_json_serializable(self):
        """Test that record_completion handles non-JSON-serializable results."""
        ledger = VibeLedger(":memory:")
        task = Task(agent_id="test-agent", payload={"action": "test"})

        # Result with non-serializable type
        class CustomObject:
            def __str__(self):
                return "CustomObject(value=42)"

        result = CustomObject()

        ledger.record_completion(task, result)

        # Verify row exists and result was converted to string
        cursor = ledger.conn.cursor()
        cursor.execute("SELECT * FROM task_history WHERE task_id = ?", (task.id,))
        row = cursor.fetchone()

        assert row is not None
        assert row["status"] == "COMPLETED"
        # Result should be string representation
        assert "CustomObject" in row["output_result"]

        ledger.close()


class TestLedgerHistory:
    """Tests for get_history functionality."""

    def test_get_history_returns_recent_tasks(self):
        """Test that get_history returns recent tasks in reverse chronological order."""
        ledger = VibeLedger(":memory:")

        # Record multiple tasks
        tasks = []
        for i in range(5):
            task = Task(id=f"task-{i}", agent_id="test-agent", payload={"order": i})
            ledger.record_completion(task, {"result": i})
            tasks.append(task)

        # Get history
        history = ledger.get_history(limit=10)

        assert len(history) == 5
        # Should be in reverse order (most recent first)
        assert history[0]["task_id"] == "task-4"
        assert history[4]["task_id"] == "task-0"

        ledger.close()

    def test_get_history_respects_limit(self):
        """Test that get_history respects the limit parameter."""
        ledger = VibeLedger(":memory:")

        # Record 10 tasks
        for i in range(10):
            task = Task(agent_id="test-agent", payload={"order": i})
            ledger.record_completion(task, {"result": i})

        # Get limited history
        history = ledger.get_history(limit=3)

        assert len(history) == 3

        ledger.close()

    def test_get_history_filters_by_status(self):
        """Test that get_history can filter by status."""
        ledger = VibeLedger(":memory:")

        # Record mixed tasks
        for i in range(3):
            task = Task(agent_id="test-agent", payload={"order": i})
            ledger.record_completion(task, {"result": i})

        for i in range(2):
            task = Task(agent_id="test-agent", payload={"order": i})
            ledger.record_failure(task, "Error")

        # Get only completed
        completed = ledger.get_history(status="COMPLETED")
        assert len(completed) == 3
        assert all(r["status"] == "COMPLETED" for r in completed)

        # Get only failed
        failed = ledger.get_history(status="FAILED")
        assert len(failed) == 2
        assert all(r["status"] == "FAILED" for r in failed)

        ledger.close()

    def test_get_history_filters_by_agent_id(self):
        """Test that get_history can filter by agent_id."""
        ledger = VibeLedger(":memory:")

        # Record tasks from different agents
        for i in range(3):
            task = Task(agent_id="agent-A", payload={"order": i})
            ledger.record_completion(task, {"result": i})

        for i in range(2):
            task = Task(agent_id="agent-B", payload={"order": i})
            ledger.record_completion(task, {"result": i})

        # Get history for agent-A
        history_a = ledger.get_history(agent_id="agent-A")
        assert len(history_a) == 3
        assert all(r["agent_id"] == "agent-A" for r in history_a)

        # Get history for agent-B
        history_b = ledger.get_history(agent_id="agent-B")
        assert len(history_b) == 2
        assert all(r["agent_id"] == "agent-B" for r in history_b)

        ledger.close()

    def test_get_history_deserializes_json(self):
        """Test that get_history deserializes JSON fields."""
        ledger = VibeLedger(":memory:")

        task = Task(agent_id="test-agent", payload={"nested": {"key": "value"}})
        result = {"complex": [1, 2, 3]}
        ledger.record_completion(task, result)

        history = ledger.get_history()
        assert len(history) == 1

        record = history[0]
        assert isinstance(record["input_payload"], dict)
        assert record["input_payload"] == {"nested": {"key": "value"}}
        assert isinstance(record["output_result"], dict)
        assert record["output_result"] == {"complex": [1, 2, 3]}

        ledger.close()


class TestLedgerQuery:
    """Tests for get_task and get_statistics."""

    def test_get_task_retrieves_specific_task(self):
        """Test that get_task retrieves a specific task by ID."""
        ledger = VibeLedger(":memory:")

        task = Task(id="specific-task", agent_id="test-agent", payload={"key": "value"})
        ledger.record_completion(task, {"result": "success"})

        record = ledger.get_task("specific-task")

        assert record is not None
        assert record["task_id"] == "specific-task"
        assert record["agent_id"] == "test-agent"
        assert record["status"] == "COMPLETED"
        assert record["input_payload"] == {"key": "value"}
        assert record["output_result"] == {"result": "success"}

        ledger.close()

    def test_get_task_returns_none_for_missing_task(self):
        """Test that get_task returns None for non-existent task ID."""
        ledger = VibeLedger(":memory:")

        record = ledger.get_task("nonexistent-task")

        assert record is None

        ledger.close()

    def test_get_statistics_returns_counts(self):
        """Test that get_statistics returns accurate counts."""
        ledger = VibeLedger(":memory:")

        # Record 5 completed tasks
        for i in range(5):
            task = Task(agent_id="agent-A", payload={"i": i})
            ledger.record_completion(task, {"result": i})

        # Record 3 failed tasks
        for i in range(3):
            task = Task(agent_id="agent-B", payload={"i": i})
            ledger.record_failure(task, "Error")

        # Record 2 started tasks
        for i in range(2):
            task = Task(agent_id="agent-C", payload={"i": i})
            ledger.record_start(task)

        stats = ledger.get_statistics()

        assert stats["total_tasks"] == 10
        assert stats["completed"] == 5
        assert stats["failed"] == 3
        assert stats["started"] == 2
        assert len(stats["agents"]) == 3
        assert "agent-A" in stats["agents"]
        assert "agent-B" in stats["agents"]
        assert "agent-C" in stats["agents"]

        ledger.close()

    def test_get_statistics_empty_ledger(self):
        """Test that get_statistics handles empty ledger."""
        ledger = VibeLedger(":memory:")

        stats = ledger.get_statistics()

        assert stats["total_tasks"] == 0
        assert stats["completed"] == 0
        assert stats["failed"] == 0
        assert stats["started"] == 0
        assert stats["agents"] == []

        ledger.close()


class TestLedgerKernelIntegration:
    """Test 3: Integration test with VibeKernel."""

    def test_kernel_records_successful_execution(self):
        """Test that kernel automatically records successful task execution."""
        # Use in-memory database for testing
        kernel = VibeKernel(ledger_path=":memory:")
        agent = TestAgent(agent_id="test-agent")

        kernel.register_agent(agent)
        kernel.boot()

        # Submit and process task
        task = Task(agent_id="test-agent", payload={"action": "test"})
        kernel.submit(task)
        kernel.tick()

        # Check ledger
        record = kernel.ledger.get_task(task.id)

        assert record is not None
        assert record["status"] == "COMPLETED"
        assert record["agent_id"] == "test-agent"
        assert record["input_payload"] == {"action": "test"}
        assert record["output_result"]["status"] == "success"
        assert record["output_result"]["data"] == {"action": "test"}

        kernel.ledger.close()

    def test_kernel_records_failed_execution(self):
        """Test that kernel records task failures with error messages."""
        kernel = VibeKernel(ledger_path=":memory:")
        agent = FailingTestAgent(agent_id="failing-agent")

        kernel.register_agent(agent)
        kernel.boot()

        # Submit task that will fail
        task = Task(agent_id="failing-agent", payload={"action": "fail"})
        kernel.submit(task)

        # Task should raise exception
        with pytest.raises(RuntimeError, match="Test failure"):
            kernel.tick()

        # Check ledger recorded the failure
        record = kernel.ledger.get_task(task.id)

        assert record is not None
        assert record["status"] == "FAILED"
        assert "RuntimeError" in record["error_message"]
        assert "Test failure" in record["error_message"]

        kernel.ledger.close()

    def test_kernel_records_agent_not_found(self):
        """Test that kernel records AgentNotFoundError to ledger."""
        kernel = VibeKernel(ledger_path=":memory:")
        kernel.boot()

        # Submit task for nonexistent agent
        task = Task(agent_id="nonexistent-agent", payload={"action": "test"})
        # Bypass validation to test ledger recording
        kernel.scheduler.submit_task(task)

        # Should raise AgentNotFoundError
        with pytest.raises(Exception):  # AgentNotFoundError
            kernel.tick()

        # Check ledger recorded the failure
        record = kernel.ledger.get_task(task.id)

        assert record is not None
        assert record["status"] == "FAILED"
        assert "not found" in record["error_message"].lower()

        kernel.ledger.close()

    def test_kernel_records_multiple_tasks(self):
        """Test that kernel records history of multiple task executions."""
        kernel = VibeKernel(ledger_path=":memory:")
        agent = TestAgent(agent_id="test-agent")

        kernel.register_agent(agent)
        kernel.boot()

        # Submit and process multiple tasks
        task_ids = []
        for i in range(5):
            task = Task(agent_id="test-agent", payload={"order": i})
            task_ids.append(task.id)
            kernel.submit(task)

        # Process all tasks
        while kernel.tick():
            pass

        # Check ledger has all tasks
        history = kernel.ledger.get_history(limit=10)
        assert len(history) == 5

        # All should be completed
        assert all(r["status"] == "COMPLETED" for r in history)

        # Verify task IDs
        recorded_ids = {r["task_id"] for r in history}
        assert recorded_ids == set(task_ids)

        kernel.ledger.close()

    def test_kernel_ledger_statistics(self):
        """Test that ledger statistics reflect kernel execution."""
        kernel = VibeKernel(ledger_path=":memory:")
        success_agent = TestAgent(agent_id="success-agent")
        failing_agent = FailingTestAgent(agent_id="failing-agent")

        kernel.register_agent(success_agent)
        kernel.register_agent(failing_agent)
        kernel.boot()

        # Submit 3 successful tasks
        for i in range(3):
            task = Task(agent_id="success-agent", payload={"i": i})
            kernel.submit(task)

        # Submit 2 failing tasks
        for i in range(2):
            task = Task(agent_id="failing-agent", payload={"i": i})
            kernel.submit(task)

        # Process tasks (some will fail)
        for _ in range(3):
            kernel.tick()

        for _ in range(2):
            try:
                kernel.tick()
            except RuntimeError:
                pass  # Expected failures

        # Check statistics
        stats = kernel.ledger.get_statistics()

        assert stats["total_tasks"] == 5
        assert stats["completed"] == 3
        assert stats["failed"] == 2
        assert len(stats["agents"]) == 2
        assert "success-agent" in stats["agents"]
        assert "failing-agent" in stats["agents"]

        kernel.ledger.close()


class TestLedgerContextManager:
    """Tests for context manager support."""

    def test_ledger_context_manager(self):
        """Test that ledger works as a context manager."""
        with VibeLedger(":memory:") as ledger:
            task = Task(agent_id="test-agent", payload={"action": "test"})
            ledger.record_completion(task, {"result": "success"})

            # Should be able to query while in context
            record = ledger.get_task(task.id)
            assert record is not None

        # Connection should be closed after context exit
        # (can't easily test this without accessing private state)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
