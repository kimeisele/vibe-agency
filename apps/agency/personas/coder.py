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

from pathlib import Path

from vibe_core.specialists import BaseAgent, KnowledgeResult


class CoderAgent(BaseAgent):
    """
    Coder: The development specialist.

    Expertise in Python, JavaScript, and software development patterns.
    """

    def __init__(
        self,
        name: str = "claude-coder",
        role: str = "Code Developer",
        vibe_root: Path | None = None,
    ):
        """
        Initialize Coder agent.

        Args:
            name: Agent instance name (default: "claude-coder")
            role: Agent role (default: "Code Developer")
            vibe_root: Path to vibe-agency root
        """
        super().__init__(name=name, role=role, vibe_root=vibe_root)
        # Explicit capability declaration (GAD-904)
        self.capabilities = [
            "coding",
            "debugging",
            "python",
            "refactoring",
        ]

    def consult_knowledge(
        self, query: str, domain: str = "patterns", limit: int = 5
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
        context.update(
            {
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
            }
        )
        return context

    def __repr__(self) -> str:
        return f"CoderAgent(name={self.name!r}, role={self.role!r})"
