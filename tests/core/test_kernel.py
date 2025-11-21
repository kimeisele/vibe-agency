"""
Unit tests for the vibe-agency kernel (ARCH-022).

Tests the Kernel Loop implementation and task execution.
Updated for ARCH-023 to include agent registration.
"""

import logging
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.agent_protocol import VibeAgent
from vibe_core.kernel import KernelStatus, VibeKernel
from vibe_core.scheduling import Task


class DummyAgent(VibeAgent):
    """Simple test agent that tracks processed tasks."""

    def __init__(self, agent_id: str):
        self._agent_id = agent_id
        self.processed_tasks = []

    @property
    def agent_id(self) -> str:
        return self._agent_id

    def process(self, task: Task) -> Any:
        self.processed_tasks.append(task)
        return {"status": "processed", "task_id": task.id}


class TestKernelBootCycle:
    """Test 1: Boot Cycle - Kernel lifecycle management."""

    def test_kernel_initialization(self):
        """Test that kernel initializes with STOPPED status."""
        kernel = VibeKernel(ledger_path=":memory:")
        assert kernel.status == KernelStatus.STOPPED
        assert kernel.scheduler is not None

    def test_kernel_boot(self):
        """Test that boot() transitions kernel to RUNNING status."""
        kernel = VibeKernel(ledger_path=":memory:")
        assert kernel.status == KernelStatus.STOPPED

        kernel.boot()
        assert kernel.status == KernelStatus.RUNNING

    def test_kernel_shutdown(self):
        """Test that shutdown() transitions kernel to STOPPED status."""
        kernel = VibeKernel(ledger_path=":memory:")
        kernel.boot()
        assert kernel.status == KernelStatus.RUNNING

        kernel.shutdown()
        assert kernel.status == KernelStatus.STOPPED

    def test_kernel_boot_shutdown_cycle(self):
        """Test multiple boot/shutdown cycles."""
        kernel = VibeKernel(ledger_path=":memory:")

        # First cycle
        kernel.boot()
        assert kernel.status == KernelStatus.RUNNING
        kernel.shutdown()
        assert kernel.status == KernelStatus.STOPPED

        # Second cycle
        kernel.boot()
        assert kernel.status == KernelStatus.RUNNING
        kernel.shutdown()
        assert kernel.status == KernelStatus.STOPPED

    def test_kernel_boot_logs_online(self, caplog):
        """Test that boot() logs 'KERNEL: ONLINE' message."""
        kernel = VibeKernel(ledger_path=":memory:")
        with caplog.at_level(logging.INFO):
            kernel.boot()
        assert "KERNEL: ONLINE" in caplog.text

    def test_kernel_shutdown_logs_shutdown(self, caplog):
        """Test that shutdown() logs 'KERNEL: SHUTDOWN' message."""
        kernel = VibeKernel(ledger_path=":memory:")
        kernel.boot()
        with caplog.at_level(logging.INFO):
            kernel.shutdown()
        assert "KERNEL: SHUTDOWN" in caplog.text


class TestKernelExecutionCycle:
    """Test 2: Execution Cycle - Task processing through tick()."""

    def test_submit_task_returns_task_id(self):
        """Test that submit() returns a task ID."""
        kernel = VibeKernel(ledger_path=":memory:")
        task = Task(agent_id="agent-1", payload={"action": "compile"})
        task_id = kernel.submit(task)

        assert task_id is not None
        assert isinstance(task_id, str)
        assert task_id == task.id

    def test_tick_processes_task_when_running(self, caplog):
        """Test that tick() processes a task and returns True (busy)."""
        kernel = VibeKernel(ledger_path=":memory:")
        agent = DummyAgent(agent_id="agent-1")
        kernel.register_agent(agent)
        kernel.boot()

        # Submit a task
        task = Task(agent_id="agent-1", payload={"action": "compile", "target": "main.py"})
        kernel.submit(task)

        # Execute tick and verify it returns True (busy)
        with caplog.at_level(logging.INFO):
            result = kernel.tick()

        assert result is True
        assert "KERNEL EXEC: Dispatching Task" in caplog.text
        assert task.id in caplog.text
        assert "agent-1" in caplog.text

    def test_tick_processes_multiple_tasks_in_order(self, caplog):
        """Test that tick() processes tasks in FIFO order."""
        kernel = VibeKernel(ledger_path=":memory:")
        agent1 = DummyAgent(agent_id="agent-1")
        agent2 = DummyAgent(agent_id="agent-2")
        agent3 = DummyAgent(agent_id="agent-3")
        kernel.register_agent(agent1)
        kernel.register_agent(agent2)
        kernel.register_agent(agent3)
        kernel.boot()

        # Submit three tasks
        task1 = Task(id="task-1", agent_id="agent-1", payload={"order": 1})
        task2 = Task(id="task-2", agent_id="agent-2", payload={"order": 2})
        task3 = Task(id="task-3", agent_id="agent-3", payload={"order": 3})

        kernel.submit(task1)
        kernel.submit(task2)
        kernel.submit(task3)

        # Process all tasks
        with caplog.at_level(logging.INFO):
            result1 = kernel.tick()
            result2 = kernel.tick()
            result3 = kernel.tick()

        # All ticks should return True (busy)
        assert result1 is True
        assert result2 is True
        assert result3 is True

        # Verify execution order in logs
        logs = caplog.text
        task1_pos = logs.find("task-1")
        task2_pos = logs.find("task-2")
        task3_pos = logs.find("task-3")

        assert task1_pos < task2_pos < task3_pos

    def test_execute_task_is_called_internally(self):
        """Test that tick() calls _execute_task() internally."""
        kernel = VibeKernel(ledger_path=":memory:")
        kernel.boot()

        task = Task(agent_id="agent-1", payload={})
        kernel.submit(task)

        # Mock _execute_task to verify it's called
        with patch.object(kernel, "_execute_task") as mock_execute:
            kernel.tick()
            mock_execute.assert_called_once()
            # Verify the task passed to _execute_task
            called_task = mock_execute.call_args[0][0]
            assert called_task.id == task.id
            assert called_task.agent_id == "agent-1"

    def test_kernel_can_submit_while_stopped(self):
        """Test that tasks can be submitted even when kernel is stopped."""
        kernel = VibeKernel(ledger_path=":memory:")
        # Don't boot - kernel is STOPPED

        task = Task(agent_id="agent-1", payload={})
        task_id = kernel.submit(task)

        assert task_id is not None
        # Task is queued but won't be processed until boot


class TestKernelIdleCycle:
    """Test 3: Idle Cycle - Behavior when no tasks are available."""

    def test_tick_returns_false_when_empty(self):
        """Test that tick() returns False when queue is empty."""
        kernel = VibeKernel(ledger_path=":memory:")
        kernel.boot()

        # Call tick on empty kernel
        result = kernel.tick()
        assert result is False

    def test_tick_returns_false_after_draining_queue(self):
        """Test that tick() returns False after all tasks are processed."""
        kernel = VibeKernel(ledger_path=":memory:")
        agent = DummyAgent(agent_id="agent-1")
        kernel.register_agent(agent)
        kernel.boot()

        # Submit one task
        task = Task(agent_id="agent-1", payload={})
        kernel.submit(task)

        # Process the task
        result1 = kernel.tick()
        assert result1 is True

        # Queue is now empty
        result2 = kernel.tick()
        assert result2 is False

    def test_multiple_idle_ticks(self):
        """Test that multiple tick() calls on empty queue all return False."""
        kernel = VibeKernel(ledger_path=":memory:")
        kernel.boot()

        # Multiple idle ticks
        assert kernel.tick() is False
        assert kernel.tick() is False
        assert kernel.tick() is False

    def test_tick_does_not_process_when_stopped(self):
        """Test that tick() returns False when kernel is not RUNNING."""
        kernel = VibeKernel(ledger_path=":memory:")
        # Don't boot - kernel is STOPPED

        task = Task(agent_id="agent-1", payload={})
        kernel.submit(task)

        # tick() should return False because kernel is not RUNNING
        result = kernel.tick()
        assert result is False

    def test_tick_logs_warning_when_not_running(self, caplog):
        """Test that tick() logs a warning when called while not RUNNING."""
        kernel = VibeKernel(ledger_path=":memory:")
        # Don't boot - kernel is STOPPED

        with caplog.at_level(logging.WARNING):
            kernel.tick()

        assert "tick() called but status is" in caplog.text
        assert "STOPPED" in caplog.text


class TestKernelStatus:
    """Tests for kernel status reporting."""

    def test_get_status_returns_kernel_and_queue_info(self):
        """Test that get_status() returns comprehensive status info."""
        kernel = VibeKernel(ledger_path=":memory:")
        status = kernel.get_status()

        assert "kernel_status" in status
        assert "pending_tasks" in status
        assert "queue_type" in status

        assert status["kernel_status"] == "STOPPED"
        assert status["pending_tasks"] == 0
        assert status["queue_type"] == "FIFO"

    def test_get_status_reflects_current_state(self):
        """Test that get_status() reflects current kernel state."""
        kernel = VibeKernel(ledger_path=":memory:")

        # Initial state
        status = kernel.get_status()
        assert status["kernel_status"] == "STOPPED"
        assert status["pending_tasks"] == 0

        # Register agents
        agent1 = DummyAgent(agent_id="agent-1")
        agent2 = DummyAgent(agent_id="agent-2")
        kernel.register_agent(agent1)
        kernel.register_agent(agent2)

        # After boot
        kernel.boot()
        status = kernel.get_status()
        assert status["kernel_status"] == "RUNNING"

        # After submitting tasks
        task1 = Task(agent_id="agent-1", payload={})
        task2 = Task(agent_id="agent-2", payload={})
        kernel.submit(task1)
        kernel.submit(task2)

        status = kernel.get_status()
        assert status["kernel_status"] == "RUNNING"
        assert status["pending_tasks"] == 2

        # After processing one task
        kernel.tick()
        status = kernel.get_status()
        assert status["pending_tasks"] == 1

        # After shutdown
        kernel.shutdown()
        status = kernel.get_status()
        assert status["kernel_status"] == "STOPPED"


class TestKernelIntegration:
    """Integration tests for complete kernel workflows."""

    def test_full_kernel_lifecycle(self, caplog):
        """Test a complete kernel lifecycle from boot to shutdown."""
        kernel = VibeKernel(ledger_path=":memory:")

        # 0. Register agents
        planning_agent = DummyAgent(agent_id="agent-planning")
        coding_agent = DummyAgent(agent_id="agent-coding")
        testing_agent = DummyAgent(agent_id="agent-testing")
        kernel.register_agent(planning_agent)
        kernel.register_agent(coding_agent)
        kernel.register_agent(testing_agent)

        # 1. Boot
        kernel.boot()
        assert kernel.status == KernelStatus.RUNNING

        # 2. Submit multiple tasks
        tasks = [
            Task(agent_id="agent-planning", payload={"phase": "planning"}),
            Task(agent_id="agent-coding", payload={"phase": "coding"}),
            Task(agent_id="agent-testing", payload={"phase": "testing"}),
        ]

        for task in tasks:
            kernel.submit(task)

        # 3. Process all tasks via tick loop
        processed_count = 0
        with caplog.at_level(logging.INFO):
            while kernel.tick():
                processed_count += 1

        assert processed_count == 3
        assert "agent-planning" in caplog.text
        assert "agent-coding" in caplog.text
        assert "agent-testing" in caplog.text

        # 4. Verify queue is empty
        status = kernel.get_status()
        assert status["pending_tasks"] == 0

        # 5. Shutdown
        kernel.shutdown()
        assert kernel.status == KernelStatus.STOPPED

    def test_kernel_can_resume_after_shutdown(self):
        """Test that kernel can process tasks after shutdown and reboot."""
        kernel = VibeKernel(ledger_path=":memory:")

        # Register agents
        agent1 = DummyAgent(agent_id="agent-1")
        agent2 = DummyAgent(agent_id="agent-2")
        kernel.register_agent(agent1)
        kernel.register_agent(agent2)

        # First cycle
        kernel.boot()
        task1 = Task(agent_id="agent-1", payload={})
        kernel.submit(task1)
        kernel.tick()
        kernel.shutdown()

        # Second cycle - submit while stopped
        task2 = Task(agent_id="agent-2", payload={})
        kernel.submit(task2)

        # Boot again and process
        kernel.boot()
        result = kernel.tick()
        assert result is True

        # Task should be processed
        status = kernel.get_status()
        assert status["pending_tasks"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
