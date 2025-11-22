"""
ARCH-067: ChainProvider - Runtime Cascade Fallback

The ChainProvider implements the "Phoenix" resilience pattern at runtime.
Instead of failing when one provider fails, it cascades through a chain
of providers until one succeeds or all fail.

Architecture:
    Google Gemini (API) → StewardProvider (Claude Code) → SmartLocalProvider → Mock

Design Philosophy:
    - Provider failures are NOT errors, they're routing signals
    - The system never says "I don't know" - it finds another brain
    - Cascading is transparent to the caller
    - Each fallback is logged for debugging
"""

import logging
from typing import Optional

from vibe_core.llm.provider import LLMProvider

logger = logging.getLogger(__name__)


class ChainProvider(LLMProvider):
    """
    Resilient provider chain that cascades on failure.

    Implements the "Runtime Immortality" concept:
    When one cognitive path is blocked, the system automatically
    switches to the next available path without halting.

    Args:
        providers: List of LLMProvider instances in priority order
        fallback_to_mock: If True, add MockProvider as final fallback
    """

    def __init__(self, providers: list[LLMProvider], fallback_to_mock: bool = True):
        """Initialize the provider chain."""
        if not providers:
            raise ValueError("ChainProvider requires at least one provider")

        self.providers = list(providers)  # Copy to avoid external modifications
        self.fallback_to_mock = fallback_to_mock
        self.current_provider_index = 0
        self.provider_history = []  # Track which providers were tried

        logger.info(
            f"🔗 ChainProvider initialized with {len(self.providers)} provider(s)"
        )
        for i, p in enumerate(self.providers, 1):
            logger.info(f"   {i}. {self._provider_name(p)}")

    @staticmethod
    def _provider_name(provider: LLMProvider) -> str:
        """Get human-readable provider name."""
        provider_type = type(provider).__name__
        metadata = getattr(provider, "get_metadata", lambda: {})()
        if isinstance(metadata, dict) and "name" in metadata:
            return f"{provider_type} ({metadata['name']})"
        return provider_type

    def chat(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Send messages through the provider chain.

        Tries each provider in sequence until one succeeds.
        On failure, moves to the next provider in the chain.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Optional model identifier
            **kwargs: Additional provider-specific parameters

        Returns:
            str: The LLM response (from first successful provider)

        Raises:
            RuntimeError: If ALL providers fail
        """
        self.provider_history = []
        last_error = None

        for i, provider in enumerate(self.providers):
            provider_name = self._provider_name(provider)
            try:
                logger.debug(f"🔗 ChainProvider: Attempting provider {i + 1}/{len(self.providers)}: {provider_name}")
                response = provider.chat(messages, model=model, **kwargs)

                # Success! Log and return
                if i > 0:
                    logger.info(
                        f"🔗 ChainProvider: Primary provider(s) failed, but {provider_name} succeeded"
                    )
                else:
                    logger.debug(f"🔗 ChainProvider: {provider_name} responded successfully")

                self.current_provider_index = i
                self.provider_history.append((provider_name, "SUCCESS"))
                return response

            except Exception as e:
                error_type = type(e).__name__
                error_msg = str(e)[:100]  # First 100 chars for logging
                self.provider_history.append((provider_name, f"FAILED: {error_type}"))

                last_error = e
                logger.warning(
                    f"🔗 ChainProvider: {provider_name} failed ({error_type}). "
                    f"Cascading to next provider..."
                )

                if i < len(self.providers) - 1:
                    next_provider = self._provider_name(self.providers[i + 1])
                    logger.info(f"   → Fallback to: {next_provider}")
                continue

        # All providers failed
        provider_list = " → ".join([p[0] for p in self.provider_history])
        error_summary = " | ".join([p[1] for p in self.provider_history])

        logger.error(
            f"🔗 ChainProvider: ALL PROVIDERS FAILED"
            f"\n   Chain: {provider_list}"
            f"\n   Errors: {error_summary}"
        )

        raise RuntimeError(
            f"ChainProvider cascade exhausted. Last error: {type(last_error).__name__}: {last_error}"
        )

    @property
    def system_prompt(self) -> str:
        """Return system prompt from primary provider."""
        if not self.providers:
            return ""
        return self.providers[0].system_prompt

    def get_metadata(self) -> dict[str, str]:
        """Return metadata showing the chain configuration."""
        return {
            "type": "ChainProvider",
            "provider_count": str(len(self.providers)),
            "providers": ", ".join(self._provider_name(p) for p in self.providers),
            "current": self._provider_name(self.providers[self.current_provider_index]),
        }

    def __repr__(self) -> str:
        """String representation showing the cascade."""
        chain = " → ".join(self._provider_name(p) for p in self.providers)
        return f"ChainProvider({chain})"
