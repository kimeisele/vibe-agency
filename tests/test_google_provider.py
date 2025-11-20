"""
Google Provider Tests (GAD-511)
================================

Tests for Google Gemini provider initialization, invocation, and cost calculation.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.runtime.providers.base import ProviderNotAvailableError

# Mock the google.generativeai module
mock_genai = MagicMock()


@pytest.fixture(autouse=True)
def mock_google_genai():
    """Mock Google Generative AI module"""
    with patch.dict(sys.modules, {"google.generativeai": mock_genai}):
        yield


class TestGoogleProviderInitialization:
    """Test Google provider initialization and configuration"""

    def test_initialization_with_valid_api_key(self):
        """Should initialize GoogleProvider with valid API key"""
        from vibe_core.runtime.providers.google import GoogleProvider

        provider = GoogleProvider(api_key="valid-key")
        assert provider.api_key == "valid-key"
        mock_genai.configure.assert_called_with(api_key="valid-key")

    def test_initialization_with_none_api_key_raises_error(self):
        """Should raise error when initialized with None API key"""
        from vibe_core.runtime.providers.google import GoogleProvider

        with pytest.raises(ProviderNotAvailableError):
            GoogleProvider(api_key=None)

    def test_get_provider_name(self):
        """Should return correct provider name"""
        from vibe_core.runtime.providers.google import GoogleProvider

        provider = GoogleProvider(api_key="test-key")
        assert provider.get_provider_name() == "Google"

    def test_is_available_with_valid_key(self):
        """Should report available when API key is set"""
        from vibe_core.runtime.providers.google import GoogleProvider

        provider = GoogleProvider(api_key="valid-key")
        assert provider.is_available() is True


class TestGoogleProviderInvocation:
    """Test Google provider LLM invocation"""

    def test_invoke_with_valid_response(self):
        """Should invoke and return properly formatted response"""
        from vibe_core.runtime.providers.google import GoogleProvider

        provider = GoogleProvider(api_key="valid-key")

        # Mock the response
        mock_response = MagicMock()
        mock_response.text = "This is a test response"

        mock_usage = MagicMock()
        mock_usage.prompt_token_count = 15
        mock_usage.candidates_token_count = 25
        mock_response.usage_metadata = mock_usage

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        result = provider.invoke("Test prompt", model="gemini-1.5-flash")

        assert result.content == "This is a test response"
        assert result.usage.input_tokens == 15
        assert result.usage.output_tokens == 25
        assert result.provider == "google"


class TestGoogleProviderCostCalculation:
    """Test Google provider cost calculation"""

    def test_calculate_cost_for_gemini_1_5_flash(self):
        """Should calculate cost for gemini-1.5-flash model"""
        from vibe_core.runtime.providers.google import GoogleProvider

        provider = GoogleProvider(api_key="valid-key")

        # Gemini 1.5 Flash: $0.075 input, $0.30 output per MTok
        cost = provider.calculate_cost(
            input_tokens=1000, output_tokens=500, model="gemini-1.5-flash"
        )

        # Expected: (1000 * 0.075 / 1_000_000) + (500 * 0.30 / 1_000_000)
        # = 0.000075 + 0.00015 = 0.000225
        assert cost > 0
        assert cost < 0.001

    def test_calculate_cost_with_zero_tokens(self):
        """Should handle zero tokens correctly"""
        from vibe_core.runtime.providers.google import GoogleProvider

        provider = GoogleProvider(api_key="valid-key")

        cost = provider.calculate_cost(input_tokens=0, output_tokens=0, model="gemini-1.5-flash")

        assert cost == 0.0

    def test_calculate_cost_for_free_preview_model(self):
        """Should have zero cost for free preview models"""
        from vibe_core.runtime.providers.google import GoogleProvider

        provider = GoogleProvider(api_key="valid-key")

        # Gemini 2.5 Flash is free during preview
        cost = provider.calculate_cost(
            input_tokens=10000, output_tokens=5000, model="gemini-2.5-flash-exp"
        )

        assert cost == 0.0


class TestGoogleProviderAvailableModels:
    """Test available models for Google provider"""

    def test_get_available_models_returns_list(self):
        """Should return list of available models"""
        from vibe_core.runtime.providers.google import GoogleProvider

        provider = GoogleProvider(api_key="valid-key")
        models = provider.get_available_models()

        assert isinstance(models, list)
        assert len(models) > 0

    def test_available_models_includes_gemini_variants(self):
        """Should include various Gemini model variants"""
        from vibe_core.runtime.providers.google import GoogleProvider

        provider = GoogleProvider(api_key="valid-key")
        models = provider.get_available_models()

        # Should include at least Gemini 1.5 Flash
        assert "gemini-1.5-flash" in models
