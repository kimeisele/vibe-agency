"""
Tests for StewardProvider (ARCH-033C).

Validates the Claude Code integration provider works correctly,
delegating cognitive work to the STEWARD (Claude Code environment).
"""

from unittest.mock import patch

from vibe_core.llm import StewardProvider


class TestStewardProvider:
    """Test suite for StewardProvider."""

    def test_initialization(self):
        """Provider initializes without errors."""
        provider = StewardProvider()
        assert provider is not None
        assert provider.system_prompt is not None

    def test_system_prompt(self):
        """System prompt references STEWARD role."""
        provider = StewardProvider()
        prompt = provider.system_prompt
        assert isinstance(prompt, str)
        assert "STEWARD" in prompt or "Claude Code" in prompt

    def test_repr(self):
        """String representation is valid."""
        provider = StewardProvider()
        repr_str = repr(provider)
        assert "StewardProvider" in repr_str

    @patch("sys.stdin.isatty", return_value=False)
    def test_chat_non_interactive_environment(self, mock_isatty):
        """Returns error message when called in non-interactive environment (CI/CD)."""
        provider = StewardProvider()
        messages = [{"role": "user", "content": "Hello"}]

        response = provider.chat(messages)

        assert "ERROR" in response
        assert "stdin is not a TTY" in response
        mock_isatty.assert_called_once()

    @patch("sys.stdin.isatty", return_value=True)
    @patch("builtins.input", return_value="Steward completion here")
    def test_chat_interactive_environment(self, mock_input, mock_isatty):
        """Prompts STEWARD and returns completion in interactive environment."""
        provider = StewardProvider()
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "What is 2+2?"},
        ]

        response = provider.chat(messages)

        assert response == "Steward completion here"
        mock_isatty.assert_called_once()
        mock_input.assert_called_once()

    @patch("sys.stdin.isatty", return_value=True)
    @patch("builtins.input", return_value="")
    def test_chat_empty_completion(self, mock_input, mock_isatty):
        """Handles empty STEWARD completion gracefully."""
        provider = StewardProvider()
        messages = [{"role": "user", "content": "Hello"}]

        response = provider.chat(messages)

        assert response == "(No completion provided by STEWARD)"
        mock_input.assert_called_once()

    @patch("sys.stdin.isatty", return_value=True)
    @patch("builtins.input", side_effect=KeyboardInterrupt)
    def test_chat_keyboard_interrupt(self, mock_input, mock_isatty):
        """Handles keyboard interrupt (Ctrl+C) gracefully."""
        provider = StewardProvider()
        messages = [{"role": "user", "content": "Hello"}]

        response = provider.chat(messages)

        assert response == "(STEWARD intervention interrupted)"
        mock_input.assert_called_once()

    @patch("sys.stdin.isatty", return_value=True)
    @patch("builtins.input", side_effect=EOFError)
    def test_chat_eof_error(self, mock_input, mock_isatty):
        """Handles EOF (Ctrl+D) gracefully."""
        provider = StewardProvider()
        messages = [{"role": "user", "content": "Hello"}]

        response = provider.chat(messages)

        assert response == "(STEWARD intervention interrupted)"
        mock_input.assert_called_once()

    def test_messages_to_prompt_formatting(self):
        """Message-to-prompt conversion formats correctly."""
        provider = StewardProvider()
        messages = [
            {"role": "system", "content": "Be concise."},
            {"role": "user", "content": "What is AI?"},
        ]

        prompt = provider._messages_to_prompt(messages)

        assert "SYSTEM: Be concise." in prompt
        assert "USER: What is AI?" in prompt

    def test_messages_to_prompt_empty(self):
        """Empty messages handled gracefully."""
        provider = StewardProvider()
        messages = []

        prompt = provider._messages_to_prompt(messages)

        assert prompt == "(empty prompt)"

    def test_messages_to_prompt_filters_empty_content(self):
        """Empty content messages are filtered out."""
        provider = StewardProvider()
        messages = [
            {"role": "system", "content": "Be helpful."},
            {"role": "user", "content": ""},  # Empty - should be filtered
            {"role": "user", "content": "Hello"},
        ]

        prompt = provider._messages_to_prompt(messages)

        assert "SYSTEM: Be helpful." in prompt
        assert "USER: Hello" in prompt
        assert prompt.count("USER:") == 1  # Only one USER line (empty filtered)
