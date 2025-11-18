"""
Runtime Components Package
===========================

GAD-002 Phase 3 Implementation

Contains runtime components for the orchestrator:
- llm_client.py: LLM client with graceful failover
- prompt_runtime.py: Prompt composition runtime
"""

from .llm_client import CostTracker, LLMClient, NoOpClient

__all__ = ["CostTracker", "LLMClient", "NoOpClient"]
