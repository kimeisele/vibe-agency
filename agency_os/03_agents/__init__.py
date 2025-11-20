"""
GAD-3: AGENT FRAMEWORK

The active agents (Legs) that utilize the infrastructure (Body, Brain, Arms).

Classes:
  - BaseAgent: The integration hub connecting Runtime, Knowledge, and Mission Control (Legacy)
  - BaseSpecialist: Abstract base class for HAP (Hierarchical Agent Pattern) - ARCH-005
"""

from .base_agent import BaseAgent, ExecutionResult, KnowledgeResult
from .base_specialist import BaseSpecialist, MissionContext, SpecialistResult

__all__ = [
    "BaseAgent",
    "BaseSpecialist",
    "ExecutionResult",
    "KnowledgeResult",
    "MissionContext",
    "SpecialistResult",
]
