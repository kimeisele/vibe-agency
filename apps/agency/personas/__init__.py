"""
GAD-302: PERSONA FRAMEWORK

Specialized agent personas inheriting from BaseAgent.

Each persona specializes in a specific domain:
- Coder: Python/JavaScript development
- Researcher: Investigation and analysis
- Reviewer: Code quality and architecture
- Architect: System design and decisions
"""

from .architect import ArchitectAgent
from .coder import CoderAgent
from .researcher import ResearcherAgent
from .reviewer import ReviewerAgent

__all__ = [
    "ArchitectAgent",
    "CoderAgent",
    "ResearcherAgent",
    "ReviewerAgent",
]
