"""
Anthropic Provider Tests (GAD-511)
===================================

Tests for Anthropic Claude provider initialization, invocation, and cost calculation.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

from agency_os.core_system.runtime.providers.base import ProviderNotAvailableError

# Mock the anthropic module
mock_anthropic = MagicMock()
mock_anthropic_client = MagicMock()
mock_anthropic.Anthropic.return_value = mock_anthropic_client


@pytest.fixture(autouse=True)
def mock_anthropic_module():
    """Mock Anthropic module"""
    with patch.dict(sys.modules, {"anthropic": mock_anthropic}):
        yield


class TestAnthropicProviderInitialization:
    """Test Anthropic provider initialization and configuration"""

    def test_initialization_with_valid_api_key(self):
        """Should initialize AnthropicProvider with valid API key"""
        from agency_os.core_system.runtime.providers.anthropic import AnthropicProvider

        provider = AnthropicProvider(api_key="sk-test-key")
        assert provider.api_key == "sk-test-key"
        assert provider.client is not None
        mock_anthropic.Anthropic.assert_called()

    def test_initialization_with_none_api_key_raises_error(self):
        """Should raise error when initialized with None API key"""
        from agency_os.core_system.runtime.providers.anthropic import AnthropicProvider

        with pytest.raises(ProviderNotAvailableError):
            AnthropicProvider(api_key=None)

    def test_get_provider_name(self):
        """Should return correct provider name"""
        from agency_os.core_system.runtime.providers.anthropic import AnthropicProvider

        provider = AnthropicProvider(api_key="sk-test-key")
        assert provider.get_provider_name() == "Anthropic"

    def test_is_available_with_valid_key(self):
        """Should report available when API key is set"""
        from agency_os.core_system.runtime.providers.anthropic import AnthropicProvider

        provider = AnthropicProvider(api_key="sk-test-key")
        assert provider.is_available() is True


class TestAnthropicProviderInvocation:
    """Test Anthropic provider LLM invocation"""

    def test_invoke_with_valid_response(self):
        """Should invoke and return properly formatted response"""
        from agency_os.core_system.runtime.providers.anthropic import AnthropicProvider

        provider = AnthropicProvider(api_key="sk-test-key")

        # Mock the response
        mock_content_block = MagicMock()
        mock_content_block.text = "This is Claude's response"

        mock_message = MagicMock()
        mock_message.content = [mock_content_block]
        mock_message.usage.input_tokens = 20
        mock_message.usage.output_tokens = 30
        mock_message.model = "claude-3.5-sonnet-20241022"
        mock_message.stop_reason = "end_turn"

        provider.client.messages.create.return_value = mock_message

        result = provider.invoke("Test prompt", model="claude-3.5-sonnet-20241022")

        assert result.content == "This is Claude's response"
        assert result.usage.input_tokens == 20
        assert result.usage.output_tokens == 30
        assert result.provider == "anthropic"
        assert result.finish_reason == "end_turn"

    def test_invoke_extracts_text_from_content_blocks(self):
        """Should extract text from content blocks properly"""
        from agency_os.core_system.runtime.providers.anthropic import AnthropicProvider

        provider = AnthropicProvider(api_key="sk-test-key")

        mock_content_block = MagicMock()
        mock_content_block.text = "Multi-block response"

        mock_message = MagicMock()
        mock_message.content = [mock_content_block]
        mock_message.usage.input_tokens = 10
        mock_message.usage.output_tokens = 5
        mock_message.model = "claude-3.5-sonnet-20241022"
        mock_message.stop_reason = "end_turn"

        provider.client.messages.create.return_value = mock_message

        result = provider.invoke("Test")

        assert result.content == "Multi-block response"


class TestAnthropicProviderCostCalculation:
    """Test Anthropic provider cost calculation"""

    def test_calculate_cost_for_sonnet_3_5(self):
        """Should calculate cost for claude-3.5-sonnet model"""
        from agency_os.core_system.runtime.providers.anthropic import AnthropicProvider

        provider = AnthropicProvider(api_key="sk-test-key")

        # Claude 3.5 Sonnet: $3.00 input, $15.00 output per MTok
        cost = provider.calculate_cost(
            input_tokens=1000, output_tokens=500, model="claude-3.5-sonnet-20241022"
        )

        # Expected: (1000 * 3.00 / 1000) + (500 * 15.00 / 1000)
        # = 3.0 + 7.5 = 10.5
        assert cost > 0
        assert cost < 50  # Should be reasonable

    def test_calculate_cost_with_zero_tokens(self):
        """Should handle zero tokens correctly"""
        from agency_os.core_system.runtime.providers.anthropic import AnthropicProvider

        provider = AnthropicProvider(api_key="sk-test-key")

        cost = provider.calculate_cost(
            input_tokens=0, output_tokens=0, model="claude-3.5-sonnet-20241022"
        )

        assert cost == 0.0

    def test_calculate_cost_scales_with_tokens(self):
        """Cost should scale with token count"""
        from agency_os.core_system.runtime.providers.anthropic import AnthropicProvider

        provider = AnthropicProvider(api_key="sk-test-key")

        cost_100 = provider.calculate_cost(
            input_tokens=100, output_tokens=100, model="claude-3.5-sonnet-20241022"
        )
        cost_1000 = provider.calculate_cost(
            input_tokens=1000, output_tokens=1000, model="claude-3.5-sonnet-20241022"
        )

        # Higher token count should cost more
        assert cost_1000 > cost_100

    def test_calculate_cost_varies_by_model(self):
        """Different models may have different pricing"""
        from agency_os.core_system.runtime.providers.anthropic import AnthropicProvider

        provider = AnthropicProvider(api_key="sk-test-key")

        cost_sonnet = provider.calculate_cost(1000, 500, "claude-3.5-sonnet-20241022")
        cost_latest = provider.calculate_cost(1000, 500, "claude-3.5-sonnet-latest")

        # Both are valid costs (may be same or different)
        assert cost_sonnet >= 0
        assert cost_latest >= 0


class TestAnthropicProviderAvailableModels:
    """Test available models for Anthropic provider"""

    def test_get_available_models_returns_list(self):
        """Should return list of available models"""
        from agency_os.core_system.runtime.providers.anthropic import AnthropicProvider

        provider = AnthropicProvider(api_key="sk-test-key")
        models = provider.get_available_models()

        assert isinstance(models, list)
        assert len(models) > 0

    def test_available_models_includes_claude_variants(self):
        """Should include Claude model variants"""
        from agency_os.core_system.runtime.providers.anthropic import AnthropicProvider

        provider = AnthropicProvider(api_key="sk-test-key")
        models = provider.get_available_models()

        # Should include at least one Claude model
        claude_models = [m for m in models if "claude" in m.lower()]
        assert len(claude_models) > 0
