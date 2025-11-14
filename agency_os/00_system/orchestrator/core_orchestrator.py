#!/usr/bin/env python3
"""
CORE ORCHESTRATOR - SDLC State Machine Controller
==================================================

Implements GAD-002 Decision 1: Hierarchical Orchestrator Architecture

This is the master orchestrator that manages the complete SDLC workflow:
- PLANNING → CODING → TESTING → DEPLOYMENT → MAINTENANCE

Architecture:
- core_orchestrator.py (this file): State machine logic, routing, validation
- Phase handlers (planning_handler.py, etc.): Framework-specific execution logic
- llm_client.py: LLM invocation with retry, cost tracking
- prompt_runtime.py: Prompt composition from fragments

Version: 1.0 (Phase 3 - GAD-002)
"""

import json
import yaml
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# Add runtime to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "runtime"))

from llm_client import LLMClient, BudgetExceededError
from prompt_runtime import PromptRuntime

logger = logging.getLogger(__name__)


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
    current_sub_state: Optional[PlanningSubState] = None
    artifacts: Dict[str, Any] = field(default_factory=dict)
    budget: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowState:
    """State definition from YAML"""
    name: str
    description: str
    responsible_agents: List[str]
    input_artifact: Optional[str] = None
    output_artifact: Optional[str] = None
    optional: bool = False
    input_artifact_optional: bool = False
    state_machine_ref: Optional[str] = None


# =============================================================================
# EXCEPTIONS
# =============================================================================

class OrchestratorError(Exception):
    """Base exception for orchestrator errors"""
    pass


class QualityGateFailure(OrchestratorError):
    """Raised when a quality gate blocks progression"""
    pass


class ArtifactNotFoundError(OrchestratorError):
    """Raised when required artifact is missing"""
    pass


class StateTransitionError(OrchestratorError):
    """Raised when state transition is invalid"""
    pass


class SchemaValidationError(OrchestratorError):
    """Raised when artifact fails schema validation"""
    pass


# =============================================================================
# SCHEMA VALIDATOR (GAD-002 Decision 3)
# =============================================================================

class SchemaValidator:
    """
    Validates artifacts against schemas defined in ORCHESTRATION_data_contracts.yaml

    Implements GAD-002 Decision 3: Centralized Schema Validation
    """

    def __init__(self, contracts_yaml_path: Path):
        """Initialize validator with contracts YAML"""
        self.contracts_yaml_path = contracts_yaml_path

        if not contracts_yaml_path.exists():
            logger.warning(f"Contracts YAML not found: {contracts_yaml_path}")
            self.contracts = None
            return

        with open(contracts_yaml_path, 'r') as f:
            self.contracts = yaml.safe_load(f)

        logger.info(f"Schema validator initialized with {len(self.contracts.get('schemas', []))} schemas")

    def validate_artifact(self, artifact_name: str, data: Dict[str, Any]) -> None:
        """
        Validate artifact against schema.

        Args:
            artifact_name: Name of artifact (e.g., "feature_spec.json")
            data: Artifact data to validate

        Raises:
            SchemaValidationError: If validation fails
        """
        if not self.contracts:
            logger.warning(f"Skipping validation for {artifact_name} (no contracts loaded)")
            return

        # Find schema for this artifact
        schema_name = artifact_name.replace('.json', '.schema.json')
        schema_def = None

        for schema in self.contracts.get('schemas', []):
            if schema['name'] == schema_name:
                schema_def = schema
                break

        if not schema_def:
            logger.warning(f"No schema found for {artifact_name}, skipping validation")
            return

        # Basic validation (check required fields)
        # TODO: Full JSON Schema validation with jsonschema library
        errors = []

        for field_def in schema_def.get('fields', []):
            field_name = field_def['name']
            required = field_def.get('required', False)

            if required and field_name not in data:
                errors.append(f"Missing required field: {field_name}")

        if errors:
            raise SchemaValidationError(
                f"Validation failed for {artifact_name}:\n" + "\n".join(f"  - {e}" for e in errors)
            )

        logger.info(f"✓ Validation passed: {artifact_name}")


# =============================================================================
# CORE ORCHESTRATOR
# =============================================================================

class CoreOrchestrator:
    """
    Master orchestrator for SDLC workflows.

    Implements GAD-002 Decision 1: Hierarchical Orchestrator

    Responsibilities:
    - Load and execute state machine from YAML
    - Route to phase-specific handlers
    - Manage artifacts and state transitions
    - Enforce quality gates
    - Validate schemas
    - Track budget
    """

    def __init__(
        self,
        repo_root: Path,
        workflow_yaml: str = "agency_os/00_system/state_machine/ORCHESTRATION_workflow_design.yaml",
        contracts_yaml: str = "agency_os/00_system/contracts/ORCHESTRATION_data_contracts.yaml"
    ):
        """
        Initialize core orchestrator.

        Args:
            repo_root: Root directory of vibe-agency repo
            workflow_yaml: Path to workflow YAML (relative to repo_root)
            contracts_yaml: Path to contracts YAML (relative to repo_root)
        """
        self.repo_root = Path(repo_root)
        self.workflow_yaml_path = self.repo_root / workflow_yaml
        self.contracts_yaml_path = self.repo_root / contracts_yaml

        # Load workflow design
        self.workflow = self._load_workflow()

        # Initialize schema validator
        self.validator = SchemaValidator(self.contracts_yaml_path)

        # Initialize LLM client (will use NoOpClient if no API key)
        self.llm_client = None  # Lazy initialization per-project (to use project budget)

        # Initialize prompt runtime
        self.prompt_runtime = PromptRuntime(base_path=self.repo_root)

        # Paths
        self.workspaces_dir = self.repo_root / "workspaces"

        # Lazy-load handlers
        self._handlers = {}

        logger.info("Core Orchestrator initialized")

    # -------------------------------------------------------------------------
    # WORKFLOW LOADING
    # -------------------------------------------------------------------------

    def _load_workflow(self) -> Dict[str, Any]:
        """Load workflow design from YAML"""
        if not self.workflow_yaml_path.exists():
            raise FileNotFoundError(f"Workflow YAML not found: {self.workflow_yaml_path}")

        with open(self.workflow_yaml_path, 'r') as f:
            return yaml.safe_load(f)

    def get_phase_handler(self, phase: ProjectPhase):
        """
        Get handler for a phase (lazy loading).

        Implements GAD-002 Decision 1: Hierarchical Architecture
        """
        if phase not in self._handlers:
            # Import handler dynamically
            handlers_dir = Path(__file__).parent / "handlers"

            if phase == ProjectPhase.PLANNING:
                from handlers.planning_handler import PlanningHandler
                self._handlers[phase] = PlanningHandler(self)
            elif phase == ProjectPhase.CODING:
                from handlers.coding_handler import CodingHandler
                self._handlers[phase] = CodingHandler(self)
            elif phase == ProjectPhase.TESTING:
                from handlers.testing_handler import TestingHandler
                self._handlers[phase] = TestingHandler(self)
            elif phase == ProjectPhase.DEPLOYMENT:
                from handlers.deployment_handler import DeploymentHandler
                self._handlers[phase] = DeploymentHandler(self)
            elif phase == ProjectPhase.MAINTENANCE:
                from handlers.maintenance_handler import MaintenanceHandler
                self._handlers[phase] = MaintenanceHandler(self)
            else:
                raise ValueError(f"No handler for phase: {phase}")

        return self._handlers[phase]

    # -------------------------------------------------------------------------
    # PROJECT MANIFEST MANAGEMENT
    # -------------------------------------------------------------------------

    def load_project_manifest(self, project_id: str) -> ProjectManifest:
        """Load project manifest from workspace"""
        manifest_path = self._get_manifest_path(project_id)

        if not manifest_path.exists():
            raise FileNotFoundError(f"Project manifest not found: {manifest_path}")

        with open(manifest_path, 'r') as f:
            data = json.load(f)

        # Parse phase
        current_phase = ProjectPhase(data['status']['projectPhase'])

        # Parse planning sub-state (if exists)
        planning_sub_state = None
        if data['status'].get('planningSubState'):
            planning_sub_state = PlanningSubState(data['status']['planningSubState'])

        # Parse budget (GAD-002 Decision 7)
        budget = data.get('budget', {
            'max_cost_usd': 10.0,  # Default budget
            'current_cost_usd': 0.0,
            'alert_threshold': 0.80,
            'cost_breakdown': {}
        })

        return ProjectManifest(
            project_id=data['metadata']['projectId'],
            name=data['metadata']['name'],
            current_phase=current_phase,
            current_sub_state=planning_sub_state,
            artifacts=data.get('artifacts', {}),
            budget=budget,
            metadata=data
        )

    def save_project_manifest(self, manifest: ProjectManifest) -> None:
        """Save project manifest to workspace"""
        manifest_path = self._get_manifest_path(manifest.project_id)

        # Update manifest data
        manifest.metadata['status']['projectPhase'] = manifest.current_phase.value
        if manifest.current_sub_state:
            manifest.metadata['status']['planningSubState'] = manifest.current_sub_state.value
        else:
            manifest.metadata['status']['planningSubState'] = None

        manifest.metadata['artifacts'] = manifest.artifacts
        manifest.metadata['budget'] = manifest.budget
        manifest.metadata['status']['lastUpdate'] = datetime.utcnow().isoformat() + "Z"

        # Write to disk
        with open(manifest_path, 'w') as f:
            json.dump(manifest.metadata, f, indent=2)

        logger.info(f"Saved manifest: {manifest.project_id} (phase: {manifest.current_phase.value})")

    def _get_manifest_path(self, project_id: str) -> Path:
        """Get path to project manifest"""
        # Find project directory by project_id
        for workspace_dir in self.workspaces_dir.iterdir():
            if workspace_dir.is_dir():
                manifest_path = workspace_dir / "project_manifest.json"
                if manifest_path.exists():
                    with open(manifest_path, 'r') as f:
                        data = json.load(f)
                        if data['metadata']['projectId'] == project_id:
                            return manifest_path

        raise FileNotFoundError(f"Project {project_id} not found in workspaces")

    # -------------------------------------------------------------------------
    # ARTIFACT MANAGEMENT (with Schema Validation)
    # -------------------------------------------------------------------------

    def load_artifact(self, project_id: str, artifact_name: str) -> Optional[Dict[str, Any]]:
        """Load artifact from project workspace"""
        artifact_paths = {
            'research_brief.json': 'artifacts/planning/research_brief.json',
            'lean_canvas_summary.json': 'artifacts/planning/lean_canvas_summary.json',
            'feature_spec.json': 'artifacts/planning/feature_spec.json',
            'code_gen_spec.json': 'artifacts/coding/code_gen_spec.json',
            'test_plan.json': 'artifacts/testing/test_plan.json',
            'qa_report.json': 'artifacts/testing/qa_report.json',
            'deploy_receipt.json': 'artifacts/deployment/deploy_receipt.json'
        }

        if artifact_name not in artifact_paths:
            raise ValueError(f"Unknown artifact: {artifact_name}")

        # Find project directory
        project_dir = self._get_manifest_path(project_id).parent
        artifact_path = project_dir / artifact_paths[artifact_name]

        if not artifact_path.exists():
            return None

        with open(artifact_path, 'r') as f:
            return json.load(f)

    def save_artifact(
        self,
        project_id: str,
        artifact_name: str,
        data: Dict[str, Any],
        validate: bool = True
    ) -> None:
        """
        Save artifact to project workspace (with schema validation).

        Implements GAD-002 Decision 3: Centralized Schema Validation
        """
        # Validate before saving
        if validate:
            self.validator.validate_artifact(artifact_name, data)

        artifact_paths = {
            'research_brief.json': 'artifacts/planning/research_brief.json',
            'lean_canvas_summary.json': 'artifacts/planning/lean_canvas_summary.json',
            'feature_spec.json': 'artifacts/planning/feature_spec.json',
            'code_gen_spec.json': 'artifacts/coding/code_gen_spec.json',
            'test_plan.json': 'artifacts/testing/test_plan.json',
            'qa_report.json': 'artifacts/testing/qa_report.json',
            'deploy_receipt.json': 'artifacts/deployment/deploy_receipt.json'
        }

        if artifact_name not in artifact_paths:
            raise ValueError(f"Unknown artifact: {artifact_name}")

        # Find project directory
        project_dir = self._get_manifest_path(project_id).parent
        artifact_path = project_dir / artifact_paths[artifact_name]

        # Ensure directory exists
        artifact_path.parent.mkdir(parents=True, exist_ok=True)

        # Write artifact
        with open(artifact_path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"✓ Saved artifact: {artifact_name}")

    # -------------------------------------------------------------------------
    # AGENT EXECUTION (with LLM Client)
    # -------------------------------------------------------------------------

    def execute_agent(
        self,
        agent_name: str,
        task_id: str,
        inputs: Dict[str, Any],
        manifest: ProjectManifest
    ) -> Dict[str, Any]:
        """
        Execute agent by composing prompt and invoking LLM.

        Implements GAD-002 Decision 6: Agent Invocation Architecture

        Args:
            agent_name: Name of agent (e.g., "VIBE_ALIGNER")
            task_id: Task ID (e.g., "scope_negotiation")
            inputs: Input context for agent
            manifest: Project manifest (for budget tracking)

        Returns:
            Agent output (parsed JSON)
        """
        # Initialize LLM client with project budget
        if not self.llm_client:
            budget_limit = manifest.budget.get('max_cost_usd', 10.0)
            self.llm_client = LLMClient(budget_limit=budget_limit)

        try:
            # 1. Compose prompt using PromptRuntime
            logger.info(f"🤖 Executing agent: {agent_name}.{task_id}")
            prompt = self.prompt_runtime.execute_task(agent_name, task_id, inputs)

            # 2. Invoke LLM
            response = self.llm_client.invoke(
                prompt=prompt,
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096
            )

            # 3. Update budget in manifest
            cost_summary = self.llm_client.get_cost_summary()
            manifest.budget['current_cost_usd'] = cost_summary['total_cost_usd']

            # Track cost breakdown by phase
            phase_key = manifest.current_phase.value.lower()
            if phase_key not in manifest.budget.get('cost_breakdown', {}):
                manifest.budget.setdefault('cost_breakdown', {})[phase_key] = 0.0
            manifest.budget['cost_breakdown'][phase_key] = cost_summary['total_cost_usd']

            # Check budget alert threshold
            if cost_summary.get('budget_used_percent', 0) >= manifest.budget.get('alert_threshold', 0.80) * 100:
                logger.warning(
                    f"⚠️  Budget alert: {cost_summary['budget_used_percent']:.1f}% used "
                    f"(${cost_summary['total_cost_usd']:.2f} / ${manifest.budget['max_cost_usd']:.2f})"
                )

            # 4. Parse JSON output
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                # If not JSON, return as text
                logger.warning(f"Agent {agent_name} returned non-JSON response")
                return {"text": response.content}

        except BudgetExceededError as e:
            logger.error(f"❌ Budget limit reached: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Agent execution failed: {e}")
            raise

    # -------------------------------------------------------------------------
    # PHASE EXECUTION
    # -------------------------------------------------------------------------

    def execute_phase(self, manifest: ProjectManifest) -> None:
        """
        Execute current phase using appropriate handler.

        Implements GAD-002 Decision 1: Hierarchical Architecture
        """
        # Get handler for current phase
        handler = self.get_phase_handler(manifest.current_phase)

        # Execute phase
        logger.info(f"▶️  Executing phase: {manifest.current_phase.value}")
        handler.execute(manifest)

        # Save manifest after phase completion
        self.save_project_manifest(manifest)

        logger.info(f"✅ Phase complete: {manifest.current_phase.value}")

    def run_full_sdlc(self, project_id: str) -> None:
        """
        Run full SDLC workflow from current phase to PRODUCTION.

        This is the main entry point for orchestrator execution.
        """
        manifest = self.load_project_manifest(project_id)

        logger.info(f"🚀 Starting SDLC workflow for project: {manifest.name}")
        logger.info(f"   Current phase: {manifest.current_phase.value}")
        logger.info(f"   Budget: ${manifest.budget.get('max_cost_usd', 'N/A')}")

        # Execute phases until PRODUCTION
        while manifest.current_phase != ProjectPhase.PRODUCTION:
            self.execute_phase(manifest)

            # Reload manifest (handler may have updated it)
            manifest = self.load_project_manifest(project_id)

            # Check for AWAITING_QA_APPROVAL (durable wait state)
            if manifest.current_phase == ProjectPhase.AWAITING_QA_APPROVAL:
                logger.info("⏸️  Workflow paused - awaiting QA approval")
                logger.info(f"   Resume with: vibe-cli approve-qa --project={project_id}")
                break

        if manifest.current_phase == ProjectPhase.PRODUCTION:
            logger.info("🎉 SDLC workflow complete - project in PRODUCTION")

        # Print final cost summary
        logger.info("\n" + "="*60)
        logger.info("COST SUMMARY")
        logger.info("="*60)
        logger.info(f"Total cost: ${manifest.budget.get('current_cost_usd', 0):.4f}")
        logger.info(f"Budget limit: ${manifest.budget.get('max_cost_usd', 0):.2f}")
        if manifest.budget.get('cost_breakdown'):
            logger.info("\nBreakdown by phase:")
            for phase, cost in manifest.budget['cost_breakdown'].items():
                logger.info(f"  {phase}: ${cost:.4f}")


# =============================================================================
# CLI INTERFACE (FOR TESTING)
# =============================================================================

def main():
    """CLI interface for testing core orchestrator"""
    import sys

    if len(sys.argv) < 3:
        print("Usage: python core_orchestrator.py <repo_root> <project_id>")
        print("\nExample:")
        print("  python core_orchestrator.py /home/user/vibe-agency my-project-123")
        sys.exit(1)

    repo_root = Path(sys.argv[1])
    project_id = sys.argv[2]

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )

    # Initialize orchestrator
    orchestrator = CoreOrchestrator(repo_root)

    # Run full SDLC
    try:
        orchestrator.run_full_sdlc(project_id)
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
