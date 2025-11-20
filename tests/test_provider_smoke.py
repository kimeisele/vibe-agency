import sys
from unittest.mock import MagicMock, patch

import pytest

# Define mocks
mock_genai = MagicMock()
mock_anthropic = MagicMock()
mock_anthropic_client = MagicMock()
mock_anthropic.Anthropic.return_value = mock_anthropic_client

# We need to patch sys.modules during the TEST EXECUTION, not just import.
# But we also need to import the classes.
# Since the classes import the modules inside __init__, we can import classes globally
# and then patch sys.modules when calling __init__.

from agency_os.core_system.runtime.providers.anthropic import AnthropicProvider
from agency_os.core_system.runtime.providers.google import GoogleProvider


@pytest.fixture(autouse=True)
def mock_providers():
    with patch.dict(sys.modules, {"google.generativeai": mock_genai, "anthropic": mock_anthropic}):
        yield


class TestGoogleProviderSmoke:
    def test_initialization(self):
        """Test that GoogleProvider initializes correctly."""
        provider = GoogleProvider(api_key="fake_key")
        assert provider.api_key == "fake_key"
        # Check if genai.configure was called
        provider.genai.configure.assert_called_with(api_key="fake_key")

    def test_invoke_mock(self):
        """Test basic invocation with mocked backend."""
        provider = GoogleProvider(api_key="fake_key")

        # Mock the response
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Hello from Gemini"
        # Mock usage metadata
        mock_usage = MagicMock()
        mock_usage.prompt_token_count = 10
        mock_usage.candidates_token_count = 5
        mock_response.usage_metadata = mock_usage

        mock_model.generate_content.return_value = mock_response
        provider.genai.GenerativeModel.return_value = mock_model

        response = provider.invoke("Hello")

        assert response.content == "Hello from Gemini"
        assert response.usage.input_tokens == 10
        assert response.usage.output_tokens == 5
        assert response.provider == "google"


class TestAnthropicProviderSmoke:
    def test_initialization(self):
        """Test that AnthropicProvider initializes correctly."""
        provider = AnthropicProvider(api_key="fake_key")
        assert provider.api_key == "fake_key"
        assert provider.client is not None

    def test_invoke_mock(self):
        """Test basic invocation with mocked backend."""
        provider = AnthropicProvider(api_key="fake_key")

        # Mock the response
        mock_message = MagicMock()
        mock_content = MagicMock()
        mock_content.text = "Hello from Claude"
        mock_message.content = [mock_content]
        mock_message.usage.input_tokens = 10
        mock_message.usage.output_tokens = 5
        mock_message.model = "claude-3-5-sonnet-20241022"
        mock_message.stop_reason = "end_turn"

        provider.client.messages.create.return_value = mock_message

        response = provider.invoke("Hello")

        assert response.content == "Hello from Claude"
        assert response.usage.input_tokens == 10
        assert response.usage.output_tokens == 5
        assert response.provider == "anthropic"
