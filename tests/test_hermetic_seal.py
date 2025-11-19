#!/usr/bin/env python3
"""
Hermetic Seal Verification Test - CRITICAL SECURITY TEST

This test verifies that the system is "hermetically sealed":
- LLMClient defaults to NoOpProvider in test environment
- Cost tracking shows $0.00 when using default provider
- System gracefully handles missing API keys without crashes

Law: "We trust the code because we've verified the seal."
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add runtime to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "agency_os" / "00_system"))


class TestHermeticSeal:
    """Verify system is hermetically sealed - no real API calls"""

    def test_llm_client_defaults_to_noop_provider(self):
        """LLMClient defaults to NoOpProvider when no API keys present"""
        from runtime.llm_client import LLMClient

        # Clear environment variables that might set real providers
        with patch.dict("os.environ", clear=True):
            client = LLMClient()

            # Verify it's using NoOpProvider (cost = $0.00)
            assert client.provider is not None
            provider_name = client.provider.get_provider_name().lower()
            assert provider_name in [
                "noop",
                "mock",
            ]

    def test_llm_client_invocation_with_noop_costs_zero(self):
        """LLMClient invocation with NoOpProvider has $0.00 cost"""
        from runtime.llm_client import LLMClient

        with patch.dict("os.environ", clear=True):
            client = LLMClient()

            # Make a "real" invocation
            response = client.invoke(prompt="Test prompt", max_tokens=100)

            # Verify response structure
            assert response is not None
            assert hasattr(response, "usage")
            assert hasattr(response.usage, "cost_usd")

            # CRITICAL: Verify cost is zero
            assert response.usage.cost_usd == 0.0, (
                "NoOp provider must have zero cost\n"
                f"Got: ${response.usage.cost_usd:.2f}\n"
                "This indicates a real provider was used!"
            )

    def test_no_api_key_no_crash(self):
        """System doesn't crash when API keys are missing"""
        from runtime.llm_client import LLMClient

        with patch.dict("os.environ", clear=True):
            try:
                client = LLMClient()
                response = client.invoke(prompt="test")
                assert response is not None
                assert response.usage.cost_usd == 0.0
            except Exception as e:
                pytest.fail(f"LLMClient should handle missing keys gracefully: {e}")

    def test_quota_manager_pure_logic(self):
        """OperationalQuota manager is pure logic, no I/O"""
        from runtime.quota_manager import OperationalQuota, QuotaLimits

        # These operations should never make external calls
        quota = OperationalQuota(QuotaLimits())

        # Pre-flight check (pure logic)
        can_execute, reason = quota.check_before_request(estimated_tokens=100)
        assert can_execute

        # Record usage (pure logic)
        quota.record_request(tokens_used=100, cost_usd=0.01)

        # Verify tracking
        assert quota.metrics.total_cost_usd >= 0.0
        assert quota.metrics.total_requests == 1

    def test_circuit_breaker_pure_logic(self):
        """Circuit Breaker is pure state machine, no I/O"""
        from runtime.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

        breaker = CircuitBreaker(CircuitBreakerConfig())

        # Check if can execute (pure logic)
        can_execute, reason = breaker.can_execute()
        assert isinstance(can_execute, bool)

        # Get status (pure logic)
        status = breaker.get_status()
        assert status is not None
        assert "state" in status

        # Reset (pure logic)
        breaker.reset()

        # All succeeded - state transitions work
        assert True

    def test_orchestrator_initialization_safe(self):
        """CoreOrchestrator initializes safely with no credentials"""
        from orchestrator import CoreOrchestrator

        with patch.dict("os.environ", clear=True):
            try:
                orchestrator = CoreOrchestrator(
                    repo_root=repo_root,
                    execution_mode="autonomous",
                )
                assert orchestrator is not None
            except Exception as e:
                pytest.fail(f"CoreOrchestrator should initialize safely: {e}")

    def test_provider_factory_fallback_to_noop(self):
        """Provider factory safely falls back to NoOp"""
        from runtime.providers.factory import get_default_provider

        with patch.dict("os.environ", clear=True):
            # No API keys set
            provider = get_default_provider()

            # Should get NoOp, not fail
            assert provider is not None
            assert provider.get_provider_name().lower() in ["noop", "mock"]

    def test_zero_cost_multiple_invocations(self):
        """Multiple invocations maintain zero cost"""
        from runtime.llm_client import LLMClient

        with patch.dict("os.environ", clear=True):
            client = LLMClient()

            # Multiple invocations
            total_cost = 0.0
            for i in range(5):
                response = client.invoke(
                    prompt=f"Test {i}",
                    max_tokens=100,
                )
                total_cost += response.usage.cost_usd

            # Total should be zero
            assert total_cost == 0.0, f"Total cost should be $0.00, got ${total_cost:.2f}"

    def test_quota_tracks_zero_cost(self):
        """Quota manager correctly tracks zero costs"""
        from runtime.quota_manager import OperationalQuota, QuotaLimits

        quota = OperationalQuota(QuotaLimits())

        # Record multiple zero-cost operations
        for i in range(10):
            quota.record_request(tokens_used=100, cost_usd=0.0)

        # Total cost should be zero
        assert quota.metrics.total_cost_usd == 0.0

    def test_prompt_registry_safe_composition(self):
        """PromptRegistry composes prompts without external calls"""
        from runtime.prompt_registry import PromptRegistry

        with patch.dict("os.environ", clear=True):
            try:
                prompt = PromptRegistry.compose(
                    agent="VIBE_ALIGNER",
                    task="02_feature_extraction",
                    workspace="ROOT",
                    inject_governance=False,
                )

                assert prompt is not None
                assert isinstance(prompt, str)
                assert len(prompt) > 0
            except Exception as e:
                pytest.fail(f"PromptRegistry should compose safely: {e}")

    @pytest.mark.parametrize(
        "missing_var",
        [
            "ANTHROPIC_API_KEY",
            "GOOGLE_API_KEY",
            "OPENAI_API_KEY",
        ],
    )
    def test_missing_single_api_key(self, missing_var):
        """System handles any single missing API key"""
        with patch.dict("os.environ", {}, clear=True):
            # Verify the key is not set
            assert missing_var not in __import__("os").environ

            from runtime.llm_client import LLMClient

            # Should initialize without error
            client = LLMClient()
            assert client is not None


class TestHermeticSealSecurityCritical:
    """Security-critical tests for the hermetic seal"""

    def test_no_live_fire_without_env_var(self):
        """Live API calls require explicit VIBE_LIVE_FIRE environment variable"""
        from runtime.llm_client import LLMClient

        with patch.dict("os.environ", {}, clear=True):
            # VIBE_LIVE_FIRE not set
            assert "VIBE_LIVE_FIRE" not in __import__("os").environ

            client = LLMClient()

            # Should use NoOp, not real provider
            assert client.provider.get_provider_name().lower() in ["noop", "mock"]

    def test_cost_audit_trail(self):
        """Cost tracking maintains audit trail"""
        from runtime.llm_client import LLMClient
        from runtime.quota_manager import OperationalQuota, QuotaLimits

        with patch.dict("os.environ", clear=True):
            client = LLMClient()
            quota = OperationalQuota(QuotaLimits())

            # Make 10 invocations
            for i in range(10):
                response = client.invoke(prompt=f"Test {i}")
                quota.record_request(
                    tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                    cost_usd=response.usage.cost_usd,
                )

            # Total should still be $0.00
            assert quota.metrics.total_cost_usd == 0.0, (
                f"Audit trail shows cost=${quota.metrics.total_cost_usd:.2f}\n"
                "This should be $0.00 for NoOp provider"
            )

    def test_graceful_degradation_no_crashes(self):
        """System never crashes due to missing credentials"""
        with patch.dict("os.environ", {}, clear=True):
            # Import all critical components
            from runtime.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
            from runtime.llm_client import LLMClient
            from runtime.quota_manager import OperationalQuota, QuotaLimits

            # All should initialize without error
            try:
                client = LLMClient()
                quota = OperationalQuota(QuotaLimits())
                breaker = CircuitBreaker(CircuitBreakerConfig())

                # Use them
                response = client.invoke(prompt="test")
                quota.record_request(
                    tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                    cost_usd=response.usage.cost_usd,
                )
                can_execute, reason = breaker.can_execute()

                # Should all complete successfully
                assert True
            except Exception as e:
                pytest.fail(f"System crashed instead of gracefully degrading: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
