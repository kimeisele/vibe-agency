#!/usr/bin/env python3
"""
Researcher Persona (GAD-302)

Specialized agent for investigation and analysis.

Responsibilities:
- Search knowledge base thoroughly
- Synthesize information across sources
- Analyze patterns and trends
- Make evidence-based conclusions
- Document findings

This agent consults research knowledge domain by default.
"""

import importlib.util
from pathlib import Path

# Dynamic import for BaseAgent (handles numeric directory names)
# Path: agency_os/03_agents/personas/researcher.py
# Need to go up 4 levels to get to vibe-agency root
vibe_root = Path(__file__).parent.parent.parent.parent
spec = importlib.util.spec_from_file_location(
    "base_agent", vibe_root / "agency_os" / "03_agents" / "base_agent.py"
)
base_agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base_agent_module)

BaseAgent = base_agent_module.BaseAgent
KnowledgeResult = base_agent_module.KnowledgeResult


class ResearcherAgent(BaseAgent):
    """
    Researcher: The investigation specialist.

    Expertise in deep research, analysis, and synthesizing information.
    """

    def __init__(
        self,
        name: str = "claude-researcher",
        role: str = "Researcher",
        vibe_root: Path | None = None,
    ):
        """
        Initialize Researcher agent.

        Args:
            name: Agent instance name (default: "claude-researcher")
            role: Agent role (default: "Researcher")
            vibe_root: Path to vibe-agency root
        """
        super().__init__(name=name, role=role, vibe_root=vibe_root)
        # Explicit capability declaration (GAD-904)
        self.capabilities = [
            "research",
            "search",
            "synthesis",
            "reasoning",
            "documentation",
        ]

    def consult_knowledge(
        self, query: str, domain: str = "research", limit: int = 10
    ) -> KnowledgeResult:
        """
        Consult knowledge with default domain biased toward research.

        Args:
            query: Search query (e.g., "vector embeddings")
            domain: Knowledge domain (default: "research" for detailed articles)
            limit: Maximum results (default: 10 for comprehensive research)

        Returns:
            KnowledgeResult with research articles and findings
        """
        return super().consult_knowledge(query=query, domain=domain, limit=limit)

    def research_topic(self, topic: str) -> dict:
        """
        Conduct comprehensive research on a topic.

        Args:
            topic: Topic to research

        Returns:
            Dict with research summary and sources
        """
        # Consult knowledge with increased limit for thorough research
        result = self.consult_knowledge(topic, domain="research", limit=15)

        return {
            "topic": topic,
            "found": result.found,
            "sources_count": len(result.artifacts),
            "artifacts": result.artifacts,
            "relevance_scores": result.relevance_scores,
            "query_used": result.query,
        }

    def compare_approaches(self, topic: str, subtopic_a: str, subtopic_b: str) -> dict:
        """
        Compare two different approaches or solutions.

        Args:
            topic: Main topic
            subtopic_a: First approach
            subtopic_b: Second approach

        Returns:
            Dict comparing the two approaches
        """
        result_a = self.research_topic(f"{topic} {subtopic_a}")
        result_b = self.research_topic(f"{topic} {subtopic_b}")

        return {
            "topic": topic,
            "approach_a": subtopic_a,
            "approach_b": subtopic_b,
            "approach_a_sources": result_a["sources_count"],
            "approach_b_sources": result_b["sources_count"],
            "approach_a_artifacts": result_a["artifacts"],
            "approach_b_artifacts": result_b["artifacts"],
        }

    def get_context_with_role(self) -> dict:
        """
        Get context enriched with Researcher-specific information.

        Returns:
            Context dict with agent role and capabilities
        """
        context = self.get_context()
        context.update(
            {
                "persona": "Researcher",
                "capabilities": [
                    "Deep research on topics",
                    "Synthesize information",
                    "Compare approaches",
                    "Analyze patterns",
                    "Document findings",
                    "Evidence-based analysis",
                ],
                "knowledge_domains": ["research", "decisions"],
                "preferred_output": "comprehensive analysis with sources",
            }
        )
        return context

    def __repr__(self) -> str:
        return f"ResearcherAgent(name={self.name!r}, role={self.role!r})"
