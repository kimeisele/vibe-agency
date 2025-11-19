#!/usr/bin/env python3
"""
Architect Persona (GAD-302)

Specialized agent for system design and architecture.

Responsibilities:
- Design systems
- Evaluate trade-offs
- Make design decisions
- Document architecture
- Plan for scalability and maintainability

This agent consults decisions/research knowledge domains by default.
"""

import importlib.util
from typing import Optional, List, Dict, Any
from pathlib import Path

# Dynamic import for BaseAgent (handles numeric directory names)
# Path: agency_os/03_agents/personas/architect.py
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


class ArchitectAgent(BaseAgent):
    """
    Architect: The system design specialist.

    Expertise in system design, architecture decisions, and long-term planning.
    """

    def __init__(
        self,
        name: str = "claude-architect",
        role: str = "System Architect",
        vibe_root: Optional[Path] = None
    ):
        """
        Initialize Architect agent.

        Args:
            name: Agent instance name (default: "claude-architect")
            role: Agent role (default: "System Architect")
            vibe_root: Path to vibe-agency root
        """
        super().__init__(name=name, role=role, vibe_root=vibe_root)

    def consult_knowledge(
        self,
        query: str,
        domain: str = "decisions",
        limit: int = 10
    ) -> KnowledgeResult:
        """
        Consult knowledge with default domain biased toward design decisions.

        Args:
            query: Search query (e.g., "event-driven architecture")
            domain: Knowledge domain (default: "decisions" for architectural choices)
            limit: Maximum results (default: 10 for comprehensive design context)

        Returns:
            KnowledgeResult with architectural patterns and decisions
        """
        return super().consult_knowledge(query=query, domain=domain, limit=limit)

    def design_system(
        self,
        system_name: str,
        requirements: List[str],
        constraints: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Design a system based on requirements and constraints.

        Args:
            system_name: Name of the system to design
            requirements: List of functional requirements
            constraints: List of constraints (performance, budget, etc.)

        Returns:
            Dict with system design proposal
        """
        if constraints is None:
            constraints = []

        return {
            "system": system_name,
            "requirements": requirements,
            "constraints": constraints,
            "design_phases": [
                "Analyze requirements",
                "Research architectural patterns",
                "Design core components",
                "Plan integration points",
                "Document decisions",
            ],
            "design_considerations": {
                "scalability": "System can grow with demand",
                "maintainability": "Easy to understand and modify",
                "resilience": "Handles failures gracefully",
                "performance": "Meets performance requirements",
                "security": "Protects sensitive data",
                "cost": "Optimizes resource usage",
            },
        }

    def evaluate_tradeoff(
        self,
        decision: str,
        option_a: str,
        option_b: str
    ) -> Dict[str, Any]:
        """
        Evaluate tradeoffs between two architectural options.

        Args:
            decision: Description of the decision
            option_a: First architectural option
            option_b: Second architectural option

        Returns:
            Dict with tradeoff analysis
        """
        # Research both options
        result_a = self.consult_knowledge(
            f"{decision} {option_a}",
            domain="decisions",
            limit=5
        )
        result_b = self.consult_knowledge(
            f"{decision} {option_b}",
            domain="decisions",
            limit=5
        )

        return {
            "decision": decision,
            "option_a": option_a,
            "option_b": option_b,
            "option_a_references": len(result_a.artifacts),
            "option_b_references": len(result_b.artifacts),
            "tradeoff_factors": [
                "Complexity",
                "Maintainability",
                "Performance",
                "Scalability",
                "Team familiarity",
                "Cost",
                "Implementation time",
            ],
            "option_a_artifacts": result_a.artifacts,
            "option_b_artifacts": result_b.artifacts,
        }

    def document_adr(
        self,
        title: str,
        status: str = "PROPOSED",
        context: Optional[str] = None,
        decision: Optional[str] = None,
        consequences: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Document an Architecture Decision Record (ADR).

        Args:
            title: ADR title
            status: ADR status (PROPOSED, ACCEPTED, SUPERSEDED, etc.)
            context: Problem statement
            decision: Decision made
            consequences: Consequences of the decision

        Returns:
            Dict with ADR structure
        """
        if consequences is None:
            consequences = []

        return {
            "title": title,
            "status": status,
            "context": context or "Context to be documented",
            "decision": decision or "Decision to be documented",
            "consequences": consequences,
            "adr_structure": {
                "status": "Proposed/Accepted/Superseded/Deprecated",
                "context": "Problem statement and background",
                "decision": "Solution chosen",
                "consequences": "Positive and negative impacts",
                "alternatives": "Other options considered",
                "related_decisions": "Links to other ADRs",
            },
        }

    def get_context_with_role(self) -> dict:
        """
        Get context enriched with Architect-specific information.

        Returns:
            Context dict with agent role and capabilities
        """
        context = self.get_context()
        context.update({
            "persona": "Architect",
            "capabilities": [
                "System design",
                "Architecture decision making",
                "Tradeoff analysis",
                "Scalability planning",
                "ADR documentation",
                "Technology evaluation",
            ],
            "knowledge_domains": ["decisions", "research"],
            "design_focus": [
                "scalability",
                "maintainability",
                "resilience",
                "performance",
                "security",
                "cost-effectiveness",
            ],
        })
        return context

    def __repr__(self) -> str:
        return f"ArchitectAgent(name={self.name!r}, role={self.role!r})"
