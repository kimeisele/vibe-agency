"""
GAD-3: AGENT FRAMEWORK

The active agents (Legs) that utilize the infrastructure (Body, Brain, Arms).

Classes:
  - BaseAgent: The integration hub connecting Runtime, Knowledge, and Mission Control (Legacy)
  - BaseSpecialist: Abstract base class for HAP (Hierarchical Agent Pattern) - ARCH-005
  - PlanningSpecialist: PLANNING phase specialist - ARCH-006
"""

from .base_agent import BaseAgent, ExecutionResult, KnowledgeResult
from .base_specialist import BaseSpecialist, MissionContext, SpecialistResult
from .planning_specialist import PlanningSpecialist
from .registry import AgentRegistry

__all__ = [
    "AgentRegistry",
    "BaseAgent",
    "BaseSpecialist",
    "ExecutionResult",
    "KnowledgeResult",
    "MissionContext",
    "PlanningSpecialist",
    "SpecialistResult",
]
