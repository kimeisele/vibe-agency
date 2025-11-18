"""
AGENCY OS ORCHESTRATOR
======================
Hybrid orchestrator for SDLC state machine execution.

Architecture:
- orchestrator.py (this file): State machine logic, routing, artifact management
- ORCHESTRATOR_PROMPT.md: AI personality, human communication, error handling

This implements GAD-001 architectural decision:
- Python handles state machine logic (testable, maintainable)
- Prompts handle AI behavior (flexible, human-friendly)
- Agents remain as prompts (not code)

Version: 2.0 (Phase 2 Implementation)
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

# =============================================================================
# DATA STRUCTURES
# =============================================================================


class ProjectPhase(Enum):
    """SDLC lifecycle phases"""

    PLANNING = "PLANNING"
    CODING = "CODING"
    TESTING = "TESTING"
    AWAITING_QA_APPROVAL = "AWAITING_QA_APPROVAL"
    DEPLOYMENT = "DEPLOYMENT"
    PRODUCTION = "PRODUCTION"
    MAINTENANCE = "MAINTENANCE"


class PlanningSubState(Enum):
    """Planning phase sub-states"""

    RESEARCH = "RESEARCH"
    BUSINESS_VALIDATION = "BUSINESS_VALIDATION"
    FEATURE_SPECIFICATION = "FEATURE_SPECIFICATION"


@dataclass
class ProjectManifest:
    """Project manifest (Single Source of Truth)"""

    project_id: str
    name: str
    current_phase: ProjectPhase
    current_sub_state: PlanningSubState | None = None
    artifacts: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowState:
    """State definition from YAML"""

    name: str
    description: str
    responsible_agents: list[str]
    input_artifact: str | None = None
    output_artifact: str | None = None
    optional: bool = False
    input_artifact_optional: bool = False
    state_machine_ref: str | None = None


@dataclass
class ResearchBrief:
    """Output from RESEARCH phase"""

    market_analysis: dict[str, Any]
    tech_analysis: dict[str, Any]
    fact_validation: dict[str, Any]
    user_insights: dict[str, Any] | None = None
    handoff_to_lean_canvas: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# EXCEPTIONS
# =============================================================================


class QualityGateFailure(Exception):
    """Raised when a quality gate blocks progression"""

    pass


class ArtifactNotFoundError(Exception):
    """Raised when required artifact is missing"""

    pass


class StateTransitionError(Exception):
    """Raised when state transition is invalid"""

    pass


# =============================================================================
# ORCHESTRATOR
# =============================================================================


class Orchestrator:
    """
    Master orchestrator for AGENCY OS SDLC workflows.

    Responsibilities:
    - Load and execute state machine from YAML
    - Invoke specialist agents (via prompts)
    - Manage artifacts and state transitions
    - Enforce quality gates
    - Handle optional phases (like RESEARCH)
    """

    def __init__(
        self,
        repo_root: Path,
        workflow_yaml: str = "agency_os/00_system/state_machine/ORCHESTRATION_workflow_design.yaml",
    ):
        """
        Initialize orchestrator.

        Args:
            repo_root: Root directory of vibe-agency repo
            workflow_yaml: Path to workflow design YAML (relative to repo_root)
        """
        self.repo_root = Path(repo_root)
        self.workflow_yaml_path = self.repo_root / workflow_yaml

        # Load workflow design
        self.workflow = self._load_workflow()

        # Paths
        self.agents_dir = self.repo_root / "agency_os" / "01_planning_framework" / "agents"
        self.workspaces_dir = self.repo_root / "workspaces"

    # -------------------------------------------------------------------------
    # WORKFLOW LOADING
    # -------------------------------------------------------------------------

    def _load_workflow(self) -> dict[str, Any]:
        """Load workflow design from YAML"""
        if not self.workflow_yaml_path.exists():
            raise FileNotFoundError(f"Workflow YAML not found: {self.workflow_yaml_path}")

        with open(self.workflow_yaml_path) as f:
            return yaml.safe_load(f)

    def get_planning_substates(self) -> list[WorkflowState]:
        """Get PLANNING sub-states from workflow"""
        for state in self.workflow.get("states", []):
            if state["name"] == "PLANNING":
                sub_states = state.get("sub_states", [])
                return [self._parse_substate(s) for s in sub_states]
        return []

    def _parse_substate(self, state_dict: dict[str, Any]) -> WorkflowState:
        """Parse sub-state dictionary into WorkflowState object"""
        return WorkflowState(
            name=state_dict["name"],
            description=state_dict.get("description", ""),
            responsible_agents=state_dict.get(
                "responsible_agents", [state_dict.get("responsible_agent")]
            ),
            input_artifact=state_dict.get("input_artifact"),
            output_artifact=state_dict.get("output_artifact"),
            optional=state_dict.get("optional", False),
            input_artifact_optional=state_dict.get("input_artifact_optional", False),
            state_machine_ref=state_dict.get("state_machine_ref"),
        )

    # -------------------------------------------------------------------------
    # PROJECT MANIFEST MANAGEMENT
    # -------------------------------------------------------------------------

    def load_project_manifest(self, project_id: str) -> ProjectManifest:
        """Load project manifest from workspace"""
        manifest_path = self._get_manifest_path(project_id)

        if not manifest_path.exists():
            raise FileNotFoundError(f"Project manifest not found: {manifest_path}")

        with open(manifest_path) as f:
            data = json.load(f)

        # Parse planning sub-state (if exists and not null)
        planning_sub_state = None
        if data["status"].get("planningSubState"):
            planning_sub_state = PlanningSubState(data["status"]["planningSubState"])

        return ProjectManifest(
            project_id=data["metadata"]["projectId"],
            name=data["metadata"]["name"],
            current_phase=ProjectPhase(data["status"]["projectPhase"]),
            current_sub_state=planning_sub_state,
            artifacts=data.get("artifacts", {}),
            metadata=data,
        )

    def save_project_manifest(self, manifest: ProjectManifest) -> None:
        """Save project manifest to workspace"""
        manifest_path = self._get_manifest_path(manifest.project_id)

        # Update manifest data
        manifest.metadata["status"]["projectPhase"] = manifest.current_phase.value
        if manifest.current_sub_state:
            manifest.metadata["status"]["planningSubState"] = manifest.current_sub_state.value
        manifest.metadata["artifacts"] = manifest.artifacts

        # Write to disk
        with open(manifest_path, "w") as f:
            json.dump(manifest.metadata, f, indent=2)

    def _get_manifest_path(self, project_id: str) -> Path:
        """Get path to project manifest"""
        # Find project directory by project_id
        for workspace_dir in self.workspaces_dir.iterdir():
            if workspace_dir.is_dir():
                manifest_path = workspace_dir / "project_manifest.json"
                if manifest_path.exists():
                    with open(manifest_path) as f:
                        data = json.load(f)
                        if data["metadata"]["projectId"] == project_id:
                            return manifest_path

        raise FileNotFoundError(f"Project {project_id} not found in workspaces")

    # -------------------------------------------------------------------------
    # ARTIFACT MANAGEMENT
    # -------------------------------------------------------------------------

    def load_artifact(self, project_id: str, artifact_name: str) -> dict[str, Any] | None:
        """Load artifact from project workspace"""
        # Determine artifact path based on type
        artifact_paths = {
            "research_brief.json": "artifacts/planning/research_brief.json",
            "lean_canvas_summary.json": "artifacts/planning/lean_canvas_summary.json",
            "feature_spec.json": "artifacts/planning/feature_spec.json",
        }

        if artifact_name not in artifact_paths:
            raise ValueError(f"Unknown artifact: {artifact_name}")

        # Find project directory
        project_dir = self._get_manifest_path(project_id).parent
        artifact_path = project_dir / artifact_paths[artifact_name]

        if not artifact_path.exists():
            return None

        with open(artifact_path) as f:
            return json.load(f)

    def save_artifact(self, project_id: str, artifact_name: str, data: dict[str, Any]) -> None:
        """Save artifact to project workspace"""
        artifact_paths = {
            "research_brief.json": "artifacts/planning/research_brief.json",
            "lean_canvas_summary.json": "artifacts/planning/lean_canvas_summary.json",
            "feature_spec.json": "artifacts/planning/feature_spec.json",
        }

        if artifact_name not in artifact_paths:
            raise ValueError(f"Unknown artifact: {artifact_name}")

        # Find project directory
        project_dir = self._get_manifest_path(project_id).parent
        artifact_path = project_dir / artifact_paths[artifact_name]

        # Ensure directory exists
        artifact_path.parent.mkdir(parents=True, exist_ok=True)

        # Write artifact
        with open(artifact_path, "w") as f:
            json.dump(data, f, indent=2)

    # -------------------------------------------------------------------------
    # PLANNING PHASE HANDLER
    # -------------------------------------------------------------------------

    def handle_planning_phase(self, project_id: str) -> None:
        """
        Execute PLANNING phase with all sub-states.

        Flow:
        1. [OPTIONAL] RESEARCH → research_brief.json
        2. BUSINESS_VALIDATION (uses research_brief if exists) → lean_canvas_summary.json
        3. FEATURE_SPECIFICATION → feature_spec.json
        """
        manifest = self.load_project_manifest(project_id)

        # Verify we're in PLANNING phase
        if manifest.current_phase != ProjectPhase.PLANNING:
            raise StateTransitionError(
                f"Cannot run planning phase. Current phase: {manifest.current_phase}"
            )

        # Get planning sub-states
        substates = self.get_planning_substates()

        # Execute each sub-state
        for substate in substates:
            if substate.optional and not self._should_execute_optional_state(substate):
                print(f"⏭️  Skipping optional state: {substate.name}")
                continue

            print(f"▶️  Executing state: {substate.name}")

            if substate.name == "RESEARCH":
                self._execute_research_state(manifest)
            elif substate.name == "BUSINESS_VALIDATION":
                self._execute_business_validation_state(manifest)
            elif substate.name == "FEATURE_SPECIFICATION":
                self._execute_feature_specification_state(manifest)

        # Transition to CODING
        manifest.current_phase = ProjectPhase.CODING
        manifest.current_sub_state = None
        self.save_project_manifest(manifest)

        print("✅ PLANNING phase complete. Transitioning to CODING")

    def _should_execute_optional_state(self, state: WorkflowState) -> bool:
        """
        Ask user if they want to execute optional state.

        TODO: This should eventually call ORCHESTRATOR_PROMPT.md for AI-driven conversation
        For Phase 2, we use simple CLI prompt
        """
        if state.name == "RESEARCH":
            print("\n" + "=" * 60)
            print("OPTIONAL: Research Phase")
            print("=" * 60)
            print("The Research phase provides fact-based market, technical, and user validation.")
            print(
                "It includes: Competitor analysis, API evaluation, citation enforcement, personas."
            )
            print("Estimated time: 1-2 hours")
            print()
            response = input("Do you want to run the Research phase? (y/n): ").strip().lower()
            return response in ["y", "yes"]

        return False

    # -------------------------------------------------------------------------
    # RESEARCH STATE EXECUTION
    # -------------------------------------------------------------------------

    def _execute_research_state(self, manifest: ProjectManifest) -> None:
        """
        Execute RESEARCH sub-state.

        Flow:
        1. MARKET_RESEARCHER → market_analysis
        2. TECH_RESEARCHER → tech_analysis
        3. FACT_VALIDATOR → fact_validation (BLOCKING)
        4. [OPTIONAL] USER_RESEARCHER → user_insights
        5. Compile → research_brief.json
        """
        print("\n🔬 Starting RESEARCH phase...")

        # Execute agents in sequence
        market_analysis = self._execute_agent_placeholder("MARKET_RESEARCHER", {})
        tech_analysis = self._execute_agent_placeholder("TECH_RESEARCHER", {})

        # FACT_VALIDATOR (blocking)
        fact_validation = self._execute_agent_placeholder(
            "FACT_VALIDATOR", {"market_analysis": market_analysis, "tech_analysis": tech_analysis}
        )

        # Check quality gate
        if fact_validation.get("quality_score", 0) < 50:
            raise QualityGateFailure(
                f"FACT_VALIDATOR blocked research. Quality score: {fact_validation.get('quality_score')}"
            )

        # USER_RESEARCHER (optional)
        user_insights = None
        if self._ask_user_researcher():
            user_insights = self._execute_agent_placeholder("USER_RESEARCHER", {})

        # Compile research brief
        research_brief = {
            "market_analysis": market_analysis,
            "tech_analysis": tech_analysis,
            "fact_validation": fact_validation,
            "user_insights": user_insights,
            "handoff_to_lean_canvas": {"status": "READY", "timestamp": self._get_timestamp()},
        }

        # Save artifact
        self.save_artifact(manifest.project_id, "research_brief.json", research_brief)
        manifest.artifacts["research_brief"] = research_brief

        print("✅ RESEARCH phase complete → research_brief.json")

    def _load_research_workflow(self) -> dict[str, Any]:
        """Load RESEARCH_workflow_design.yaml"""
        research_yaml = (
            self.repo_root
            / "agency_os"
            / "01_planning_framework"
            / "state_machine"
            / "RESEARCH_workflow_design.yaml"
        )

        if not research_yaml.exists():
            raise FileNotFoundError(f"Research workflow not found: {research_yaml}")

        with open(research_yaml) as f:
            return yaml.safe_load(f)

    def _ask_user_researcher(self) -> bool:
        """Ask if user wants USER_RESEARCHER (optional within RESEARCH)"""
        print("\n📋 USER_RESEARCHER is optional (generates personas, interview scripts)")
        response = input("Include USER_RESEARCHER? (y/n): ").strip().lower()
        return response in ["y", "yes"]

    # -------------------------------------------------------------------------
    # BUSINESS VALIDATION STATE
    # -------------------------------------------------------------------------

    def _execute_business_validation_state(self, manifest: ProjectManifest) -> None:
        """
        Execute BUSINESS_VALIDATION sub-state.

        Flow:
        1. Load optional research_brief.json (if exists)
        2. Execute LEAN_CANVAS_VALIDATOR (uses research if available)
        3. Save lean_canvas_summary.json
        """
        print("\n💼 Starting BUSINESS_VALIDATION phase...")

        # Load research brief if exists
        research_brief = self.load_artifact(manifest.project_id, "research_brief.json")

        # Execute LEAN_CANVAS_VALIDATOR
        lean_canvas = self._execute_agent_placeholder(
            "LEAN_CANVAS_VALIDATOR", {"research_brief": research_brief}
        )

        # Save artifact
        self.save_artifact(manifest.project_id, "lean_canvas_summary.json", lean_canvas)
        manifest.artifacts["lean_canvas_summary"] = lean_canvas

        print("✅ BUSINESS_VALIDATION complete → lean_canvas_summary.json")

    # -------------------------------------------------------------------------
    # FEATURE SPECIFICATION STATE
    # -------------------------------------------------------------------------

    def _execute_feature_specification_state(self, manifest: ProjectManifest) -> None:
        """
        Execute FEATURE_SPECIFICATION sub-state.

        Flow:
        1. Load lean_canvas_summary.json
        2. Execute VIBE_ALIGNER
        3. Save feature_spec.json
        """
        print("\n⚙️  Starting FEATURE_SPECIFICATION phase...")

        # Load lean canvas
        lean_canvas = self.load_artifact(manifest.project_id, "lean_canvas_summary.json")
        if not lean_canvas:
            raise ArtifactNotFoundError("lean_canvas_summary.json not found")

        # Execute VIBE_ALIGNER
        feature_spec = self._execute_agent_placeholder(
            "VIBE_ALIGNER", {"lean_canvas_summary": lean_canvas}
        )

        # Save artifact
        self.save_artifact(manifest.project_id, "feature_spec.json", feature_spec)
        manifest.artifacts["feature_spec"] = feature_spec

        print("✅ FEATURE_SPECIFICATION complete → feature_spec.json")

    # -------------------------------------------------------------------------
    # AGENT EXECUTION (PLACEHOLDER FOR PHASE 2)
    # -------------------------------------------------------------------------

    def _execute_agent_placeholder(self, agent_name: str, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        PLACEHOLDER: Execute agent by loading prompt and calling LLM.

        For Phase 2, this returns mock data.
        Phase 3 will implement actual LLM invocation via Anthropic API.

        Args:
            agent_name: Name of agent to execute
            inputs: Input artifacts for agent

        Returns:
            Agent output (parsed JSON)
        """
        print(f"   🤖 Executing {agent_name}... (mock)")

        # Mock outputs for testing
        if agent_name == "MARKET_RESEARCHER":
            return {
                "competitors": [{"name": "Competitor A", "source": "https://example.com"}],
                "pricing_insights": {"median": 50, "currency": "USD"},
                "market_size": "TAM: $1B",
            }
        elif agent_name == "TECH_RESEARCHER":
            return {
                "apis_evaluated": [{"name": "Stripe", "docs": "https://stripe.com/docs"}],
                "feasibility_score": "high",
            }
        elif agent_name == "FACT_VALIDATOR":
            # For testing: simulate low quality score to test blocking
            import os

            if os.environ.get("TEST_FACT_VALIDATOR_FAILURE"):
                return {
                    "quality_score": 42,
                    "verified_claims": 5,
                    "flagged_issues": [
                        "Missing source URL for Competitor A",
                        "Market size has no methodology",
                        "Pricing data is outdated",
                    ],
                }
            return {"quality_score": 85, "verified_claims": 10, "flagged_issues": []}
        elif agent_name == "USER_RESEARCHER":
            return {"personas": [{"name": "Early Adopter", "age": "25-35"}]}
        elif agent_name == "LEAN_CANVAS_VALIDATOR":
            return {
                "problem": "User problem",
                "solution": "MVP solution",
                "readiness": {"status": "READY"},
            }
        elif agent_name == "VIBE_ALIGNER":
            return {
                "features": ["Feature 1", "Feature 2"],
                "code_gen_spec": {"complexity": "medium"},
            }

        return {}

    # -------------------------------------------------------------------------
    # UTILITIES
    # -------------------------------------------------------------------------

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime

        return datetime.utcnow().isoformat() + "Z"


# =============================================================================
# CLI INTERFACE (FOR TESTING)
# =============================================================================


def main():
    """CLI interface for testing orchestrator"""
    import sys

    if len(sys.argv) < 3:
        print("Usage: python orchestrator.py <repo_root> <project_id>")
        sys.exit(1)

    repo_root = Path(sys.argv[1])
    project_id = sys.argv[2]

    # Initialize orchestrator
    orchestrator = Orchestrator(repo_root)

    # Execute planning phase
    try:
        orchestrator.handle_planning_phase(project_id)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
