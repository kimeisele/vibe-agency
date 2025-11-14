#!/usr/bin/env python3
"""
LLM Client - Thin wrapper around LLM providers
================================================

Implements GAD-002 Decision 6: Agent Invocation Architecture

Features:
- Graceful failover (no crash if API key missing)
- Retry logic with exponential backoff
- Cost tracking (input/output tokens)
- Rate limiting support
- Error handling

Version: 1.0 (Phase 3 - GAD-002)
"""

import os
import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class LLMUsage:
    """Token usage and cost information"""
    input_tokens: int
    output_tokens: int
    model: str
    cost_usd: float
    timestamp: str


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    usage: LLMUsage
    model: str
    finish_reason: str


# =============================================================================
# COST TRACKER
# =============================================================================

class CostTracker:
    """
    Tracks API costs across invocations.

    Pricing (as of 2025-11-14):
    - Claude 3.5 Sonnet: $3/MTok input, $15/MTok output
    """

    # Pricing table (USD per million tokens)
    PRICING = {
        "claude-3-5-sonnet-20241022": {
            "input": 3.0,
            "output": 15.0
        },
        "claude-3-5-sonnet-20250129": {
            "input": 3.0,
            "output": 15.0
        }
    }

    def __init__(self):
        self.total_cost = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.invocations = []

    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate cost for a single invocation"""
        if model not in self.PRICING:
            logger.warning(f"Unknown model pricing: {model}, using Sonnet defaults")
            pricing = self.PRICING["claude-3-5-sonnet-20241022"]
        else:
            pricing = self.PRICING[model]

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def record(self, input_tokens: int, output_tokens: int, model: str) -> LLMUsage:
        """Record token usage and calculate cost"""
        cost = self.calculate_cost(input_tokens, output_tokens, model)

        usage = LLMUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            cost_usd=cost,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

        self.total_cost += cost
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.invocations.append(usage)

        return usage

    def get_summary(self) -> Dict[str, Any]:
        """Get cost summary"""
        return {
            "total_cost_usd": round(self.total_cost, 4),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_invocations": len(self.invocations),
            "average_cost_per_invocation": round(self.total_cost / len(self.invocations), 4) if self.invocations else 0
        }


# =============================================================================
# EXCEPTIONS
# =============================================================================

class LLMClientError(Exception):
    """Base exception for LLM client errors"""
    pass


class LLMInvocationError(LLMClientError):
    """Raised when LLM invocation fails after retries"""
    pass


class BudgetExceededError(LLMClientError):
    """Raised when budget limit is reached"""
    pass


# =============================================================================
# NO-OP CLIENT (GRACEFUL FAILOVER)
# =============================================================================

class NoOpClient:
    """
    Fallback client when API key is not available.

    Implements GAD-002 Decision 6 - Graceful Failover:
    - Returns empty responses instead of crashing
    - Allows system to run in knowledge-only mode
    - Logs warnings for visibility
    """

    def __init__(self):
        logger.warning("NoOpClient initialized - running in knowledge-only mode")

    def messages_create(self, **kwargs) -> Any:
        """Mock messages.create() that returns empty response"""
        logger.warning("NoOpClient: Skipping LLM call (no API key)")

        # Return mock response object
        class MockResponse:
            def __init__(self):
                self.content = [MockContent()]
                self.usage = MockUsage()
                self.model = kwargs.get("model", "noop")
                self.stop_reason = "no_api_key"

        class MockContent:
            def __init__(self):
                self.text = "{}"  # Empty JSON response

        class MockUsage:
            def __init__(self):
                self.input_tokens = 0
                self.output_tokens = 0

        return MockResponse()


# =============================================================================
# LLM CLIENT
# =============================================================================

class LLMClient:
    """
    Thin wrapper around Anthropic API with retry, cost tracking, error handling.

    Implements GAD-002 Decision 6: Agent Invocation Architecture

    Features:
    - Graceful failover (NoOpClient if no API key)
    - Retry with exponential backoff (up to 3 attempts)
    - Cost tracking via CostTracker
    - Budget enforcement (optional)
    - Rate limiting support (optional)

    Usage:
        client = LLMClient()
        response = client.invoke(
            prompt="What is 2+2?",
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024
        )
        print(response.content)
        print(f"Cost: ${response.usage.cost_usd:.4f}")
    """

    def __init__(self, budget_limit: Optional[float] = None):
        """
        Initialize LLM client.

        Args:
            budget_limit: Optional budget limit in USD (default: None = no limit)
        """
        self.cost_tracker = CostTracker()
        self.budget_limit = budget_limit

        # Initialize Anthropic client with graceful failover
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")

        if not self.api_key:
            logger.warning(
                "ANTHROPIC_API_KEY not found - using NoOpClient (knowledge-only mode). "
                "Set ANTHROPIC_API_KEY environment variable to enable LLM invocations."
            )
            self.client = NoOpClient()
            self.mode = "noop"
        else:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
                self.mode = "anthropic"
                logger.info("LLM Client initialized with Anthropic API")
            except ImportError:
                logger.error(
                    "anthropic package not installed. "
                    "Install with: pip install anthropic>=0.18.0"
                )
                self.client = NoOpClient()
                self.mode = "noop"

    def invoke(
        self,
        prompt: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
        temperature: float = 1.0,
        max_retries: int = 3
    ) -> LLMResponse:
        """
        Invoke LLM with retry logic and cost tracking.

        Args:
            prompt: Input prompt
            model: Model to use
            max_tokens: Maximum output tokens
            temperature: Sampling temperature
            max_retries: Maximum retry attempts (default: 3)

        Returns:
            LLMResponse with content and usage info

        Raises:
            BudgetExceededError: If budget limit reached
            LLMInvocationError: If all retries fail
        """
        # Check budget before invocation
        if self.budget_limit and self.cost_tracker.total_cost >= self.budget_limit:
            raise BudgetExceededError(
                f"Budget limit reached: ${self.budget_limit:.2f} "
                f"(current: ${self.cost_tracker.total_cost:.4f})"
            )

        # Retry loop with exponential backoff
        last_error = None
        for attempt in range(max_retries):
            try:
                # Call Anthropic API
                response = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}]
                )

                # Track cost
                usage = self.cost_tracker.record(
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    model=model
                )

                # Log invocation
                logger.info(
                    f"LLM invocation successful: {model} "
                    f"(in: {usage.input_tokens}, out: {usage.output_tokens}, "
                    f"cost: ${usage.cost_usd:.4f})"
                )

                # Return standardized response
                return LLMResponse(
                    content=response.content[0].text,
                    usage=usage,
                    model=response.model,
                    finish_reason=response.stop_reason
                )

            except Exception as e:
                last_error = e
                error_name = type(e).__name__

                # Check if retryable error
                retryable_errors = ["RateLimitError", "APIConnectionError", "APITimeoutError"]
                is_retryable = any(err in error_name for err in retryable_errors)

                if is_retryable and attempt < max_retries - 1:
                    # Exponential backoff: 2s, 4s, 8s
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"LLM invocation failed ({error_name}), "
                        f"retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)
                else:
                    # Non-retryable error or max retries reached
                    logger.error(f"LLM invocation failed: {error_name} - {str(e)}")
                    break

        # All retries failed
        raise LLMInvocationError(
            f"LLM invocation failed after {max_retries} attempts. "
            f"Last error: {type(last_error).__name__} - {str(last_error)}"
        )

    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost tracking summary"""
        summary = self.cost_tracker.get_summary()
        if self.budget_limit:
            summary['budget_limit_usd'] = self.budget_limit
            summary['budget_remaining_usd'] = round(self.budget_limit - self.cost_tracker.total_cost, 4)
            summary['budget_used_percent'] = round((self.cost_tracker.total_cost / self.budget_limit) * 100, 2)
        return summary


# =============================================================================
# CLI INTERFACE (FOR TESTING)
# =============================================================================

if __name__ == "__main__":
    import sys

    # Test LLM client
    print("Testing LLM Client...")
    print("=" * 60)

    # Initialize client
    client = LLMClient(budget_limit=1.0)  # $1 budget for testing

    print(f"Mode: {client.mode}")
    print(f"Budget: ${client.budget_limit}")
    print()

    # Test invocation
    if client.mode == "anthropic":
        try:
            response = client.invoke(
                prompt="What is 2+2? Answer in one sentence.",
                model="claude-3-5-sonnet-20241022",
                max_tokens=100
            )

            print("Response:")
            print(response.content)
            print()
            print("Usage:")
            print(f"  Input tokens: {response.usage.input_tokens}")
            print(f"  Output tokens: {response.usage.output_tokens}")
            print(f"  Cost: ${response.usage.cost_usd:.4f}")
            print()
            print("Cost Summary:")
            summary = client.get_cost_summary()
            for key, value in summary.items():
                print(f"  {key}: {value}")

        except Exception as e:
            print(f"Error: {e}")

    else:
        print("NoOp mode - skipping test invocation")
        print("Set ANTHROPIC_API_KEY to test real invocations")
