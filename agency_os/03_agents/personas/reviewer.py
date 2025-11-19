#!/usr/bin/env python3
"""
Reviewer Persona (GAD-302)

Specialized agent for code quality and architecture review.

Responsibilities:
- Analyze code quality
- Check architectural soundness
- Verify against best practices
- Suggest improvements
- Validate test coverage

This agent consults patterns/decisions knowledge domains by default.
"""

import importlib.util
from pathlib import Path

# Dynamic import for BaseAgent (handles numeric directory names)
# Path: agency_os/03_agents/personas/reviewer.py
# Need to go up 4 levels to get to vibe-agency root
vibe_root = Path(__file__).parent.parent.parent.parent
spec = importlib.util.spec_from_file_location(
    "base_agent", vibe_root / "agency_os" / "03_agents" / "base_agent.py"
)
base_agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base_agent_module)

BaseAgent = base_agent_module.BaseAgent
KnowledgeResult = base_agent_module.KnowledgeResult


class ReviewerAgent(BaseAgent):
    """
    Reviewer: The quality assurance specialist.

    Expertise in code quality, architecture, and best practices.
    """

    def __init__(
        self,
        name: str = "claude-reviewer",
        role: str = "Code Reviewer",
        vibe_root: Path | None = None,
    ):
        """
        Initialize Reviewer agent.

        Args:
            name: Agent instance name (default: "claude-reviewer")
            role: Agent role (default: "Code Reviewer")
            vibe_root: Path to vibe-agency root
        """
        super().__init__(name=name, role=role, vibe_root=vibe_root)
        # Explicit capability declaration (GAD-904)
        self.capabilities = [
            "audit",
            "security",
            "qa",
            "code_analysis",
            "testing",
            "pattern_knowledge",
        ]

    def consult_knowledge(
        self, query: str, domain: str = "patterns", limit: int = 5
    ) -> KnowledgeResult:
        """
        Consult knowledge for review standards and best practices.

        Args:
            query: Search query (e.g., "error handling patterns")
            domain: Knowledge domain (default: "patterns" for best practices)
            limit: Maximum results

        Returns:
            KnowledgeResult with quality standards and patterns
        """
        return super().consult_knowledge(query=query, domain=domain, limit=limit)

    def review_code(self, code_path: str, focus_areas: list[str] | None = None) -> dict:
        """
        Review code for quality and architectural soundness.

        Args:
            code_path: Path to code file to review
            focus_areas: Specific areas to focus on (e.g., ["error handling", "performance"])

        Returns:
            Dict with review findings
        """
        if focus_areas is None:
            focus_areas = [
                "code quality",
                "error handling",
                "performance",
                "maintainability",
            ]

        findings = {
            "file": code_path,
            "focus_areas": focus_areas,
            "review_checklist": {
                "error_handling": "Check for proper error handling",
                "test_coverage": "Verify test coverage",
                "documentation": "Check for adequate documentation",
                "performance": "Identify performance bottlenecks",
                "maintainability": "Assess code maintainability",
                "security": "Check for security issues",
                "dependencies": "Verify dependency management",
            },
        }

        return findings

    def compare_architectures(self, architecture_a: str, architecture_b: str) -> dict:
        """
        Compare two architectural approaches.

        Args:
            architecture_a: First architecture description
            architecture_b: Second architecture description

        Returns:
            Dict with comparison analysis
        """
        return {
            "comparison": "architectural evaluation",
            "approach_a": architecture_a,
            "approach_b": architecture_b,
            "evaluation_criteria": [
                "scalability",
                "maintainability",
                "complexity",
                "resilience",
                "testability",
                "deployment ease",
            ],
        }

    def get_context_with_role(self) -> dict:
        """
        Get context enriched with Reviewer-specific information.

        Returns:
            Context dict with agent role and capabilities
        """
        context = self.get_context()
        context.update(
            {
                "persona": "Reviewer",
                "capabilities": [
                    "Code quality analysis",
                    "Architectural review",
                    "Best practices checking",
                    "Performance assessment",
                    "Security review",
                    "Test coverage analysis",
                ],
                "knowledge_domains": ["patterns", "decisions"],
                "review_criteria": [
                    "code quality",
                    "error handling",
                    "test coverage",
                    "documentation",
                    "performance",
                    "security",
                ],
            }
        )
        return context

    def __repr__(self) -> str:
        return f"ReviewerAgent(name={self.name!r}, role={self.role!r})"
