"""
Tests for HumanProvider (ARCH-033B).

Validates the Human-in-the-Loop fallback provider works correctly
in both interactive and non-interactive environments.
"""

from unittest.mock import patch

from vibe_core.llm import HumanProvider


class TestHumanProvider:
    """Test suite for HumanProvider."""

    def test_initialization(self):
        """Provider initializes without errors."""
        provider = HumanProvider()
        assert provider is not None
        assert provider.system_prompt is not None

    def test_system_prompt(self):
        """System prompt is informational."""
        provider = HumanProvider()
        prompt = provider.system_prompt
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_repr(self):
        """String representation is valid."""
        provider = HumanProvider()
        repr_str = repr(provider)
        assert "HumanProvider" in repr_str

    @patch("sys.stdin.isatty", return_value=False)
    def test_chat_non_interactive_environment(self, mock_isatty):
        """Returns error message when called in non-interactive environment (CI/CD)."""
        provider = HumanProvider()
        messages = [{"role": "user", "content": "Hello"}]

        response = provider.chat(messages)

        assert "ERROR" in response
        assert "stdin is not a TTY" in response
        mock_isatty.assert_called_once()

    @patch("sys.stdin.isatty", return_value=True)
    @patch("builtins.input", return_value="Test response")
    def test_chat_interactive_environment(self, mock_input, mock_isatty):
        """Prompts human and returns input in interactive environment."""
        provider = HumanProvider()
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "What is 2+2?"},
        ]

        response = provider.chat(messages)

        assert response == "Test response"
        mock_isatty.assert_called_once()
        mock_input.assert_called_once()

    @patch("sys.stdin.isatty", return_value=True)
    @patch("builtins.input", return_value="")
    def test_chat_empty_input(self, mock_input, mock_isatty):
        """Handles empty input gracefully."""
        provider = HumanProvider()
        messages = [{"role": "user", "content": "Hello"}]

        response = provider.chat(messages)

        assert response == "(No response provided)"
        mock_input.assert_called_once()

    @patch("sys.stdin.isatty", return_value=True)
    @patch("builtins.input", side_effect=KeyboardInterrupt)
    def test_chat_keyboard_interrupt(self, mock_input, mock_isatty):
        """Handles keyboard interrupt (Ctrl+C) gracefully."""
        provider = HumanProvider()
        messages = [{"role": "user", "content": "Hello"}]

        response = provider.chat(messages)

        assert response == "(Human operator interrupted)"
        mock_input.assert_called_once()

    @patch("sys.stdin.isatty", return_value=True)
    @patch("builtins.input", side_effect=EOFError)
    def test_chat_eof_error(self, mock_input, mock_isatty):
        """Handles EOF (Ctrl+D) gracefully."""
        provider = HumanProvider()
        messages = [{"role": "user", "content": "Hello"}]

        response = provider.chat(messages)

        assert response == "(Human operator interrupted)"
        mock_input.assert_called_once()

    @patch("sys.stdin.isatty", return_value=True)
    @patch("builtins.input", return_value="Long response here")
    def test_chat_with_model_parameter(self, mock_input, mock_isatty):
        """Model parameter is ignored (humans don't have variants)."""
        provider = HumanProvider()
        messages = [{"role": "user", "content": "Hello"}]

        response = provider.chat(messages, model="gpt-4")

        assert response == "Long response here"
        mock_input.assert_called_once()
