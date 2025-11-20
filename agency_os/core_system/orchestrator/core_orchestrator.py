#!/usr/bin/env python3
"""
CORE ORCHESTRATOR - SDLC State Machine Controller
==================================================

Implements GAD-002 Decision 1: Hierarchical Orchestrator Architecture
Extended with GAD-003: Research Tool Integration

This is the master orchestrator that manages the complete SDLC workflow:
- PLANNING → CODING → TESTING → DEPLOYMENT → MAINTENANCE

Architecture:
- core_orchestrator.py (this file): State machine logic, routing, validation
- Phase handlers (planning_handler.py, etc.): Framework-specific execution logic
- llm_client.py: LLM invocation with retry, cost tracking
- prompt_runtime.py: Prompt composition from fragments
- tools/tool_executor.py: Tool execution for research agents (GAD-003)

Version: 1.1 (Phase 3 - GAD-002 + GAD-003)
"""

import json
import logging
import re
import subprocess
import time
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from agency_os.core_system.runtime.llm_client import BudgetExceededError, LLMClient
from agency_os.persistence.sqlite_store import SQLiteStore

# Initialize logger BEFORE using it
logger = logging.getLogger(__name__)

# GAD-003 Phase 2: Use PromptRegistry instead of PromptRuntime
# PromptRegistry provides automatic governance injection
try:
    from agency_os.core_system.runtime.prompt_registry import PromptRegistry

    PROMPT_REGISTRY_AVAILABLE = True
except ImportError:
    # Fallback to PromptRuntime if Registry not available
    from agency_os.core_system.runtime.prompt_runtime import PromptRuntime

    PROMPT_REGISTRY_AVAILABLE = False
    logger.warning("PromptRegistry not available, falling back to PromptRuntime")


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
    budget: dict[str, Any] = field(default_factory=dict)
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


class KernelViolationError(OrchestratorError):
    """
    Raised when Pre-Action Kernel check fails (GAD-005).

    Haiku-readable error format (GAD-502 Phase 3):
    - Simple explanation (1 sentence, no jargon)
    - Actionable remediation (numbered steps)
    - Working example (copy-pasteable)
    - Bad example (what they tried)
    """

    def __init__(
        self,
        operation: str,  # What they tried to do
        why: str,  # Simple 1-sentence explanation
        remediation: list[str],  # Numbered action steps
        example_good: str,  # Working code
        example_bad: str,  # What they tried
        learn_more: str | None = None,  # Optional doc link
    ):
        self.operation = operation
        self.why = why
        self.remediation = remediation
        self.example_good = example_good
        self.example_bad = example_bad
        self.learn_more = learn_more
        super().__init__(str(self))

    def __str__(self):
        msg = f"🚫 BLOCKED: {self.operation}\n\n"
        msg += f"WHY: {self.why}\n\n"
        msg += "WHAT TO DO INSTEAD:\n"
        for i, step in enumerate(self.remediation, 1):
            msg += f"  {i}. {step}\n"
        msg += "\nEXAMPLE:\n"
        msg += f"  ✅ {self.example_good}\n"
        msg += f"  ❌ {self.example_bad}\n"
        if self.learn_more:
            msg += f"\n📚 LEARN MORE: {self.learn_more}\n"
        return msg


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

        with open(contracts_yaml_path) as f:
            self.contracts = yaml.safe_load(f)

        logger.info(
            f"Schema validator initialized with {len(self.contracts.get('schemas', []))} schemas"
        )

    def validate_artifact(self, artifact_name: str, data: dict[str, Any]) -> None:
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
        schema_name = artifact_name.replace(".json", ".schema.json")
        schema_def = None

        for schema in self.contracts.get("schemas", []):
            if schema["name"] == schema_name:
                schema_def = schema
                break

        if not schema_def:
            logger.warning(f"No schema found for {artifact_name}, skipping validation")
            return

        # Basic validation (check required fields)
        # TODO: Full JSON Schema validation with jsonschema library
        errors = []

        for field_def in schema_def.get("fields", []):
            field_name = field_def["name"]
            required = field_def.get("required", False)

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
        workflow_yaml: str = "agency_os/core_system/state_machine/ORCHESTRATION_workflow_design.yaml",
        contracts_yaml: str = "agency_os/core_system/contracts/ORCHESTRATION_data_contracts.yaml",
        execution_mode: str = "delegated",
    ):
        """
        Initialize core orchestrator.

        Args:
            repo_root: Root directory of vibe-agency repo
            workflow_yaml: Path to workflow YAML (relative to repo_root)
            contracts_yaml: Path to contracts YAML (relative to repo_root)
            execution_mode: Execution mode - "delegated" (default, Claude Code integration) or "autonomous" (legacy)
        """
        self.repo_root = Path(repo_root)
        self.workflow_yaml_path = self.repo_root / workflow_yaml
        self.contracts_yaml_path = self.repo_root / contracts_yaml
        self.execution_mode = execution_mode

        # Load workflow design
        self.workflow = self._load_workflow()

        # Initialize schema validator
        self.validator = SchemaValidator(self.contracts_yaml_path)

        # Initialize LLM client (only for autonomous mode)
        self.llm_client = None  # Lazy initialization per-project (to use project budget)

        # Initialize prompt composition (Registry preferred, Runtime fallback)
        # PromptRegistry provides automatic Guardian Directives injection
        if PROMPT_REGISTRY_AVAILABLE:
            self.prompt_registry = PromptRegistry
            self.use_registry = True
            logger.info("✅ Using PromptRegistry (with governance injection)")
        else:
            self.prompt_runtime = PromptRuntime(base_path=self.repo_root)
            self.use_registry = False
            logger.warning("⚠️  Using PromptRuntime (fallback, no governance)")

        # Kernel violation tracking (GAD-502 Phase 5: Escalation)
        self._kernel_violations: dict[str, int] = {}

        # Paths
        self.workspaces_dir = self.repo_root / "workspaces"

        # Initialize SQLite persistence (ARCH-003: Dual Write Mode)
        db_path = self.repo_root / ".vibe" / "state" / "vibe_agency.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.sqlite_store = SQLiteStore(str(db_path))
        logger.info(f"✅ SQLite persistence initialized: {db_path}")

        # Lazy-load handlers
        self._handlers = {}

        # GAD-100 Phase 3: Add VibeConfig
        try:
            from lib.vibe_config import VibeConfig

            self.vibe_config = VibeConfig(repo_root=self.repo_root)
            self.system_self_aware = True
        except Exception as e:
            logger.warning(f"VibeConfig not available: {e}")
            self.vibe_config = None
            self.system_self_aware = False

        logger.info(f"Core Orchestrator initialized (mode: {execution_mode})")

    # -------------------------------------------------------------------------
    # WORKFLOW LOADING
    # -------------------------------------------------------------------------

    def _load_workflow(self) -> dict[str, Any]:
        """Load workflow design from YAML"""
        if not self.workflow_yaml_path.exists():
            raise FileNotFoundError(f"Workflow YAML not found: {self.workflow_yaml_path}")

        with open(self.workflow_yaml_path) as f:
            return yaml.safe_load(f)

    def get_phase_handler(self, phase: ProjectPhase):
        """
        Get handler for a phase (lazy loading).

        Implements GAD-002 Decision 1: Hierarchical Architecture
        """
        if phase not in self._handlers:
            # Import handler dynamically
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
    # SYSTEM HEALTH (GAD-100 Phase 3)
    # -------------------------------------------------------------------------

    def check_system_health(self) -> bool:
        """
        Check system health before phase transitions.

        Returns:
            True if system healthy, False if degraded

        Related: GAD-100 (VibeConfig), GAD-500 (integrity checks)
        """
        if not self.system_self_aware:
            # Graceful degradation: no VibeConfig = assume healthy
            return True

        try:
            return self.vibe_config.is_system_healthy()
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return True  # Fail open (don't block work)

    def get_system_status_summary(self) -> dict[str, Any]:
        """
        Get full system status for logging/debugging.

        Returns:
            Full status dict or error dict if VibeConfig unavailable
        """
        if not self.system_self_aware:
            return {"error": "VibeConfig not available"}

        try:
            return self.vibe_config.get_full_status()
        except Exception as e:
            return {"error": str(e)}

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

        # Validate manifest against schema (CRITICAL: Do this BEFORE accessing fields)
        try:
            self._validate_manifest_structure(data, project_id)
        except SchemaValidationError as e:
            raise OrchestratorError(f"Invalid project manifest for '{project_id}':\n{e}") from e

        # Parse phase
        current_phase = ProjectPhase(data["status"]["projectPhase"])

        # Parse planning sub-state (if exists)
        planning_sub_state = None
        if data["status"].get("planningSubState"):
            planning_sub_state = PlanningSubState(data["status"]["planningSubState"])

        # Parse budget (GAD-002 Decision 7)
        budget = data.get(
            "budget",
            {
                "max_cost_usd": 10.0,  # Default budget
                "current_cost_usd": 0.0,
                "alert_threshold": 0.80,
                "cost_breakdown": {},
            },
        )

        return ProjectManifest(
            project_id=data["metadata"]["projectId"],
            name=data["metadata"]["name"],
            current_phase=current_phase,
            current_sub_state=planning_sub_state,
            artifacts=data.get("artifacts", {}),
            budget=budget,
            metadata=data,
        )

    def save_project_manifest(self, manifest: ProjectManifest) -> None:
        """Save project manifest to workspace"""
        manifest_path = self._get_manifest_path(manifest.project_id)

        # Update manifest data
        manifest.metadata["status"]["projectPhase"] = manifest.current_phase.value
        if manifest.current_sub_state:
            manifest.metadata["status"]["planningSubState"] = manifest.current_sub_state.value
        else:
            manifest.metadata["status"]["planningSubState"] = None

        manifest.metadata["artifacts"] = manifest.artifacts
        manifest.metadata["budget"] = manifest.budget
        manifest.metadata["status"]["lastUpdate"] = datetime.utcnow().isoformat() + "Z"

        # Write to disk (JSON)
        with open(manifest_path, "w") as f:
            json.dump(manifest.metadata, f, indent=2)

        # ARCH-003: Dual Write Mode - also write to SQLite (Shadow Mode Phase 1)
        try:
            mission_id = self.sqlite_store.import_project_manifest(manifest.metadata)
            logger.debug(f"✅ Dual-write to SQLite: mission_id={mission_id}")
        except Exception as e:
            # Non-fatal - JSON is source of truth in Shadow Mode Phase 1
            logger.warning(f"⚠️ SQLite dual-write failed (non-fatal): {e}")

        logger.info(
            f"Saved manifest: {manifest.project_id} (phase: {manifest.current_phase.value})"
        )

    def _get_manifest_path(self, project_id: str) -> Path:
        """Get path to project manifest (robust search).

        Searches:
          - workspaces/ (non-recursive and recursive)
          - repo root (recursive) as a fallback

        Accepts a match when either:
          - metadata.projectId == project_id OR
          - parent directory name == project_id
        """
        searched_paths = []
        search_bases = []

        # Prefer explicit workspaces dir, but fall back to repo root
        if self.workspaces_dir.exists():
            search_bases.append(self.workspaces_dir)
        else:
            logger.warning(
                f"Workspaces directory not found at {self.workspaces_dir}; "
                f"falling back to repo root search"
            )
            search_bases.append(self.repo_root)

        # Always add repo_root as secondary fallback (avoids missing test fixtures)
        if self.repo_root not in search_bases:
            search_bases.append(self.repo_root)

        for base in search_bases:
            # search recursively to handle nested fixtures
            for manifest_path in base.rglob("project_manifest.json"):
                searched_paths.append(str(manifest_path))
                try:
                    with open(manifest_path) as f:
                        data = json.load(f)
                except (json.JSONDecodeError, OSError) as e:
                    logger.warning(f"Skipping invalid manifest {manifest_path}: {e}")
                    continue

                # Prefer explicit metadata.projectId match
                if data.get("metadata", {}).get("projectId") == project_id:
                    logger.debug(f"Found manifest for {project_id} at {manifest_path}")
                    return manifest_path

                # Fallback: if workspace folder name matches project_id
                if manifest_path.parent.name == project_id:
                    logger.debug(
                        f"Found manifest by parent folder match for {project_id} at {manifest_path}"
                    )
                    return manifest_path

        # Nothing found — include searched bases for diagnostics
        raise FileNotFoundError(
            f"Project '{project_id}' not found in workspaces. "
            f"Searched bases: {', '.join(str(p) for p in search_bases)}. "
            f"Checked manifest candidates: {len(searched_paths)} "
            f"(examples: {searched_paths[:5]})"
        )

    def _validate_manifest_structure(self, data: dict[str, Any], project_id: str) -> None:
        """
        Validate project manifest structure against required schema.

        This catches common errors (missing fields, wrong types) BEFORE
        we try to access them, providing clear error messages instead of KeyErrors.

        Args:
            data: Manifest data (loaded JSON)
            project_id: Project ID (for error messages)

        Raises:
            SchemaValidationError: If manifest structure is invalid
        """
        errors = []

        # Check top-level required fields
        required_fields = ["apiVersion", "kind", "metadata", "status", "artifacts"]
        for req_field in required_fields:
            if req_field not in data:
                errors.append(f"Missing required top-level field: '{req_field}'")

        # Validate metadata structure
        if "metadata" in data:
            metadata_required = ["projectId", "name", "owner", "createdAt"]
            for meta_field in metadata_required:
                if meta_field not in data["metadata"]:
                    errors.append(f"Missing required metadata field: 'metadata.{meta_field}'")

        # Validate status structure
        if "status" in data:
            if "projectPhase" not in data["status"]:
                errors.append("Missing required field: 'status.projectPhase'")
            else:
                # Validate phase value
                valid_phases = [
                    "PLANNING",
                    "CODING",
                    "TESTING",
                    "AWAITING_QA_APPROVAL",
                    "DEPLOYMENT",
                    "PRODUCTION",
                    "MAINTENANCE",
                ]
                if data["status"]["projectPhase"] not in valid_phases:
                    errors.append(
                        f"Invalid projectPhase: '{data['status']['projectPhase']}'. "
                        f"Must be one of: {', '.join(valid_phases)}"
                    )

        # Validate apiVersion
        if data.get("apiVersion") and data["apiVersion"] != "agency.os/v1alpha1":
            errors.append(
                f"Invalid apiVersion: '{data['apiVersion']}'. Expected: 'agency.os/v1alpha1'"
            )

        # Validate kind
        if data.get("kind") and data["kind"] != "Project":
            errors.append(f"Invalid kind: '{data['kind']}'. Expected: 'Project'")

        if errors:
            raise SchemaValidationError(
                f"Manifest validation failed for project '{project_id}':\n"
                + "\n".join(f"  - {e}" for e in errors)
            )

        logger.debug(f"✓ Manifest structure validation passed for '{project_id}'")

    # -------------------------------------------------------------------------
    # ARTIFACT MANAGEMENT (with Schema Validation)
    # -------------------------------------------------------------------------

    def load_artifact(self, project_id: str, artifact_name: str) -> dict[str, Any] | None:
        """Load artifact from project workspace"""
        artifact_paths = {
            "research_brief.json": "artifacts/planning/research_brief.json",
            "lean_canvas_summary.json": "artifacts/planning/lean_canvas_summary.json",
            "feature_spec.json": "artifacts/planning/feature_spec.json",
            "architecture.json": "artifacts/planning/architecture.json",
            "code_gen_spec.json": "artifacts/coding/code_gen_spec.json",
            "test_plan.json": "artifacts/testing/test_plan.json",
            "qa_report.json": "artifacts/testing/qa_report.json",
            "deploy_receipt.json": "artifacts/deployment/deploy_receipt.json",
            "bug_report.json": "artifacts/deployment/bug_report.json",
            "rollback_info.json": "artifacts/deployment/rollback_info.json",
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

    def save_artifact(
        self, project_id: str, artifact_name: str, data: dict[str, Any], validate: bool = True
    ) -> None:
        """
        Save artifact to project workspace (with schema validation).

        Implements GAD-002 Decision 3: Centralized Schema Validation
        NEW (GAD-005): Pre-Action Kernel check before saving
        """
        # PRE-ACTION KERNEL CHECK (GAD-005)
        self._kernel_check_save_artifact(artifact_name)

        # Validate before saving
        if validate:
            self.validator.validate_artifact(artifact_name, data)

        artifact_paths = {
            "research_brief.json": "artifacts/planning/research_brief.json",
            "lean_canvas_summary.json": "artifacts/planning/lean_canvas_summary.json",
            "feature_spec.json": "artifacts/planning/feature_spec.json",
            "architecture.json": "artifacts/planning/architecture.json",
            "code_gen_spec.json": "artifacts/coding/code_gen_spec.json",
            "test_plan.json": "artifacts/testing/test_plan.json",
            "qa_report.json": "artifacts/testing/qa_report.json",
            "deploy_receipt.json": "artifacts/deployment/deploy_receipt.json",
            "bug_report.json": "artifacts/deployment/bug_report.json",
            "rollback_info.json": "artifacts/deployment/rollback_info.json",
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

        logger.info(f"✓ Saved artifact: {artifact_name}")

    # -------------------------------------------------------------------------
    # AGENT EXECUTION (with LLM Client)
    # -------------------------------------------------------------------------

    def execute_agent(
        self, agent_name: str, task_id: str, inputs: dict[str, Any], manifest: ProjectManifest
    ) -> dict[str, Any]:
        """
        Execute agent by composing prompt and delegating to appropriate executor.

        Implements GAD-002 Decision 6: Agent Invocation Architecture
        NEW: Supports delegated execution (Claude Code integration)

        Args:
            agent_name: Name of agent (e.g., "VIBE_ALIGNER")
            task_id: Task ID (e.g., "scope_negotiation")
            inputs: Input context for agent
            manifest: Project manifest (for budget tracking)

        Returns:
            Agent output (parsed JSON)
        """
        try:
            # 1. Compose prompt (ALWAYS - this is the "Arm's" job)
            logger.info(f"🤖 Executing agent: {agent_name}.{task_id}")

            # Use PromptRegistry if available (provides governance injection)
            if self.use_registry:
                # PromptRegistry.compose() with automatic governance
                prompt = self.prompt_registry.compose(
                    agent=agent_name,
                    task=task_id,
                    workspace=manifest.name,  # Use manifest name as workspace
                    inject_governance=True,  # ALWAYS inject Guardian Directives
                    inject_tools=None,  # Tools loaded from agent's _composition.yaml
                    inject_sops=None,  # SOPs can be added per-task if needed
                    context=inputs,  # Pass inputs as context
                )
            else:
                # Fallback to PromptRuntime (no governance)
                prompt = self.prompt_runtime.execute_task(agent_name, task_id, inputs)

            # 2. Route based on execution mode
            if self.execution_mode == "delegated":
                # NEW: Request intelligence from external operator (Claude Code)
                return self._request_intelligence(agent_name, task_id, prompt, manifest)
            elif self.execution_mode == "autonomous":
                # OLD: Direct LLM invocation (legacy mode for testing)
                return self._execute_autonomous(agent_name, prompt, manifest)
            else:
                raise ValueError(f"Invalid execution mode: {self.execution_mode}")

        except BudgetExceededError as e:
            logger.error(f"❌ Budget limit reached: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Agent execution failed: {e}")
            raise

    def _request_intelligence(
        self, agent_name: str, task_id: str, prompt: str, manifest: ProjectManifest
    ) -> dict[str, Any]:
        """
        Request intelligence from external operator (Claude Code) via file-based delegation.

        This is the "Fließband" (conveyor belt) mechanism - the orchestrator
        (the "Arm") composes the prompt and hands it to the "Brain" (Claude Code)
        for execution.

        Protocol (GAD-003 File-Based):
        1. Write request to .delegation/request_{uuid}.json
        2. Poll for response file .delegation/response_{uuid}.json
        3. Read response and cleanup files
        4. Return result

        Args:
            agent_name: Agent name
            task_id: Task ID
            prompt: Composed prompt (ready for LLM)
            manifest: Project manifest

        Returns:
            Agent result (parsed from response)
        """
        # Generate request ID
        request_id = str(uuid.uuid4())

        # Build intelligence request
        request = {
            "type": "INTELLIGENCE_DELEGATION",
            "request_id": request_id,
            "agent": agent_name,
            "task_id": task_id,
            "prompt": prompt,
            "timestamp": datetime.now().isoformat(),
            "context": {
                "project_id": manifest.project_id,
                "phase": manifest.current_phase.value,
                "sub_state": (
                    manifest.current_sub_state.value if manifest.current_sub_state else None
                ),
            },
        }

        # Determine workspace directory
        workspace_dir = self.workspaces_dir / manifest.name / ".delegation"
        workspace_dir.mkdir(parents=True, exist_ok=True)

        # Write request file
        request_file = workspace_dir / f"request_{request_id}.json"
        response_file = workspace_dir / f"response_{request_id}.json"

        logger.info(f"📤 Writing delegation request: {request_file}")
        with open(request_file, "w") as f:
            json.dump(request, f, indent=2)

        # Poll for response file
        timeout = 600  # 10 minutes
        poll_interval = 0.5  # 500ms
        start_time = time.time()

        logger.info(f"⏳ Waiting for response file: {response_file}")
        logger.info(f"   Timeout: {timeout}s, Poll interval: {poll_interval}s")

        while not response_file.exists():
            elapsed = time.time() - start_time
            if elapsed > timeout:
                # Cleanup request file on timeout
                if request_file.exists():
                    request_file.unlink()
                raise TimeoutError(
                    f"No intelligence response after {timeout}s\n"
                    f"Request: {request_file}\n"
                    f"Expected response: {response_file}"
                )

            time.sleep(poll_interval)

        # Read response
        logger.info(f"✅ Response file found: {response_file}")
        with open(response_file) as f:
            response = json.load(f)

        # Cleanup files
        logger.info("🧹 Cleaning up delegation files...")
        if request_file.exists():
            request_file.unlink()
        if response_file.exists():
            response_file.unlink()

        # Extract result
        result = response.get("result")
        if result is None:
            raise RuntimeError(
                f"Intelligence response missing 'result' field\nResponse: {response}"
            )

        logger.info("✅ Intelligence response received and processed")
        return result

    # =========================================================================
    # PRE-ACTION KERNEL (GAD-005)
    # Simple validation checks before dangerous operations
    # =========================================================================

    def _kernel_check_save_artifact(self, artifact_name: str) -> None:
        """
        Kernel check: Prevent overwriting critical files (GAD-502 Phase 5: with escalation).

        Args:
            artifact_name: Name of artifact being saved

        Raises:
            KernelViolationError: If trying to overwrite critical file (escalates on repeat)
        """
        CRITICAL_FILES = ["project_manifest.json", ".session_handoff.json"]

        if artifact_name in CRITICAL_FILES:
            attempts = self._record_kernel_violation(f"overwrite_{artifact_name}")

            if attempts == 1:
                # First attempt: Helpful error
                raise KernelViolationError(
                    operation=f"You tried to overwrite {artifact_name}",
                    why="This file tracks critical system state. Overwriting it breaks the system.",
                    remediation=[
                        "Use the designated method: orchestrator.save_project_manifest(data)",
                        "Or check current content: cat project_manifest.json | jq .",
                        "If stuck, ask operator: 'How do I update the manifest?'",
                    ],
                    example_good="orchestrator.save_project_manifest({'phase': 'CODING'})",
                    example_bad=f"echo '{{}}' > {artifact_name}",
                )
            elif attempts == 2:
                # Second attempt: More explicit
                raise KernelViolationError(
                    operation=f"SECOND ATTEMPT to overwrite {artifact_name}",
                    why="This operation is BLOCKED (not a warning). You cannot bypass this.",
                    remediation=[
                        "STOP trying to overwrite directly",
                        "Use: orchestrator.save_project_manifest(data)",
                        "Ask operator: 'How do I update the manifest correctly?'",
                    ],
                    example_good="orchestrator.save_project_manifest(data)",
                    example_bad="ANY direct file write",
                )
            else:
                # Third+ attempt: Escalate to operator
                raise KernelViolationError(
                    operation=f"REPEATED VIOLATION ({attempts}x) - overwrite {artifact_name}",
                    why="You have tried multiple times. This is BLOCKED BY DESIGN.",
                    remediation=[
                        "🚨 YOU NEED OPERATOR HELP 🚨",
                        "Ask: 'I'm blocked trying to update manifest. What am I doing wrong?'",
                        "Do NOT retry this operation",
                    ],
                    example_good="[Ask operator - you're stuck in a loop]",
                    example_bad=f"Trying same operation {attempts} times",
                )

        logger.debug(f"✓ Kernel check passed: save_artifact({artifact_name})")

    def _kernel_check_transition_state(self, transition_name: str) -> None:
        """
        Kernel check: Warn if git working directory is not clean.

        Args:
            transition_name: Name of state transition
        """
        git_status = self._get_git_status()

        if not git_status.get("status", {}).get("clean", False):
            uncommitted = git_status.get("uncommitted_changes", [])[:5]
            changes_str = "\n".join(f"     - {line}" for line in uncommitted)
            logger.warning(
                f"⚠️  KERNEL WARNING: Git working directory not clean during transition: {transition_name}\n"
                f"   Uncommitted changes:\n"
                f"{changes_str}\n"
                f"\n"
                f"   Recommendation: Commit or stash changes before state transitions"
            )

        logger.debug(f"✓ Kernel check passed: transition_state({transition_name})")

    def _kernel_check_git_commit(self) -> None:
        """
        Kernel check: Block git commits if linting errors exist.

        Raises:
            KernelViolationError: If linting errors detected
        """
        status = self._get_system_status()
        linting = status.get("linting", {})

        if linting.get("status") == "failing":
            errors_count = linting.get("errors_count", 0)
            raise KernelViolationError(
                operation=f"You tried to commit code with {errors_count} linting errors",
                why="Linting errors cause CI/CD failures. Fix them before committing.",
                remediation=[
                    "Run: uv run ruff check . --fix",
                    "Check what's left: uv run ruff check .",
                    "Then retry: git commit",
                ],
                example_good="uv run ruff check . --fix && git commit -m 'message'",
                example_bad="git commit (without fixing linting errors)",
            )

        logger.debug("✓ Kernel check passed: git_commit()")

    def _kernel_check_shell_command(self, command: str) -> None:
        """
        Kernel check: Block dangerous shell operations (GAD-502 Phase 2).

        Prevents shell-based bypasses of Python kernel checks.
        Runs BEFORE executing any shell command.

        Args:
            command: Shell command to validate

        Raises:
            KernelViolationError: If command violates safety rules
        """
        import shlex

        # Parse command safely (to validate it's well-formed)
        try:
            shlex.split(command)
        except ValueError:
            # Malformed command - let shell handle error
            return

        # Dangerous patterns: (regex, error message, remediation)
        patterns = [
            # Critical file overwrites
            (
                r"(echo|cat|sed|awk).*>\s*(project_manifest\.json|\.session_handoff\.json|manifest\.json)",
                "You tried to overwrite a critical file via shell",
                "Critical files must be updated through orchestrator methods.",
                "orchestrator.save_project_manifest(data)",
                "echo '{}' > manifest.json",
            ),
            # Git operations without checks
            (
                r"git\s+push(?!\s+.*--dry-run)",
                "You tried to push without pre-push checks",
                "Git push requires pre-push validation to prevent CI/CD failures.",
                "./bin/pre-push-check.sh && git push",
                "git push origin main",
            ),
            # System integrity violations
            (
                r"(rm|mv|cp|chmod).*\.vibe/",
                "You tried to modify the system integrity directory",
                "The .vibe/ directory is protected by Layer 0 verification.",
                "[Don't modify .vibe/ - ask operator if you think this is needed]",
                "rm -rf .vibe/",
            ),
            # Direct manifest edits
            (
                r"(vim|nano|emacs|ed|vi).*manifest\.json",
                "You tried to directly edit manifest.json",
                "Use orchestrator methods to update manifest safely.",
                "orchestrator.save_project_manifest(updated_data)",
                "vim manifest.json",
            ),
        ]

        for pattern, operation_desc, why, example_good, example_bad in patterns:
            if re.search(pattern, command):
                raise KernelViolationError(
                    operation=operation_desc,
                    why=why,
                    remediation=[
                        f"Use: {example_good}",
                        "If stuck, ask operator: 'How do I do this safely?'",
                    ],
                    example_good=example_good,
                    example_bad=example_bad,
                )

        logger.debug(f"✓ Kernel check passed: shell_command({command[:50]}...)")

    def _record_kernel_violation(self, violation_type: str) -> int:
        """
        Record kernel violation attempt, return count (GAD-502 Phase 5).

        Args:
            violation_type: Type of violation (e.g., "overwrite_manifest", "git_push")

        Returns:
            int: Number of times this violation has been attempted (1-indexed)
        """
        self._kernel_violations[violation_type] = self._kernel_violations.get(violation_type, 0) + 1
        return self._kernel_violations[violation_type]

    def _get_system_status(self) -> dict[str, Any]:
        """
        Get current system status from .system_status.json

        Returns:
            System status dict
        """
        status_file = self.repo_root / ".system_status.json"
        if status_file.exists():
            with open(status_file) as f:
                return json.load(f)
        return {}

    def _get_git_status(self) -> dict[str, Any]:
        """
        Get git working directory status.

        Returns:
            Dict with git state
        """
        try:
            # Check if working directory is clean
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                check=False,
            )
            clean = len(result.stdout.strip()) == 0

            return {
                "status": {"clean": clean},
                "uncommitted_changes": result.stdout.strip().split("\n") if not clean else [],
            }
        except Exception as e:
            logger.warning(f"Failed to get git status: {e}")
            return {"status": {"clean": False}, "error": str(e)}

    def _parse_tool_use(self, text: str) -> dict[str, Any] | None:
        """
        Parse tool use XML from agent response (GAD-003)

        Expected format:
        <tool_use name="tool_name">
          <parameters>
            <param_name>value</param_name>
            ...
          </parameters>
        </tool_use>

        Args:
            text: Response text that might contain tool use

        Returns:
            Dict with 'name' and 'parameters' if tool use found, None otherwise
        """
        # Check if text contains tool_use tag
        if "<tool_use" not in text:
            return None

        try:
            # Extract tool_use XML (might be embedded in other text)
            match = re.search(r"<tool_use[^>]*>.*?</tool_use>", text, re.DOTALL)
            if not match:
                return None

            tool_xml = match.group(0)

            # Parse XML
            root = ET.fromstring(tool_xml)

            # Extract tool name from attribute
            tool_name = root.get("name")
            if not tool_name:
                logger.warning("Tool use missing 'name' attribute")
                return None

            # Extract parameters
            parameters = {}
            params_elem = root.find("parameters")
            if params_elem is not None:
                for param in params_elem:
                    param_name = param.tag
                    param_value = param.text or ""
                    parameters[param_name] = param_value

            return {"name": tool_name, "parameters": parameters}

        except ET.ParseError as e:
            logger.error(f"Failed to parse tool use XML: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing tool use: {e}")
            return None

    def _execute_autonomous(
        self, agent_name: str, prompt: str, manifest: ProjectManifest
    ) -> dict[str, Any]:
        """
        Execute agent autonomously (legacy mode) via direct LLM invocation.

        This is the OLD behavior - kept for backward compatibility and testing.

        Args:
            agent_name: Agent name
            prompt: Composed prompt
            manifest: Project manifest

        Returns:
            Agent output (parsed JSON)
        """
        # Initialize LLM client with project budget
        if not self.llm_client:
            budget_limit = manifest.budget.get("max_cost_usd", 10.0)
            self.llm_client = LLMClient(budget_limit=budget_limit)

        # Invoke LLM
        response = self.llm_client.invoke(
            prompt=prompt, model="claude-3-5-sonnet-20241022", max_tokens=4096
        )

        # Update budget in manifest
        cost_summary = self.llm_client.get_cost_summary()
        manifest.budget["current_cost_usd"] = cost_summary["total_cost_usd"]

        # Track cost breakdown by phase
        phase_key = manifest.current_phase.value.lower()
        if phase_key not in manifest.budget.get("cost_breakdown", {}):
            manifest.budget.setdefault("cost_breakdown", {})[phase_key] = 0.0
        manifest.budget["cost_breakdown"][phase_key] = cost_summary["total_cost_usd"]

        # Check budget alert threshold
        budget_used_percent = float(cost_summary.get("budget_used_percent", 0))
        if budget_used_percent >= manifest.budget.get("alert_threshold", 0.80) * 100:
            logger.warning(
                f"⚠️  Budget alert: {budget_used_percent:.1f}% used "
                f"(${cost_summary['total_cost_usd']:.2f} / ${manifest.budget['max_cost_usd']:.2f})"
            )

        # Parse JSON output
        try:
            # Defensive: ensure response.content is a string (not MagicMock in tests)
            content = str(response.content) if response.content else "{}"
            result = json.loads(content)

            # DEBUG: Log what we're returning for validation debugging
            logger.debug(f"🐛 execute_agent({agent_name}) returning keys={list(result.keys())}")

            return result
        except json.JSONDecodeError:
            # If not JSON, return as text
            logger.warning(f"Agent {agent_name} returned non-JSON response")
            return {"text": str(response.content)}

    # -------------------------------------------------------------------------
    # AUDITOR & QUALITY GATES (GAD-002 Decision 2 & 4)
    # -------------------------------------------------------------------------

    def invoke_auditor(
        self,
        check_type: str,
        manifest: ProjectManifest,
        severity: str = "info",
        blocking: bool = False,
    ) -> dict[str, Any]:
        """
        Invoke AUDITOR agent for quality gate checks.

        Implements GAD-002 Decision 2: Hybrid Blocking/Async Quality Gates
        Enhanced with GAD-004 Phase 2: Duration tracking for audit trail

        Args:
            check_type: Type of audit check (e.g., "prompt_security_scan", "code_security_scan")
            manifest: Project manifest
            severity: Severity level (critical, high, info)
            blocking: If True, raise exception on failure

        Returns:
            Audit report dict with status (PASS/FAIL), findings, duration_ms
        """
        # Track duration (GAD-004 Phase 2)
        start_time = time.time()

        logger.info(f"🔍 Running {severity.upper()} audit: {check_type} (blocking={blocking})")

        # Build audit context based on check type
        audit_context = self._build_audit_context(check_type, manifest)

        try:
            # Execute AUDITOR agent
            # Note: AUDITOR doesn't use task_id, it uses audit_mode in runtime_context
            audit_result = self.execute_agent(
                agent_name="AUDITOR",
                task_id="semantic_audit",  # Default task
                inputs=audit_context,
                manifest=manifest,
            )

            # Parse audit result
            status = audit_result.get("status", "UNKNOWN")
            findings = audit_result.get("findings", [])

            # Calculate duration (GAD-004 Phase 2)
            duration_ms = int((time.time() - start_time) * 1000)

            audit_report = {
                "check_type": check_type,
                "severity": severity,
                "blocking": blocking,
                "status": status,
                "findings": findings,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "duration_ms": duration_ms,  # GAD-004 Phase 2
            }

            # Add optional fields from audit result (GAD-004 Phase 2)
            if "message" in audit_result:
                audit_report["message"] = audit_result["message"]
            if "remediation" in audit_result:
                audit_report["remediation"] = audit_result["remediation"]

            # Log results
            if status == "PASS":
                logger.info(f"✅ Audit PASSED: {check_type} ({duration_ms}ms)")
            elif status == "FAIL":
                logger.warning(f"❌ Audit FAILED: {check_type} ({duration_ms}ms)")
                if findings:
                    for finding in findings[:3]:  # Show first 3 findings
                        logger.warning(f"   - {finding.get('description', 'N/A')}")
            else:
                logger.warning(f"⚠️  Audit status UNKNOWN: {check_type} ({duration_ms}ms)")

            # If blocking and failed, raise exception
            if blocking and status == "FAIL":
                raise QualityGateFailure(
                    f"Quality gate '{check_type}' FAILED (severity={severity})\n"
                    f"Findings: {len(findings)} issues found\n"
                    f"First issue: {findings[0].get('description', 'N/A') if findings else 'N/A'}"
                )

            return audit_report

        except BudgetExceededError:
            # Budget errors should propagate
            raise
        except QualityGateFailure:
            # Quality gate failures should propagate if blocking
            raise
        except Exception as e:
            # For non-blocking audits, log error and return failure report
            logger.error(f"❌ Audit execution error: {e}")

            # Calculate duration even on error (GAD-004 Phase 2)
            duration_ms = int((time.time() - start_time) * 1000)

            if blocking:
                raise QualityGateFailure(f"Audit execution failed: {e}")
            else:
                return {
                    "check_type": check_type,
                    "severity": severity,
                    "blocking": blocking,
                    "status": "ERROR",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "duration_ms": duration_ms,  # GAD-004 Phase 2
                }

    def _build_audit_context(self, check_type: str, manifest: ProjectManifest) -> dict[str, Any]:
        """
        Build audit context for specific check type.

        Maps quality gate check types to AUDITOR input format.
        """
        # Base context
        context = {
            "audit_mode": check_type,
            "project_id": manifest.project_id,
            "current_phase": manifest.current_phase.value,
            "target_files": [],
        }

        # Check-type specific context
        if check_type == "prompt_security_scan":
            # Scan all agent prompts in planning framework
            context["target_files"] = [
                "agency_os/01_planning_framework/agents/*/tasks/*.md",
                "agency_os/01_planning_framework/agents/*/_prompt_core.md",
            ]
            context["scan_for"] = [
                "prompt_injection_vulnerabilities",
                "instruction_override_risks",
                "context_pollution",
            ]

        elif check_type == "data_privacy_scan":
            # Scan feature specs and planning artifacts for PII leaks
            context["target_files"] = [
                f"workspaces/{manifest.project_id}/artifacts/planning/feature_spec.json",
                f"workspaces/{manifest.project_id}/artifacts/planning/lean_canvas_summary.json",
            ]
            context["scan_for"] = ["pii_leaks", "sensitive_data_exposure", "gdpr_compliance"]

        elif check_type == "code_security_scan":
            # Scan generated code for security vulnerabilities
            context["target_files"] = [
                f"workspaces/{manifest.project_id}/artifacts/coding/generated_code/**/*"
            ]
            context["scan_for"] = [
                "sql_injection",
                "xss_vulnerabilities",
                "hardcoded_secrets",
                "insecure_dependencies",
            ]

        elif check_type == "license_compliance_scan":
            # Scan dependencies for license compatibility
            context["target_files"] = [
                f"workspaces/{manifest.project_id}/artifacts/coding/code_gen_spec.json"
            ]
            context["scan_for"] = [
                "incompatible_licenses",
                "copyleft_violations",
                "missing_attributions",
            ]

        elif check_type == "feature_spec_validation":
            # Validate feature_spec against schema
            context["target_files"] = [
                f"workspaces/{manifest.project_id}/artifacts/planning/feature_spec.json"
            ]
            context["scan_for"] = [
                "schema_violations",
                "incomplete_specifications",
                "logical_inconsistencies",
            ]

        else:
            # Generic audit
            logger.warning(f"Unknown audit check type: {check_type}, using generic context")

        return context

    def apply_quality_gates(self, transition_name: str, manifest: ProjectManifest) -> None:
        """
        Apply quality gates for a state transition.

        Implements GAD-002 Decision 2: Hybrid Blocking/Async Quality Gates
        Enhanced with GAD-004 Phase 2: Record all gate results in manifest before blocking

        Args:
            transition_name: Name of transition (e.g., "T1_StartCoding")
            manifest: Project manifest

        Raises:
            QualityGateFailure: If blocking quality gate fails
        """
        # Find transition in workflow
        transition = None
        for t in self.workflow.get("transitions", []):
            if t["name"] == transition_name:
                transition = t
                break

        if not transition or "quality_gates" not in transition:
            # No quality gates for this transition
            return

        logger.info(f"🔒 Applying quality gates for transition: {transition_name}")

        quality_gates = transition["quality_gates"]
        audit_reports = []

        # GAD-004 Phase 2: Run ALL gates and record results BEFORE raising exceptions
        # This ensures durable state even when gates fail
        for gate in quality_gates:
            try:
                # Execute AUDITOR agent (always blocking=False to prevent early exception)
                audit_report = self.invoke_auditor(
                    check_type=gate["check"],
                    manifest=manifest,
                    severity=gate.get("severity", "critical"),
                    blocking=False,  # Don't raise exception yet (GAD-004)
                )

                # RECORD RESULT in manifest (GAD-004: new functionality)
                self._record_quality_gate_result(
                    manifest=manifest,
                    transition_name=transition_name,
                    gate=gate,
                    audit_report=audit_report,
                )

                audit_reports.append(audit_report)

                # NOW check if we should block (after recording)
                if gate.get("blocking", False) and audit_report.get("status") == "FAIL":
                    raise QualityGateFailure(
                        f"Quality gate '{gate['check']}' FAILED (severity={gate.get('severity')})\n"
                        f"Findings: {audit_report.get('findings', 'N/A')}\n"
                        f"Message: {audit_report.get('message', 'N/A')}\n"
                        f"Remediation: {audit_report.get('remediation', 'See audit report')}"
                    )

            except QualityGateFailure:
                # Gate failed - result already recorded in manifest
                # Re-raise to block transition
                raise
            except Exception as e:
                # Unexpected error - record as ERROR status
                logger.error(f"Quality gate execution error: {e}")
                error_report = {
                    "status": "ERROR",
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
                self._record_quality_gate_result(
                    manifest=manifest,
                    transition_name=transition_name,
                    gate=gate,
                    audit_report=error_report,
                )

                # If blocking, propagate error
                if gate.get("blocking", False):
                    raise QualityGateFailure(f"Quality gate execution failed: {e}") from e

        # Store audit reports in manifest artifacts (legacy compatibility)
        if audit_reports:
            if "quality_gate_reports" not in manifest.artifacts:
                manifest.artifacts["quality_gate_reports"] = {}
            manifest.artifacts["quality_gate_reports"][transition_name] = audit_reports

        logger.info(f"✅ Quality gates passed for: {transition_name}")

    def run_horizontal_audits(self, manifest: ProjectManifest) -> list[dict[str, Any]]:
        """
        Run horizontal audits for current phase.

        Implements GAD-002 Decision 4: Continuous Per-Phase Auditing

        Args:
            manifest: Project manifest

        Returns:
            List of audit reports
        """
        # Find current phase in workflow
        phase_name = manifest.current_phase.value
        phase_config = None

        for state in self.workflow.get("states", []):
            if state["name"] == phase_name:
                phase_config = state
                break

        if not phase_config or "horizontal_audits" not in phase_config:
            logger.info(f"No horizontal audits defined for phase: {phase_name}")
            return []

        logger.info(f"🔍 Running horizontal audits for phase: {phase_name}")

        horizontal_audits = phase_config["horizontal_audits"]
        audit_results = []

        for audit in horizontal_audits:
            try:
                audit_result = self.invoke_auditor(
                    check_type=audit["name"],
                    manifest=manifest,
                    severity=audit.get("severity", "info"),
                    blocking=audit.get("blocking", False),
                )
                audit_results.append(audit_result)
            except QualityGateFailure as e:
                # Blocking audit failed - propagate error
                logger.error(f"Horizontal audit BLOCKED phase completion: {e}")
                raise
            except Exception as e:
                logger.warning(f"Horizontal audit failed (non-blocking): {e}")
                audit_results.append(
                    {
                        "check_type": audit["name"],
                        "severity": audit.get("severity", "info"),
                        "blocking": False,
                        "status": "ERROR",
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                    }
                )

        # Store horizontal audit results in manifest
        if audit_results:
            if "horizontal_audits" not in manifest.artifacts:
                manifest.artifacts["horizontal_audits"] = {}
            manifest.artifacts["horizontal_audits"][phase_name] = audit_results

        logger.info(f"✅ Horizontal audits complete for phase: {phase_name}")
        return audit_results

    # -------------------------------------------------------------------------
    # GAD-004: Layer 2 - Workflow-Scoped Quality Gate Recording
    # -------------------------------------------------------------------------

    def _get_transition_config(self, transition_name: str) -> dict[str, Any]:
        """
        Get transition configuration from workflow YAML.

        Implements GAD-004 Phase 2: Quality gate result recording

        Args:
            transition_name: Name of transition (e.g., "T1_StartCoding")

        Returns:
            Transition config dict with from_state, to_state, quality_gates

        Raises:
            ValueError: If transition not found
        """
        for transition in self.workflow.get("transitions", []):
            if transition["name"] == transition_name:
                return transition

        raise ValueError(f"Transition not found in workflow: {transition_name}")

    def _record_quality_gate_result(
        self,
        manifest: ProjectManifest,
        transition_name: str,
        gate: dict[str, Any],
        audit_report: dict[str, Any],
    ) -> None:
        """
        Record quality gate result in manifest for auditability.

        Implements GAD-004 Phase 2: Durable state tracking for quality gates

        This enables:
        - Durable state (persists after process ends)
        - Audit trail (all gate executions recorded)
        - Async remediation (external tools can read manifest and fix)

        Args:
            manifest: Project manifest to update
            transition_name: Name of transition (e.g., "T1_StartCoding")
            gate: Gate config from workflow YAML
            audit_report: Result from AUDITOR agent
        """
        # Initialize qualityGates structure if not exists
        if "status" not in manifest.metadata:
            manifest.metadata["status"] = {}

        if "qualityGates" not in manifest.metadata["status"]:
            manifest.metadata["status"]["qualityGates"] = {}

        # Get or create transition record
        if transition_name not in manifest.metadata["status"]["qualityGates"]:
            # Extract transition info from workflow YAML
            try:
                transition = self._get_transition_config(transition_name)
                manifest.metadata["status"]["qualityGates"][transition_name] = {
                    "transition": f"{transition['from_state']} → {transition['to_state']}",
                    "gates": [],
                }
            except ValueError:
                # Fallback if transition not found
                manifest.metadata["status"]["qualityGates"][transition_name] = {
                    "transition": transition_name,
                    "gates": [],
                }

        # Build gate result record
        gate_result = {
            "check": gate["check"],
            "status": audit_report.get("status", "UNKNOWN"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Add optional fields
        if "duration_ms" in audit_report:
            gate_result["duration_ms"] = audit_report["duration_ms"]
        if "severity" in gate:
            gate_result["severity"] = gate["severity"]
        if "blocking" in gate:
            gate_result["blocking"] = gate["blocking"]
        if "findings" in audit_report:
            gate_result["findings"] = audit_report["findings"]
        if "message" in audit_report:
            gate_result["message"] = audit_report["message"]
        if "remediation" in audit_report:
            gate_result["remediation"] = audit_report["remediation"]

        # Append to gates list
        manifest.metadata["status"]["qualityGates"][transition_name]["gates"].append(gate_result)

        # Save manifest immediately (durable state)
        self.save_project_manifest(manifest)

        logger.info(f"✓ Recorded quality gate result: {gate['check']} = {gate_result['status']}")

    # -------------------------------------------------------------------------
    # PHASE EXECUTION
    # -------------------------------------------------------------------------

    def execute_phase(self, manifest: ProjectManifest) -> None:
        """
        Execute current phase using appropriate handler.

        Implements GAD-002 Decision 1: Hierarchical Architecture
        Implements GAD-002 Decision 4: Continuous Per-Phase Auditing
        Implements GAD-100 Phase 3: System health validation
        """
        # GAD-100 Phase 3: Check health before phase transition
        if self.system_self_aware:
            healthy = self.check_system_health()
            if not healthy:
                logger.warning("⚠️  System integrity degraded!")
                logger.warning("   Continuing but recommend running:")
                logger.warning("   python scripts/verify-system-integrity.py")
                # Don't block - just warn

        # Get handler for current phase
        handler = self.get_phase_handler(manifest.current_phase)

        # Execute phase
        logger.info(f"▶️  Executing phase: {manifest.current_phase.value}")
        handler.execute(manifest)

        # Run horizontal audits after phase completion (GAD-002 Decision 4)
        try:
            self.run_horizontal_audits(manifest)
        except QualityGateFailure:
            logger.error(f"Phase {manifest.current_phase.value} BLOCKED by horizontal audit")
            # Save manifest with audit failure
            self.save_project_manifest(manifest)
            raise

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
        logger.info("\n" + "=" * 60)
        logger.info("COST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total cost: ${manifest.budget.get('current_cost_usd', 0):.4f}")
        logger.info(f"Budget limit: ${manifest.budget.get('max_cost_usd', 0):.2f}")
        if manifest.budget.get("cost_breakdown"):
            logger.info("\nBreakdown by phase:")
            for phase, cost in manifest.budget["cost_breakdown"].items():
                logger.info(f"  {phase}: ${cost:.4f}")


# =============================================================================
# CLI INTERFACE (FOR TESTING)
# =============================================================================


def main():
    """CLI interface for testing core orchestrator"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Agency OS Core Orchestrator - SDLC State Machine Controller",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Delegated mode (default - for Claude Code integration)
  python core_orchestrator.py /home/user/vibe-agency my-project-123

  # Autonomous mode (legacy - for testing without Claude Code)
  python core_orchestrator.py /home/user/vibe-agency my-project-123 --mode=autonomous

Execution Modes:
  delegated   - Hands off prompts to Claude Code via STDOUT/STDIN (default)
  autonomous  - Executes prompts directly via Anthropic API (legacy)
        """,
    )

    parser.add_argument("repo_root", type=Path, help="Root directory of vibe-agency repository")
    parser.add_argument("project_id", type=str, help="Project ID (from project_manifest.json)")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["delegated", "autonomous"],
        default="delegated",
        help="Execution mode (default: delegated)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(message)s")

    # Initialize orchestrator
    orchestrator = CoreOrchestrator(repo_root=args.repo_root, execution_mode=args.mode)

    # Run full SDLC
    try:
        orchestrator.run_full_sdlc(args.project_id)
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
