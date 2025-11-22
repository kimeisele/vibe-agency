"""
Unit tests for agent dispatch mechanism (ARCH-023).

Tests the integration between VibeKernel and VibeAgent protocol,
including agent registration, task dispatch, and error handling.
"""

import logging
from typing import Any

import pytest

from vibe_core.agent_protocol import AgentNotFoundError, VibeAgent
from vibe_core.kernel import VibeKernel
from vibe_core.scheduling import Task


class EchoAgent(VibeAgent):
    """
    Simple test agent that echoes task payloads.

    This is a dummy agent used to verify the dispatch mechanism
    without complex LLM or processing logic.
    """

    def __init__(self, agent_id: str = "echo-agent"):
        """Initialize the echo agent with an ID."""
        self._agent_id = agent_id
        self.processed_tasks = []  # Track tasks for testing

    @property
    def agent_id(self) -> str:
        """Return the agent's ID."""
        return self._agent_id

    @property
    def capabilities(self) -> list[str]:
        """Return agent capabilities."""
        return ["echo"]

    def process(self, task: Task) -> Any:
        """Echo the task payload back as a result."""
        self.processed_tasks.append(task)
        return {"echo": task.payload, "task_id": task.id, "agent_id": self.agent_id}


class CounterAgent(VibeAgent):
    """
    Test agent that counts how many tasks it has processed.
    """

    def __init__(self, agent_id: str = "counter-agent"):
        """Initialize the counter agent."""
        self._agent_id = agent_id
        self.task_count = 0

    @property
    def agent_id(self) -> str:
        """Return the agent's ID."""
        return self._agent_id

    @property
    def capabilities(self) -> list[str]:
        """Return agent capabilities."""
        return ["count"]

    def process(self, task: Task) -> Any:
        """Increment counter and return count."""
        self.task_count += 1
        return {"count": self.task_count, "task_id": task.id}


class FailingAgent(VibeAgent):
    """
    Test agent that always raises an exception.
    """

    def __init__(self, agent_id: str = "failing-agent"):
        """Initialize the failing agent."""
        self._agent_id = agent_id

    @property
    def agent_id(self) -> str:
        """Return the agent's ID."""
        return self._agent_id

    @property
    def capabilities(self) -> list[str]:
        """Return agent capabilities."""
        return ["fail"]

    def process(self, task: Task) -> Any:
        """Always raise an exception."""
        raise RuntimeError(f"Agent {self.agent_id} failed to process task {task.id}")


class TestAgentRegistration:
    """Tests for agent registration in the kernel."""

    def test_register_single_agent(self):
        """Test registering a single agent with the kernel."""
        kernel = VibeKernel(ledger_path=":memory:")
        agent = EchoAgent(agent_id="echo-1")

        kernel.register_agent(agent)

        status = kernel.get_status()
        assert status["registered_agents"] == 1
        assert "echo-1" in status["agent_ids"]

    def test_register_multiple_agents(self):
        """Test registering multiple agents with different IDs."""
        kernel = VibeKernel(ledger_path=":memory:")
        agent1 = EchoAgent(agent_id="echo-1")
        agent2 = EchoAgent(agent_id="echo-2")
        agent3 = CounterAgent(agent_id="counter-1")

        kernel.register_agent(agent1)
        kernel.register_agent(agent2)
        kernel.register_agent(agent3)

        status = kernel.get_status()
        assert status["registered_agents"] == 3
        assert "echo-1" in status["agent_ids"]
        assert "echo-2" in status["agent_ids"]
        assert "counter-1" in status["agent_ids"]

    def test_register_duplicate_agent_raises_error(self):
        """Test that registering duplicate agent ID raises ValueError."""
        kernel = VibeKernel(ledger_path=":memory:")
        agent1 = EchoAgent(agent_id="echo-1")
        agent2 = EchoAgent(agent_id="echo-1")  # Same ID

        kernel.register_agent(agent1)

        with pytest.raises(ValueError, match="already registered"):
            kernel.register_agent(agent2)

    def test_register_agent_logs_message(self, caplog):
        """Test that agent registration logs a message."""
        kernel = VibeKernel(ledger_path=":memory:")
        agent = EchoAgent(agent_id="echo-1")

        with caplog.at_level(logging.INFO):
            kernel.register_agent(agent)

        assert "Registered agent 'echo-1'" in caplog.text

    def test_register_agent_before_boot(self):
        """Test that agents can be registered before kernel boot."""
        kernel = VibeKernel(ledger_path=":memory:")
        agent = EchoAgent(agent_id="echo-1")

        # Register before boot
        kernel.register_agent(agent)

        # Should still be registered after boot
        kernel.boot()

        status = kernel.get_status()
        assert status["registered_agents"] == 1


class TestAgentDispatch:
    """Tests for task dispatch to registered agents."""

    def test_dispatch_to_echo_agent(self):
        """Test that kernel dispatches task to EchoAgent and returns result."""
        kernel = VibeKernel(ledger_path=":memory:")
        agent = EchoAgent(agent_id="echo-1")

        kernel.register_agent(agent)
        kernel.boot()

        task = Task(agent_id="echo-1", payload={"message": "hello"})
        kernel.submit(task)

        # Process the task
        kernel.tick()

        # Verify agent received and processed the task
        assert len(agent.processed_tasks) == 1
        processed_task = agent.processed_tasks[0]
        assert processed_task.id == task.id
        assert processed_task.payload == {"message": "hello"}

    def test_dispatch_returns_agent_result(self):
        """Test that _execute_task returns the agent's result."""
        kernel = VibeKernel(ledger_path=":memory:")
        agent = EchoAgent(agent_id="echo-1")

        kernel.register_agent(agent)
        kernel.boot()

        task = Task(agent_id="echo-1", payload={"data": "test"})
        result = kernel._execute_task(task)

        # Verify the result from EchoAgent
        assert result["echo"] == {"data": "test"}
        assert result["task_id"] == task.id
        assert result["agent_id"] == "echo-1"

    def test_dispatch_multiple_tasks_to_same_agent(self):
        """Test dispatching multiple tasks to the same agent."""
        kernel = VibeKernel(ledger_path=":memory:")
        agent = CounterAgent(agent_id="counter-1")

        kernel.register_agent(agent)
        kernel.boot()

        # Submit three tasks
        task1 = Task(agent_id="counter-1", payload={})
        task2 = Task(agent_id="counter-1", payload={})
        task3 = Task(agent_id="counter-1", payload={})

        kernel.submit(task1)
        kernel.submit(task2)
        kernel.submit(task3)

        # Process all tasks
        kernel.tick()
        kernel.tick()
        kernel.tick()

        # Verify counter increased
        assert agent.task_count == 3

    def test_dispatch_to_multiple_agents(self):
        """Test dispatching tasks to different agents."""
        kernel = VibeKernel(ledger_path=":memory:")
        echo_agent = EchoAgent(agent_id="echo-1")
        counter_agent = CounterAgent(agent_id="counter-1")

        kernel.register_agent(echo_agent)
        kernel.register_agent(counter_agent)
        kernel.boot()

        # Submit tasks to different agents
        task_echo = Task(agent_id="echo-1", payload={"msg": "test"})
        task_counter1 = Task(agent_id="counter-1", payload={})
        task_counter2 = Task(agent_id="counter-1", payload={})

        kernel.submit(task_echo)
        kernel.submit(task_counter1)
        kernel.submit(task_counter2)

        # Process all tasks
        kernel.tick()
        kernel.tick()
        kernel.tick()

        # Verify each agent processed its tasks
        assert len(echo_agent.processed_tasks) == 1
        assert counter_agent.task_count == 2

    def test_dispatch_logs_execution(self, caplog):
        """Test that task dispatch logs execution details."""
        kernel = VibeKernel(ledger_path=":memory:")
        agent = EchoAgent(agent_id="echo-1")

        kernel.register_agent(agent)
        kernel.boot()

        task = Task(agent_id="echo-1", payload={"test": "data"})
        kernel.submit(task)

        with caplog.at_level(logging.INFO):
            kernel.tick()

        assert "Dispatching Task" in caplog.text
        assert "echo-1" in caplog.text
        assert task.id in caplog.text


class TestAgentNotFound:
    """Tests for handling missing/unregistered agents."""

    def test_dispatch_to_unregistered_agent_raises_error(self):
        """Test that dispatching to unregistered agent raises AgentNotFoundError."""
        kernel = VibeKernel(ledger_path=":memory:")
        kernel.boot()

        task = Task(agent_id="nonexistent-agent", payload={})

        with pytest.raises(ValueError, match="not registered"):
            kernel.submit(task)

    def test_agent_not_found_logs_error(self, caplog):
        """Test that missing agent logs an error message."""
        kernel = VibeKernel(ledger_path=":memory:")
        kernel.boot()

        task = Task(agent_id="missing-agent", payload={})
        # Bypass submit() validation to test tick() error handling
        kernel.scheduler.submit_task(task)

        with caplog.at_level(logging.ERROR), pytest.raises(AgentNotFoundError):
            kernel.tick()

        assert "not found" in caplog.text
        assert "missing-agent" in caplog.text

    def test_agent_not_found_shows_available_agents(self, caplog):
        """Test that error message includes available agents."""
        kernel = VibeKernel(ledger_path=":memory:")
        agent1 = EchoAgent(agent_id="echo-1")
        agent2 = CounterAgent(agent_id="counter-1")

        kernel.register_agent(agent1)
        kernel.register_agent(agent2)
        kernel.boot()

        task = Task(agent_id="nonexistent", payload={})

        with pytest.raises(ValueError, match="Available"):
            kernel.submit(task)

        # Error should mention available agents
        assert "echo-1" in caplog.text or "counter-1" in caplog.text


class TestAgentExceptions:
    """Tests for handling exceptions raised by agents."""

    def test_agent_exception_propagates(self):
        """Test that exceptions from agent.process() propagate to caller."""
        kernel = VibeKernel(ledger_path=":memory:")
        agent = FailingAgent(agent_id="fail-1")

        kernel.register_agent(agent)
        kernel.boot()

        task = Task(agent_id="fail-1", payload={})
        kernel.submit(task)

        # The exception should propagate
        with pytest.raises(RuntimeError, match="failed to process task"):
            kernel.tick()


class TestDispatchIntegration:
    """Integration tests for complete dispatch workflows."""

    def test_full_dispatch_lifecycle(self, caplog):
        """Test a complete dispatch lifecycle from registration to execution."""
        kernel = VibeKernel(ledger_path=":memory:")

        # 1. Register agents
        echo_agent = EchoAgent(agent_id="echo-1")
        counter_agent = CounterAgent(agent_id="counter-1")

        kernel.register_agent(echo_agent)
        kernel.register_agent(counter_agent)

        # 2. Boot kernel
        kernel.boot()

        # 3. Submit tasks
        tasks = [
            Task(agent_id="echo-1", payload={"msg": "first"}),
            Task(agent_id="counter-1", payload={}),
            Task(agent_id="echo-1", payload={"msg": "second"}),
            Task(agent_id="counter-1", payload={}),
        ]

        for task in tasks:
            kernel.submit(task)

        # 4. Process all tasks
        with caplog.at_level(logging.INFO):
            processed = 0
            while kernel.tick():
                processed += 1

        # 5. Verify results
        assert processed == 4
        assert len(echo_agent.processed_tasks) == 2
        assert counter_agent.task_count == 2
        assert "Dispatching Task" in caplog.text

        # 6. Verify queue is empty
        status = kernel.get_status()
        assert status["pending_tasks"] == 0

    def test_dispatch_preserves_fifo_order(self):
        """Test that dispatch preserves FIFO order across multiple agents."""
        kernel = VibeKernel(ledger_path=":memory:")
        agent = EchoAgent(agent_id="echo-1")

        kernel.register_agent(agent)
        kernel.boot()

        # Submit tasks with ordered payloads
        for i in range(5):
            task = Task(agent_id="echo-1", payload={"order": i})
            kernel.submit(task)

        # Process all tasks
        while kernel.tick():
            pass

        # Verify FIFO order
        for i, task in enumerate(agent.processed_tasks):
            assert task.payload["order"] == i


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
