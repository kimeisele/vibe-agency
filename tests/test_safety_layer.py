#!/usr/bin/env python3
"""
Test suite for GAD-509 (Circuit Breaker) and GAD-510 (Operational Quota Manager)

Tests the safety layer that protects against:
- Cascading API failures (Circuit Breaker)
- Unexpected cost spikes (Quota Manager)
- Rate limit violations (Quota Manager)
- Token consumption spikes (Quota Manager)
"""

import time
from unittest.mock import MagicMock, Mock

import pytest

from agency_os.core_system.runtime.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitBreakerState,
)
from agency_os.core_system.runtime.quota_manager import (
    OperationalQuota,
    QuotaExceededError,
    QuotaLimits,
)

# =============================================================================
# CIRCUIT BREAKER TESTS
# =============================================================================


class TestCircuitBreaker:
    """Tests for Circuit Breaker state machine and failure protection"""

    def test_circuit_breaker_initial_state_closed(self):
        """Circuit breaker starts in CLOSED state"""
        breaker = CircuitBreaker()
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0

    def test_circuit_breaker_successful_request(self):
        """Successful requests maintain CLOSED state"""
        breaker = CircuitBreaker()
        mock_func = Mock(return_value="success")

        result = breaker.call(mock_func, arg1="test")

        assert result == "success"
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.metrics.successful_requests == 1

    def test_circuit_breaker_single_failure(self):
        """Single failure doesn't trigger OPEN state"""
        breaker = CircuitBreaker(config=CircuitBreakerConfig(failure_threshold=5))
        mock_func = Mock(side_effect=ValueError("API Error"))

        with pytest.raises(ValueError):
            breaker.call(mock_func)

        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 1
        assert breaker.metrics.failed_requests == 1

    def test_circuit_breaker_threshold_opens_circuit(self):
        """Reaching failure threshold opens the circuit"""
        config = CircuitBreakerConfig(failure_threshold=3, window_size_seconds=60)
        breaker = CircuitBreaker(config=config)
        mock_func = Mock(side_effect=Exception("API Error"))

        # Trigger 3 failures
        for i in range(3):
            try:
                breaker.call(mock_func)
            except Exception:
                pass

        assert breaker.state == CircuitBreakerState.OPEN
        assert breaker.failure_count == 3

    def test_circuit_breaker_open_rejects_requests(self):
        """OPEN circuit rejects new requests"""
        config = CircuitBreakerConfig(failure_threshold=2)
        breaker = CircuitBreaker(config=config)
        mock_func = Mock(side_effect=Exception("API Error"))

        # Open the circuit
        for _ in range(2):
            try:
                breaker.call(mock_func)
            except Exception:
                pass

        # Try to make request on OPEN circuit
        with pytest.raises(CircuitBreakerOpenError):
            breaker.call(mock_func)

        assert breaker.metrics.rejected_requests == 1

    def test_circuit_breaker_recovery_timeout_transitions_to_half_open(self):
        """Circuit transitions to HALF_OPEN after recovery timeout"""
        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout_seconds=1)
        breaker = CircuitBreaker(config=config)
        mock_func = Mock(side_effect=Exception("API Error"))

        # Open the circuit
        for _ in range(2):
            try:
                breaker.call(mock_func)
            except Exception:
                pass

        assert breaker.state == CircuitBreakerState.OPEN

        # Wait for recovery timeout
        time.sleep(1.1)

        # Next request should transition to HALF_OPEN and allow execution
        mock_func = Mock(return_value="recovered")
        result = breaker.call(mock_func)

        assert result == "recovered"
        # After successful probe, transitions to CLOSED (not staying in HALF_OPEN)
        assert breaker.state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_half_open_probe_succeeds_closes_circuit(self):
        """Successful probe in HALF_OPEN transitions to CLOSED"""
        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout_seconds=1)
        breaker = CircuitBreaker(config=config)
        mock_func = Mock(side_effect=Exception("API Error"))

        # Open the circuit
        for _ in range(2):
            try:
                breaker.call(mock_func)
            except Exception:
                pass

        assert breaker.state == CircuitBreakerState.OPEN

        # Wait for recovery timeout
        time.sleep(1.1)

        # Probe succeeds - should transition through HALF_OPEN to CLOSED
        mock_func = Mock(return_value="recovered")
        breaker.call(mock_func)

        # After successful probe, transitions directly to CLOSED
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.metrics.successful_requests == 1
        assert breaker.failure_count == 0  # Failure count reset on successful probe

    def test_circuit_breaker_metrics_tracking(self):
        """Circuit breaker accurately tracks metrics"""
        breaker = CircuitBreaker()
        mock_func = Mock(return_value="result")

        # 5 successful calls
        for _ in range(5):
            breaker.call(mock_func)

        status = breaker.get_status()
        assert status["state"] == "closed"
        assert status["metrics"]["total_requests"] == 5
        assert status["metrics"]["successful_requests"] == 5

    def test_circuit_breaker_rolling_window(self):
        """Failures outside rolling window are not counted"""
        config = CircuitBreakerConfig(failure_threshold=2, window_size_seconds=1)
        breaker = CircuitBreaker(config=config)
        mock_func = Mock(side_effect=Exception("API Error"))

        # Trigger failure
        try:
            breaker.call(mock_func)
        except Exception:
            pass

        assert breaker.failure_count == 1

        # Wait for window to pass
        time.sleep(1.1)

        # Trigger another failure - should reset window
        try:
            breaker.call(mock_func)
        except Exception:
            pass

        # Only 1 failure should be counted in current window
        assert breaker.failure_count == 1


# =============================================================================
# QUOTA MANAGER TESTS
# =============================================================================


class TestQuotaManager:
    """Tests for Operational Quota Manager"""

    def test_quota_manager_initial_state(self):
        """Quota manager initializes with correct limits (GAD-510.1: Safe defaults)"""
        quota = OperationalQuota()
        status = quota.get_status()

        # GAD-510.1: Changed to safe defaults
        assert status["requests"]["limit"] == 10  # Safe default RPM
        assert status["tokens"]["limit"] == 10000  # Safe default TPM
        assert status["cost"]["limit_per_hour_usd"] == 2.0  # Safe default hourly
        assert status["cost"]["limit_per_day_usd"] == 5.0  # Safe default daily

    def test_quota_manager_check_before_request_passes(self):
        """Valid requests pass pre-flight check"""
        quota = OperationalQuota()
        # Should not raise
        quota.check_before_request(estimated_tokens=1000, operation="test_operation")

    def test_quota_manager_request_rate_limit(self):
        """Request rate limit (RPM) is enforced"""
        limits = QuotaLimits(requests_per_minute=2)
        quota = OperationalQuota(limits=limits)

        # Record 2 requests
        quota.record_request(tokens_used=100, cost_usd=0.01, operation="req1")
        quota.record_request(tokens_used=100, cost_usd=0.01, operation="req2")

        # Third request should fail
        with pytest.raises(QuotaExceededError):
            quota.check_before_request(estimated_tokens=100, operation="req3")

    def test_quota_manager_token_rate_limit(self):
        """Token per minute limit (TPM) is enforced"""
        limits = QuotaLimits(requests_per_minute=100, tokens_per_minute=1000)
        quota = OperationalQuota(limits=limits)

        # Record request with 900 tokens
        quota.record_request(tokens_used=900, cost_usd=0.05, operation="req1")

        # Try to make request with 200 tokens (would exceed 1000)
        with pytest.raises(QuotaExceededError):
            quota.check_before_request(estimated_tokens=200, operation="req2")

    def test_quota_manager_cost_per_request_limit(self):
        """Cost per request limit is enforced"""
        limits = QuotaLimits(cost_per_request_usd=0.05)  # Very low limit
        quota = OperationalQuota(limits=limits)

        # Request that would cost >$0.05
        # 20,000 tokens at 50% input/output would cost approximately:
        # 10,000 input @ $3/MTok = $0.03
        # 10,000 output @ $15/MTok = $0.15
        # Total = $0.18, which exceeds $0.05 limit
        with pytest.raises(QuotaExceededError):
            quota.check_before_request(estimated_tokens=20000, operation="expensive")

    def test_quota_manager_hourly_cost_limit(self):
        """Hourly cost limit is enforced"""
        limits = QuotaLimits(cost_per_hour_usd=1.0)
        quota = OperationalQuota(limits=limits)

        # Record request: 100,000 tokens = ~$0.90 estimated cost
        # (50,000 input @ $3/MTok = $0.15, 50,000 output @ $15/MTok = $0.75)
        quota.record_request(tokens_used=100000, cost_usd=0.90, operation="req1")

        # Try request with 50,000+ tokens that would push over $1.00/hour
        # 50,000 tokens = ~$0.45 estimated cost, $0.90 + $0.45 = $1.35 > $1.00
        with pytest.raises(QuotaExceededError):
            quota.check_before_request(estimated_tokens=50000, operation="req2")

    def test_quota_manager_daily_cost_limit(self):
        """Daily cost limit is enforced"""
        limits = QuotaLimits(cost_per_day_usd=1.0)
        quota = OperationalQuota(limits=limits)

        # Record request: 100,000 tokens = ~$0.90 estimated cost
        quota.record_request(tokens_used=100000, cost_usd=0.90, operation="req1")

        # Try request with 50,000+ tokens that would push over $1.00/day
        with pytest.raises(QuotaExceededError):
            quota.check_before_request(estimated_tokens=50000, operation="req2")

    def test_quota_manager_rolling_window_resets(self):
        """Rolling windows reset after time period"""
        limits = QuotaLimits(requests_per_minute=2)
        quota = OperationalQuota(limits=limits)

        # Record 2 requests
        quota.record_request(tokens_used=100, cost_usd=0.01, operation="req1")
        quota.record_request(tokens_used=100, cost_usd=0.01, operation="req2")

        # Check that 3rd request fails
        with pytest.raises(QuotaExceededError):
            quota.check_before_request(estimated_tokens=100, operation="req3")

        # Manually simulate minute window reset
        quota.metrics.requests_this_minute = 0
        quota.metrics.minute_start_time = time.time()

        # Now 3rd request should pass
        quota.check_before_request(estimated_tokens=100, operation="req3")

    def test_quota_manager_record_request_updates_metrics(self):
        """Recording request updates all relevant metrics"""
        quota = OperationalQuota()

        quota.record_request(tokens_used=1000, cost_usd=0.15, operation="test")

        status = quota.get_status()
        assert status["totals"]["total_requests"] == 1
        assert status["totals"]["total_tokens"] == 1000
        assert status["cost"]["total_usd"] == 0.15
        assert status["requests"]["this_minute"] == 1
        assert status["tokens"]["this_minute"] == 1000

    def test_quota_manager_reset(self):
        """Quota manager can be manually reset"""
        quota = OperationalQuota()
        quota.record_request(tokens_used=1000, cost_usd=0.15, operation="test")

        status_before = quota.get_status()
        assert status_before["totals"]["total_requests"] == 1

        # Reset
        quota.reset()

        status_after = quota.get_status()
        assert status_after["totals"]["total_requests"] == 0
        assert status_after["totals"]["total_tokens"] == 0

    def test_quota_manager_cost_estimation(self):
        """Cost estimation is conservative and accurate"""
        quota = OperationalQuota()

        # 10,000 tokens should estimate to roughly:
        # 5,000 input tokens * $3/million = $0.015
        # 5,000 output tokens * $15/million = $0.075
        # Total: ~$0.09
        estimated = quota._estimate_cost(10000)
        assert 0.08 < estimated < 0.10


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestSafetyLayerIntegration:
    """Integration tests between Circuit Breaker, Quota Manager, and LLMClient"""

    def test_llm_client_quota_check_before_request(self):
        """LLMClient checks quotas before making API calls"""
        # Import after sys.path is set
        import importlib

        llm_module = importlib.import_module("runtime.llm_client")
        LLMClient = llm_module.LLMClient

        client = LLMClient()
        # Set low quota to trigger failure
        client.quota_manager.limits.tokens_per_minute = 100

        # Try to make request that exceeds quota
        with pytest.raises(QuotaExceededError):
            client.invoke(prompt="test", max_tokens=200)

    def test_llm_client_circuit_breaker_protection(self):
        """LLMClient circuit breaker protects against cascading failures"""
        # Import after sys.path is set
        import importlib

        llm_module = importlib.import_module("runtime.llm_client")
        LLMClient = llm_module.LLMClient
        LLMInvocationError = llm_module.LLMInvocationError

        # Create mock provider that raises errors
        mock_provider = MagicMock()
        mock_provider.invoke.side_effect = Exception("Provider Error")
        mock_provider.get_provider_name.return_value = "MockProvider"

        client = LLMClient(provider=mock_provider)
        client.circuit_breaker.config.failure_threshold = 2

        # Trigger 2 failures
        for _ in range(2):
            try:
                client.invoke(prompt="test")
            except Exception:
                pass

        # Circuit should now be OPEN, next request should fail with CircuitBreakerOpenError
        with pytest.raises(LLMInvocationError):
            client.invoke(prompt="test")

    def test_llm_client_records_quota_metrics(self):
        """LLMClient records quota metrics after successful requests"""
        # Import after sys.path is set
        import importlib

        llm_module = importlib.import_module("runtime.llm_client")
        LLMClient = llm_module.LLMClient
        LLMUsage = llm_module.LLMUsage
        LLMResponse = llm_module.LLMResponse

        from datetime import datetime

        # Create mock provider response
        mock_usage = LLMUsage(
            input_tokens=100,
            output_tokens=50,
            model="claude-3-5-sonnet-20241022",
            cost_usd=0.001,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        mock_response = LLMResponse(
            content="Response",
            usage=mock_usage,
            model="claude-3-5-sonnet-20241022",
            finish_reason="end_turn",
        )

        mock_provider = MagicMock()
        mock_provider.invoke.return_value = mock_response
        mock_provider.get_provider_name.return_value = "MockProvider"

        client = LLMClient(provider=mock_provider)
        client.invoke(prompt="test")

        # Verify metrics were recorded
        status = client.quota_manager.get_status()
        assert status["totals"]["total_requests"] == 1
        assert status["totals"]["total_tokens"] == 150

    def test_circuit_breaker_and_quota_manager_together(self):
        """Circuit breaker and quota manager work together"""
        breaker = CircuitBreaker(config=CircuitBreakerConfig(failure_threshold=2))
        quota = OperationalQuota(limits=QuotaLimits(requests_per_minute=5))

        # Both should start healthy
        assert breaker.state == CircuitBreakerState.CLOSED
        assert quota.get_status()["requests"]["this_minute"] == 0

        # Make 5 successful requests
        mock_func = Mock(return_value="success")
        for i in range(5):
            breaker.call(mock_func)
            quota.record_request(tokens_used=100, cost_usd=0.01, operation=f"req{i}")

        assert breaker.metrics.successful_requests == 5
        assert quota.get_status()["totals"]["total_requests"] == 5

        # 6th request should fail quota check
        quota.reset()
        quota.limits.requests_per_minute = 5
        for i in range(5):
            quota.record_request(tokens_used=100, cost_usd=0.01, operation=f"req{i}")

        with pytest.raises(QuotaExceededError):
            quota.check_before_request(estimated_tokens=100, operation="req6")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
