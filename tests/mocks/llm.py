"""
Mock LLM provider for testing.

This module provides a mock LLM provider that returns predictable
responses without making actual API calls. Used for unit testing
to avoid costs and latency.
"""

from vibe_core.llm import LLMProvider


class MockLLMProvider(LLMProvider):
    """
    Mock LLM provider for testing.

    Returns predictable responses without calling real APIs.
    Useful for:
    - Unit tests (fast, no API costs)
    - Integration tests (deterministic responses)
    - Development (no API keys needed)

    Example:
        >>> provider = MockLLMProvider()
        >>> response = provider.chat([{"role": "user", "content": "Hello"}])
        >>> print(response)  # "I am a mock response"
    """

    def __init__(
        self,
        mock_response: str = "I am a mock response",
        system_prompt_text: str = "You are a helpful mock assistant.",
        track_calls: bool = False,
    ):
        """
        Initialize the mock provider.

        Args:
            mock_response: The response to return from all chat() calls
            system_prompt_text: The system prompt to return
            track_calls: If True, track all calls in self.call_history

        Example:
            >>> provider = MockLLMProvider(mock_response="Test response")
            >>> provider.chat([{"role": "user", "content": "Hi"}])
            "Test response"
        """
        self._mock_response = mock_response
        self._system_prompt_text = system_prompt_text
        self._track_calls = track_calls
        self.call_history: list[dict] = []

    def chat(self, messages: list[dict[str, str]], model: str | None = None, **kwargs) -> str:
        """
        Return the mock response (no actual API call).

        Args:
            messages: List of message dicts (ignored in mock)
            model: Model identifier (ignored in mock)
            **kwargs: Additional parameters (ignored in mock)

        Returns:
            str: The pre-configured mock response

        Example:
            >>> provider = MockLLMProvider(mock_response="42")
            >>> provider.chat([{"role": "user", "content": "What is 2+2?"}])
            "42"
        """
        if self._track_calls:
            self.call_history.append({"messages": messages, "model": model, "kwargs": kwargs})

        return self._mock_response

    @property
    def system_prompt(self) -> str:
        """
        Return the mock system prompt.

        Returns:
            str: The pre-configured system prompt

        Example:
            >>> provider = MockLLMProvider(system_prompt_text="Be helpful.")
            >>> print(provider.system_prompt)
            "Be helpful."
        """
        return self._system_prompt_text

    def set_mock_response(self, response: str) -> None:
        """
        Update the mock response (useful for testing different scenarios).

        Args:
            response: New response to return from chat()

        Example:
            >>> provider = MockLLMProvider()
            >>> provider.set_mock_response("New response")
            >>> provider.chat([{"role": "user", "content": "Hi"}])
            "New response"
        """
        self._mock_response = response

    def get_call_count(self) -> int:
        """
        Get the number of times chat() was called (if tracking enabled).

        Returns:
            int: Number of calls, or 0 if tracking disabled

        Example:
            >>> provider = MockLLMProvider(track_calls=True)
            >>> provider.chat([{"role": "user", "content": "Hi"}])
            >>> provider.get_call_count()
            1
        """
        return len(self.call_history) if self._track_calls else 0

    def clear_history(self) -> None:
        """
        Clear the call history (if tracking enabled).

        Example:
            >>> provider = MockLLMProvider(track_calls=True)
            >>> provider.chat([{"role": "user", "content": "Hi"}])
            >>> provider.clear_history()
            >>> provider.get_call_count()
            0
        """
        if self._track_calls:
            self.call_history.clear()
