"""
Unit tests for the vibe-agency cortex (ARCH-025).

Tests the LLM integration layer: LLMProvider, SimpleLLMAgent,
and full stack integration (Kernel → Agent → LLM → Ledger).
"""

import pytest

from tests.mocks.llm import MockLLMProvider
from vibe_core.agents import SimpleLLMAgent
from vibe_core.kernel import VibeKernel
from vibe_core.llm import LLMError, LLMProvider
from vibe_core.scheduling import Task


class TestMockLLMProvider:
    """Test 1: MockLLMProvider functionality."""

    def test_mock_provider_initialization(self):
        """Test that MockLLMProvider initializes with default response."""
        provider = MockLLMProvider()
        assert provider.system_prompt == "You are a helpful mock assistant."

    def test_mock_provider_custom_response(self):
        """Test that MockLLMProvider returns custom response."""
        provider = MockLLMProvider(mock_response="Custom response")

        messages = [{"role": "user", "content": "Hello"}]
        response = provider.chat(messages)

        assert response == "Custom response"

    def test_mock_provider_custom_system_prompt(self):
        """Test that MockLLMProvider uses custom system prompt."""
        provider = MockLLMProvider(system_prompt_text="Be very formal.")
        assert provider.system_prompt == "Be very formal."

    def test_mock_provider_tracks_calls(self):
        """Test that MockLLMProvider tracks call history when enabled."""
        provider = MockLLMProvider(track_calls=True)

        messages1 = [{"role": "user", "content": "First"}]
        messages2 = [{"role": "user", "content": "Second"}]

        provider.chat(messages1)
        provider.chat(messages2, model="gpt-4")

        assert provider.get_call_count() == 2
        assert provider.call_history[0]["messages"] == messages1
        assert provider.call_history[1]["model"] == "gpt-4"

    def test_mock_provider_set_response(self):
        """Test that MockLLMProvider allows updating response."""
        provider = MockLLMProvider(mock_response="First")

        assert provider.chat([{"role": "user", "content": "Hi"}]) == "First"

        provider.set_mock_response("Second")
        assert provider.chat([{"role": "user", "content": "Hi"}]) == "Second"

    def test_mock_provider_clear_history(self):
        """Test that MockLLMProvider can clear call history."""
        provider = MockLLMProvider(track_calls=True)

        provider.chat([{"role": "user", "content": "Test"}])
        assert provider.get_call_count() == 1

        provider.clear_history()
        assert provider.get_call_count() == 0

    def test_mock_provider_is_llm_provider(self):
        """Test that MockLLMProvider is instance of LLMProvider."""
        provider = MockLLMProvider()
        assert isinstance(provider, LLMProvider)


class TestSimpleLLMAgent:
    """Test 2: SimpleLLMAgent functionality."""

    def test_agent_initialization(self):
        """Test that SimpleLLMAgent initializes correctly."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(
            agent_id="test-agent", provider=provider, system_prompt="Be helpful."
        )

        assert agent.agent_id == "test-agent"
        assert agent.provider is provider
        assert agent._system_prompt == "Be helpful."

    def test_agent_uses_provider_default_system_prompt(self):
        """Test that agent uses provider's system prompt if none provided."""
        provider = MockLLMProvider(system_prompt_text="Provider prompt")
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)

        assert agent._system_prompt == "Provider prompt"

    def test_agent_process_basic_task(self):
        """Test that agent processes a basic task successfully."""
        provider = MockLLMProvider(mock_response="Hello, user!")
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)

        task = Task(agent_id="test-agent", payload={"user_message": "Hi there!"})

        result = agent.process(task)

        assert result["success"] is True
        assert result["response"] == "Hello, user!"
        assert result["provider"] == "MockLLMProvider"
        assert result["error"] is None

    def test_agent_process_with_model(self):
        """Test that agent passes model to provider."""
        provider = MockLLMProvider(track_calls=True, mock_response="OK")
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider, model="gpt-4")

        task = Task(agent_id="test-agent", payload={"user_message": "Test"})

        result = agent.process(task)

        assert result["model_used"] == "gpt-4"
        assert provider.call_history[0]["model"] == "gpt-4"

    def test_agent_process_task_override_model(self):
        """Test that task payload can override agent's default model."""
        provider = MockLLMProvider(track_calls=True, mock_response="OK")
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider, model="gpt-4")

        task = Task(
            agent_id="test-agent", payload={"user_message": "Test", "model": "claude-3-opus"}
        )

        result = agent.process(task)

        assert result["model_used"] == "claude-3-opus"
        assert provider.call_history[0]["model"] == "claude-3-opus"

    def test_agent_builds_messages_correctly(self):
        """Test that agent builds message list correctly."""
        provider = MockLLMProvider(track_calls=True, mock_response="OK")
        agent = SimpleLLMAgent(
            agent_id="test-agent", provider=provider, system_prompt="Be concise."
        )

        task = Task(agent_id="test-agent", payload={"user_message": "What is 2+2?"})

        agent.process(task)

        messages = provider.call_history[0]["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "Be concise."
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "What is 2+2?"

    def test_agent_includes_context_in_system_message(self):
        """Test that agent includes context in system message."""
        provider = MockLLMProvider(track_calls=True, mock_response="OK")
        agent = SimpleLLMAgent(
            agent_id="test-agent", provider=provider, system_prompt="Base prompt."
        )

        task = Task(
            agent_id="test-agent",
            payload={"user_message": "Hello", "context": {"mode": "friendly", "lang": "en"}},
        )

        agent.process(task)

        messages = provider.call_history[0]["messages"]
        system_content = messages[0]["content"]

        assert "Base prompt." in system_content
        assert "mode: friendly" in system_content
        assert "lang: en" in system_content

    def test_agent_raises_on_missing_user_message(self):
        """Test that agent raises ValueError if user_message is missing."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)

        task = Task(agent_id="test-agent", payload={"other_field": "value"})

        with pytest.raises(ValueError, match="must contain 'user_message'"):
            agent.process(task)

    def test_agent_raises_on_non_dict_payload(self):
        """Test that agent raises ValueError if payload is not a dict."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)

        task = Task(agent_id="test-agent", payload="not a dict")

        with pytest.raises(ValueError, match="must be a dict"):
            agent.process(task)

    def test_agent_handles_provider_error(self):
        """Test that agent handles provider errors gracefully."""

        class FailingProvider(LLMProvider):
            def chat(self, messages, model=None, **kwargs):
                raise RuntimeError("API call failed")

            @property
            def system_prompt(self):
                return "Test"

        provider = FailingProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)

        task = Task(agent_id="test-agent", payload={"user_message": "Hello"})

        with pytest.raises(LLMError, match="LLM call failed"):
            agent.process(task)

    def test_agent_update_system_prompt(self):
        """Test that agent can update system prompt."""
        provider = MockLLMProvider(track_calls=True, mock_response="OK")
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider, system_prompt="Original")

        agent.update_system_prompt("Updated")

        task = Task(agent_id="test-agent", payload={"user_message": "Test"})
        agent.process(task)

        messages = provider.call_history[0]["messages"]
        assert messages[0]["content"] == "Updated"


class TestKernelLLMIntegration:
    """Test 3: Full stack integration (Kernel → Agent → LLM → Ledger)."""

    def test_kernel_processes_llm_task(self):
        """Test that kernel can process a task via SimpleLLMAgent."""
        # Create kernel with in-memory ledger
        kernel = VibeKernel(ledger_path=":memory:")

        # Create mock provider and agent
        provider = MockLLMProvider(mock_response="I am a mock response")
        agent = SimpleLLMAgent(
            agent_id="llm-agent", provider=provider, system_prompt="You are helpful."
        )

        # Register agent and boot kernel
        kernel.register_agent(agent)
        kernel.boot()

        # Submit task
        task = Task(agent_id="llm-agent", payload={"user_message": "Hello, AI!"})
        kernel.submit(task)

        # Process task
        kernel.tick()

        # Verify ledger recorded the interaction
        record = kernel.ledger.get_task(task.id)

        assert record is not None
        assert record["status"] == "COMPLETED"
        assert record["agent_id"] == "llm-agent"
        assert record["input_payload"]["user_message"] == "Hello, AI!"
        assert record["output_result"]["response"] == "I am a mock response"
        assert record["output_result"]["success"] is True

    def test_kernel_records_llm_failure(self):
        """Test that kernel records LLM failures to ledger."""

        class FailingProvider(LLMProvider):
            def chat(self, messages, model=None, **kwargs):
                raise RuntimeError("API timeout")

            @property
            def system_prompt(self):
                return "Test"

        kernel = VibeKernel(ledger_path=":memory:")
        provider = FailingProvider()
        agent = SimpleLLMAgent(agent_id="llm-agent", provider=provider)

        kernel.register_agent(agent)
        kernel.boot()

        task = Task(agent_id="llm-agent", payload={"user_message": "Test"})
        kernel.submit(task)

        # Task should fail
        with pytest.raises(LLMError):
            kernel.tick()

        # Verify ledger recorded the failure
        record = kernel.ledger.get_task(task.id)

        assert record is not None
        assert record["status"] == "FAILED"
        assert "LLMError" in record["error_message"]
        assert "API timeout" in record["error_message"]

    def test_kernel_processes_multiple_llm_tasks(self):
        """Test that kernel can process multiple LLM tasks in sequence."""
        kernel = VibeKernel(ledger_path=":memory:")

        # Create provider that tracks calls
        provider = MockLLMProvider(track_calls=True, mock_response="Response")
        agent = SimpleLLMAgent(agent_id="llm-agent", provider=provider)

        kernel.register_agent(agent)
        kernel.boot()

        # Submit multiple tasks
        tasks = []
        for i in range(3):
            task = Task(agent_id="llm-agent", payload={"user_message": f"Message {i}"})
            tasks.append(task)
            kernel.submit(task)

        # Process all tasks
        while kernel.tick():
            pass

        # Verify all tasks were processed
        assert provider.get_call_count() == 3

        # Verify ledger has all tasks
        history = kernel.ledger.get_history(limit=10)
        assert len(history) == 3
        assert all(r["status"] == "COMPLETED" for r in history)

    def test_kernel_llm_integration_with_different_messages(self):
        """Test full integration with varied user messages."""
        kernel = VibeKernel(ledger_path=":memory:")

        provider = MockLLMProvider(track_calls=True, mock_response="OK")
        agent = SimpleLLMAgent(agent_id="llm-agent", provider=provider, system_prompt="Be concise.")

        kernel.register_agent(agent)
        kernel.boot()

        # Test different message types
        messages = [
            "What is Python?",
            "How do I write a function?",
            "Explain async/await",
        ]

        for msg in messages:
            task = Task(agent_id="llm-agent", payload={"user_message": msg})
            kernel.submit(task)
            kernel.tick()

        # Verify all messages were sent to provider
        assert provider.get_call_count() == 3

        for i, msg in enumerate(messages):
            call_messages = provider.call_history[i]["messages"]
            user_message = call_messages[1]  # Second message is user
            assert user_message["content"] == msg

    def test_kernel_statistics_with_llm_tasks(self):
        """Test that ledger statistics reflect LLM task execution."""
        kernel = VibeKernel(ledger_path=":memory:")

        # Create two agents
        provider1 = MockLLMProvider(mock_response="Agent 1")
        provider2 = MockLLMProvider(mock_response="Agent 2")

        agent1 = SimpleLLMAgent(agent_id="agent-1", provider=provider1)
        agent2 = SimpleLLMAgent(agent_id="agent-2", provider=provider2)

        kernel.register_agent(agent1)
        kernel.register_agent(agent2)
        kernel.boot()

        # Submit tasks to both agents
        for i in range(3):
            task1 = Task(agent_id="agent-1", payload={"user_message": f"To agent 1: {i}"})
            task2 = Task(agent_id="agent-2", payload={"user_message": f"To agent 2: {i}"})
            kernel.submit(task1)
            kernel.submit(task2)

        # Process all
        while kernel.tick():
            pass

        # Check statistics
        stats = kernel.ledger.get_statistics()

        assert stats["total_tasks"] == 6
        assert stats["completed"] == 6
        assert stats["failed"] == 0
        assert len(stats["agents"]) == 2
        assert "agent-1" in stats["agents"]
        assert "agent-2" in stats["agents"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
