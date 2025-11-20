"""
Test Provider Factory (GAD-511)
================================

Tests for the factory pattern that creates and configures LLM providers.
"""

import os
from unittest.mock import patch

from agency_os.core_system.runtime.providers.base import NoOpProvider
from agency_os.core_system.runtime.providers.factory import (
    _detect_provider,
    _get_api_key_for_provider,
)


class TestDetectProvider:
    """Test provider auto-detection logic"""

    def test_detect_google_when_google_key_set(self):
        """Should detect Google provider when GOOGLE_API_KEY is set"""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "valid-key"}, clear=True):
            assert _detect_provider() == "google"

    def test_detect_anthropic_when_anthropic_key_set(self):
        """Should detect Anthropic provider when ANTHROPIC_API_KEY is set"""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "valid-key"}, clear=True):
            assert _detect_provider() == "anthropic"

    def test_detect_openai_when_openai_key_set(self):
        """Should detect OpenAI provider when OPENAI_API_KEY is set"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "valid-key"}, clear=True):
            assert _detect_provider() == "openai"

    def test_detect_noop_when_no_keys_set(self):
        """Should fall back to noop when no API keys are set"""
        with patch.dict(os.environ, {}, clear=True):
            assert _detect_provider() == "noop"

    def test_google_takes_priority_over_others(self):
        """Google should have priority in detection order"""
        with patch.dict(
            os.environ,
            {
                "GOOGLE_API_KEY": "google-key",
                "ANTHROPIC_API_KEY": "anthropic-key",
            },
            clear=True,
        ):
            assert _detect_provider() == "google"

    def test_reject_placeholder_keys(self):
        """Should reject placeholder values as invalid keys"""
        placeholder_values = [
            "your-api-key-here",
            "xxx",
            "placeholder",
            "example",
            "test-key",
        ]

        for value in placeholder_values:
            with patch.dict(os.environ, {"GOOGLE_API_KEY": value}, clear=True):
                assert _detect_provider() == "noop"


class TestGetApiKeyForProvider:
    """Test API key retrieval for providers"""

    def test_get_google_api_key(self):
        """Should retrieve Google API key from environment"""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "my-google-key"}):
            key = _get_api_key_for_provider("google")
            assert key == "my-google-key"

    def test_get_anthropic_api_key(self):
        """Should retrieve Anthropic API key from environment"""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "my-anthropic-key"}):
            key = _get_api_key_for_provider("anthropic")
            assert key == "my-anthropic-key"

    def test_get_openai_api_key(self):
        """Should retrieve OpenAI API key from environment"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "my-openai-key"}):
            key = _get_api_key_for_provider("openai")
            assert key == "my-openai-key"

    def test_local_provider_needs_no_key(self):
        """Local provider should not require API key"""
        key = _get_api_key_for_provider("local")
        assert key is None

    def test_noop_provider_needs_no_key(self):
        """NoOp provider should not require API key"""
        key = _get_api_key_for_provider("noop")
        assert key is None

    def test_unknown_provider_returns_none(self):
        """Unknown provider should return None for API key"""
        key = _get_api_key_for_provider("unknown")
        assert key is None


class TestProviderFactoryIntegration:
    """Integration tests for provider factory"""

    def test_noop_provider_always_available(self):
        """NoOp provider should always be available"""
        noop = NoOpProvider()
        assert noop.is_available() is True

    def test_noop_provider_returns_zero_cost(self):
        """NoOp provider should have zero cost"""
        noop = NoOpProvider()
        cost = noop.calculate_cost(1000, 500, "noop")
        assert cost == 0.0

    def test_noop_provider_returns_empty_models_list(self):
        """NoOp provider should return empty models"""
        noop = NoOpProvider()
        models = noop.get_available_models()
        assert models == ["noop"]

    def test_noop_provider_returns_mock_response(self):
        """NoOp provider should return mock response"""
        noop = NoOpProvider()
        result = noop.invoke("test prompt", model="noop")

        assert result.content == "{}"  # Empty JSON
        assert result.usage.input_tokens == 0
        assert result.usage.output_tokens == 0
        assert result.usage.cost_usd == 0.0
        assert result.provider == "noop"
