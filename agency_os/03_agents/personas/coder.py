#!/usr/bin/env python3
"""
Coder Persona (GAD-302)

Specialized agent for Python/JavaScript development.

Responsibilities:
- Write clean, maintainable code
- Understand syntax and patterns
- Create functions and modules
- Optimize and refactor code
- Write tests

This agent consults patterns/snippets knowledge domains by default.
"""

import importlib.util
from typing import Optional
from pathlib import Path

# Dynamic import for BaseAgent (handles numeric directory names)
# Path: agency_os/03_agents/personas/coder.py
# Need to go up 4 levels to get to vibe-agency root
vibe_root = Path(__file__).parent.parent.parent.parent
spec = importlib.util.spec_from_file_location(
    "base_agent",
    vibe_root / "agency_os" / "03_agents" / "base_agent.py"
)
base_agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base_agent_module)

BaseAgent = base_agent_module.BaseAgent
KnowledgeResult = base_agent_module.KnowledgeResult


class CoderAgent(BaseAgent):
    """
    Coder: The development specialist.

    Expertise in Python, JavaScript, and software development patterns.
    """

    def __init__(
        self,
        name: str = "claude-coder",
        role: str = "Code Developer",
        vibe_root: Optional[Path] = None
    ):
        """
        Initialize Coder agent.

        Args:
            name: Agent instance name (default: "claude-coder")
            role: Agent role (default: "Code Developer")
            vibe_root: Path to vibe-agency root
        """
        super().__init__(name=name, role=role, vibe_root=vibe_root)

    def consult_knowledge(
        self,
        query: str,
        domain: str = "patterns",
        limit: int = 5
    ) -> KnowledgeResult:
        """
        Consult knowledge with default domain biased toward code patterns.

        Args:
            query: Search query (e.g., "python context manager")
            domain: Knowledge domain (default: "patterns" for code snippets)
            limit: Maximum results

        Returns:
            KnowledgeResult with code patterns and best practices
        """
        return super().consult_knowledge(query=query, domain=domain, limit=limit)

    def get_context_with_role(self) -> dict:
        """
        Get context enriched with Coder-specific information.

        Returns:
            Context dict with agent role and capabilities
        """
        context = self.get_context()
        context.update({
            "persona": "Coder",
            "capabilities": [
                "Write Python code",
                "Write JavaScript code",
                "Refactor existing code",
                "Create unit tests",
                "Optimize performance",
                "Follow design patterns",
            ],
            "knowledge_domains": ["patterns", "snippets"],
            "preferred_languages": ["python", "javascript", "typescript"],
        })
        return context

    def __repr__(self) -> str:
        return f"CoderAgent(name={self.name!r}, role={self.role!r})"
