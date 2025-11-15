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
import yaml
import logging
import sys
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# Add runtime to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "runtime"))

from llm_client import LLMClient, BudgetExceededError

# GAD-003 Phase 2: Use PromptRegistry instead of PromptRuntime
# PromptRegistry provides automatic governance injection
try:
    from prompt_registry import PromptRegistry
    PROMPT_REGISTRY_AVAILABLE = True
except ImportError:
    # Fallback to PromptRuntime if Registry not available
    from prompt_runtime import PromptRuntime
    PROMPT_REGISTRY_AVAILABLE = False
    logger.warning("PromptRegistry not available, falling back to PromptRuntime")

# GAD-003: Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "tools"))
try:
    from tool_executor import ToolExecutor
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False
    logging.warning("ToolExecutor not available - tool execution disabled")

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
        contracts_yaml: str = "agency_os/00_system/contracts/ORCHESTRATION_data_contracts.yaml",
        execution_mode: str = "delegated"
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

        # Paths
        self.workspaces_dir = self.repo_root / "workspaces"

        # Lazy-load handlers
        self._handlers = {}

        logger.info(f"Core Orchestrator initialized (mode: {execution_mode})")

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

        # Validate manifest against schema (CRITICAL: Do this BEFORE accessing fields)
        try:
            self._validate_manifest_structure(data, project_id)
        except SchemaValidationError as e:
            raise OrchestratorError(
                f"Invalid project manifest for '{project_id}':\n{e}"
            ) from e

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
                    try:
                        with open(manifest_path, 'r') as f:
                            data = json.load(f)
                            # Safely check for projectId (handle invalid manifests)
                            if data.get('metadata', {}).get('projectId') == project_id:
                                return manifest_path
                    except (json.JSONDecodeError, KeyError) as e:
                        # Skip invalid manifests (log warning but continue search)
                        logger.warning(
                            f"Skipping invalid manifest {manifest_path}: {e}"
                        )
                        continue

        raise FileNotFoundError(f"Project {project_id} not found in workspaces")

    def _validate_manifest_structure(self, data: Dict[str, Any], project_id: str) -> None:
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
        required_fields = ['apiVersion', 'kind', 'metadata', 'status', 'artifacts']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required top-level field: '{field}'")

        # Validate metadata structure
        if 'metadata' in data:
            metadata_required = ['projectId', 'name', 'owner', 'createdAt']
            for field in metadata_required:
                if field not in data['metadata']:
                    errors.append(f"Missing required metadata field: 'metadata.{field}'")

        # Validate status structure
        if 'status' in data:
            if 'projectPhase' not in data['status']:
                errors.append("Missing required field: 'status.projectPhase'")
            else:
                # Validate phase value
                valid_phases = ['PLANNING', 'CODING', 'TESTING', 'AWAITING_QA_APPROVAL', 'DEPLOYMENT', 'PRODUCTION', 'MAINTENANCE']
                if data['status']['projectPhase'] not in valid_phases:
                    errors.append(
                        f"Invalid projectPhase: '{data['status']['projectPhase']}'. "
                        f"Must be one of: {', '.join(valid_phases)}"
                    )

        # Validate apiVersion
        if data.get('apiVersion') and data['apiVersion'] != 'agency.os/v1alpha1':
            errors.append(
                f"Invalid apiVersion: '{data['apiVersion']}'. "
                f"Expected: 'agency.os/v1alpha1'"
            )

        # Validate kind
        if data.get('kind') and data['kind'] != 'Project':
            errors.append(
                f"Invalid kind: '{data['kind']}'. Expected: 'Project'"
            )

        if errors:
            raise SchemaValidationError(
                f"Manifest validation failed for project '{project_id}':\n" +
                "\n".join(f"  - {e}" for e in errors)
            )

        logger.debug(f"✓ Manifest structure validation passed for '{project_id}'")

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
                    inject_governance=True,   # ALWAYS inject Guardian Directives
                    inject_tools=None,        # Tools loaded from agent's _composition.yaml
                    inject_sops=None,         # SOPs can be added per-task if needed
                    context=inputs            # Pass inputs as context
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
        self,
        agent_name: str,
        task_id: str,
        prompt: str,
        manifest: ProjectManifest
    ) -> Dict[str, Any]:
        """
        Request intelligence from external operator (Claude Code) via STDOUT/STDIN handoff.

        This is the "Fließband" (conveyor belt) mechanism - the orchestrator
        (the "Arm") composes the prompt and hands it to the "Brain" (Claude Code)
        for execution.

        Protocol (GAD-003 Extended):
        1. Write INTELLIGENCE_REQUEST to STDOUT (JSON)
        2. Wait for response on STDIN
        3. If response contains <tool_use>: Execute tool, send result, goto 2
        4. If response is INTELLIGENCE_RESPONSE: Parse and return
        5. Otherwise: Pass through to user

        Args:
            agent_name: Agent name
            task_id: Task ID
            prompt: Composed prompt (ready for LLM)
            manifest: Project manifest

        Returns:
            Agent result (parsed from response)
        """
        # Build intelligence request
        request = {
            "type": "INTELLIGENCE_REQUEST",
            "agent": agent_name,
            "task_id": task_id,
            "prompt": prompt,
            "context": {
                "project_id": manifest.project_id,
                "phase": manifest.current_phase.value,
                "sub_state": manifest.current_sub_state.value if manifest.current_sub_state else None
            },
            "wait_for_response": True
        }

        # Write request to STDOUT with markers (for parsing)
        print("---INTELLIGENCE_REQUEST_START---", file=sys.stderr)
        print(json.dumps(request, indent=2))
        sys.stdout.flush()
        print("---INTELLIGENCE_REQUEST_END---", file=sys.stderr)

        # GAD-003: Initialize tool executor if available
        tool_executor = ToolExecutor() if TOOLS_AVAILABLE else None

        # GAD-003: Tool execution loop
        logger.info(f"⏳ Waiting for intelligence response from Claude Code...")
        while True:
            response_line = sys.stdin.readline()

            if not response_line:
                raise RuntimeError("No intelligence response received (EOF on STDIN)")

            response_text = response_line.strip()

            # GAD-003: Check if response contains tool use
            tool_call = self._parse_tool_use(response_text)
            if tool_call and tool_executor:
                logger.info(f"🔧 Tool call detected: {tool_call['name']}")

                # Execute tool
                try:
                    result = tool_executor.execute(tool_call['name'], tool_call['parameters'])
                    logger.info(f"✅ Tool executed successfully: {tool_call['name']}")
                except Exception as e:
                    logger.error(f"❌ Tool execution failed: {e}")
                    result = {'error': str(e)}

                # Send tool result back to Claude Code
                tool_result = {
                    "type": "TOOL_RESULT",
                    "tool": tool_call['name'],
                    "result": result
                }
                print("---TOOL_RESULT_START---", file=sys.stderr)
                print(json.dumps(tool_result, indent=2))
                sys.stdout.flush()
                print("---TOOL_RESULT_END---", file=sys.stderr)

                # Continue loop (wait for next response)
                continue

            # Check if final response (INTELLIGENCE_RESPONSE)
            try:
                response = json.loads(response_text)
                if response.get("type") == "INTELLIGENCE_RESPONSE":
                    # Extract result
                    result = response.get("result")
                    if result is None:
                        raise RuntimeError("Intelligence response missing 'result' field")

                    logger.info(f"✅ Intelligence response received from Claude Code")
                    return result
            except json.JSONDecodeError:
                # Not JSON - might be intermediate output, pass through
                print(response_text, file=sys.stderr)
                continue

            # If we get here, something unexpected happened
            logger.warning(f"Unexpected response format: {response_text[:100]}")
            print(response_text, file=sys.stderr)

    def _parse_tool_use(self, text: str) -> Optional[Dict[str, Any]]:
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
        if '<tool_use' not in text:
            return None

        try:
            # Extract tool_use XML (might be embedded in other text)
            match = re.search(r'<tool_use[^>]*>.*?</tool_use>', text, re.DOTALL)
            if not match:
                return None

            tool_xml = match.group(0)

            # Parse XML
            root = ET.fromstring(tool_xml)

            # Extract tool name from attribute
            tool_name = root.get('name')
            if not tool_name:
                logger.warning("Tool use missing 'name' attribute")
                return None

            # Extract parameters
            parameters = {}
            params_elem = root.find('parameters')
            if params_elem is not None:
                for param in params_elem:
                    param_name = param.tag
                    param_value = param.text or ""
                    parameters[param_name] = param_value

            return {
                'name': tool_name,
                'parameters': parameters
            }

        except ET.ParseError as e:
            logger.error(f"Failed to parse tool use XML: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing tool use: {e}")
            return None

    def _execute_autonomous(
        self,
        agent_name: str,
        prompt: str,
        manifest: ProjectManifest
    ) -> Dict[str, Any]:
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
            budget_limit = manifest.budget.get('max_cost_usd', 10.0)
            self.llm_client = LLMClient(budget_limit=budget_limit)

        # Invoke LLM
        response = self.llm_client.invoke(
            prompt=prompt,
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096
        )

        # Update budget in manifest
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

        # Parse JSON output
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            # If not JSON, return as text
            logger.warning(f"Agent {agent_name} returned non-JSON response")
            return {"text": response.content}

    # -------------------------------------------------------------------------
    # AUDITOR & QUALITY GATES (GAD-002 Decision 2 & 4)
    # -------------------------------------------------------------------------

    def invoke_auditor(
        self,
        check_type: str,
        manifest: ProjectManifest,
        severity: str = "info",
        blocking: bool = False
    ) -> Dict[str, Any]:
        """
        Invoke AUDITOR agent for quality gate checks.

        Implements GAD-002 Decision 2: Hybrid Blocking/Async Quality Gates

        Args:
            check_type: Type of audit check (e.g., "prompt_security_scan", "code_security_scan")
            manifest: Project manifest
            severity: Severity level (critical, high, info)
            blocking: If True, raise exception on failure

        Returns:
            Audit report dict with status (PASS/FAIL) and findings
        """
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
                manifest=manifest
            )

            # Parse audit result
            status = audit_result.get('status', 'UNKNOWN')
            findings = audit_result.get('findings', [])

            audit_report = {
                'check_type': check_type,
                'severity': severity,
                'blocking': blocking,
                'status': status,
                'findings': findings,
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }

            # Log results
            if status == "PASS":
                logger.info(f"✅ Audit PASSED: {check_type}")
            elif status == "FAIL":
                logger.warning(f"❌ Audit FAILED: {check_type}")
                if findings:
                    for finding in findings[:3]:  # Show first 3 findings
                        logger.warning(f"   - {finding.get('description', 'N/A')}")
            else:
                logger.warning(f"⚠️  Audit status UNKNOWN: {check_type}")

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
            if blocking:
                raise QualityGateFailure(f"Audit execution failed: {e}")
            else:
                return {
                    'check_type': check_type,
                    'severity': severity,
                    'blocking': blocking,
                    'status': 'ERROR',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }

    def _build_audit_context(self, check_type: str, manifest: ProjectManifest) -> Dict[str, Any]:
        """
        Build audit context for specific check type.

        Maps quality gate check types to AUDITOR input format.
        """
        # Base context
        context = {
            'audit_mode': check_type,
            'project_id': manifest.project_id,
            'current_phase': manifest.current_phase.value,
            'target_files': []
        }

        # Check-type specific context
        if check_type == "prompt_security_scan":
            # Scan all agent prompts in planning framework
            context['target_files'] = [
                'agency_os/01_planning_framework/agents/*/tasks/*.md',
                'agency_os/01_planning_framework/agents/*/_prompt_core.md'
            ]
            context['scan_for'] = [
                'prompt_injection_vulnerabilities',
                'instruction_override_risks',
                'context_pollution'
            ]

        elif check_type == "data_privacy_scan":
            # Scan feature specs and planning artifacts for PII leaks
            context['target_files'] = [
                f"workspaces/{manifest.project_id}/artifacts/planning/feature_spec.json",
                f"workspaces/{manifest.project_id}/artifacts/planning/lean_canvas_summary.json"
            ]
            context['scan_for'] = [
                'pii_leaks',
                'sensitive_data_exposure',
                'gdpr_compliance'
            ]

        elif check_type == "code_security_scan":
            # Scan generated code for security vulnerabilities
            context['target_files'] = [
                f"workspaces/{manifest.project_id}/artifacts/coding/generated_code/**/*"
            ]
            context['scan_for'] = [
                'sql_injection',
                'xss_vulnerabilities',
                'hardcoded_secrets',
                'insecure_dependencies'
            ]

        elif check_type == "license_compliance_scan":
            # Scan dependencies for license compatibility
            context['target_files'] = [
                f"workspaces/{manifest.project_id}/artifacts/coding/code_gen_spec.json"
            ]
            context['scan_for'] = [
                'incompatible_licenses',
                'copyleft_violations',
                'missing_attributions'
            ]

        elif check_type == "feature_spec_validation":
            # Validate feature_spec against schema
            context['target_files'] = [
                f"workspaces/{manifest.project_id}/artifacts/planning/feature_spec.json"
            ]
            context['scan_for'] = [
                'schema_violations',
                'incomplete_specifications',
                'logical_inconsistencies'
            ]

        else:
            # Generic audit
            logger.warning(f"Unknown audit check type: {check_type}, using generic context")

        return context

    def apply_quality_gates(
        self,
        transition_name: str,
        manifest: ProjectManifest
    ) -> None:
        """
        Apply quality gates for a state transition.

        Implements GAD-002 Decision 2: Hybrid Blocking/Async Quality Gates

        Args:
            transition_name: Name of transition (e.g., "T1_StartCoding")
            manifest: Project manifest

        Raises:
            QualityGateFailure: If blocking quality gate fails
        """
        # Find transition in workflow
        transition = None
        for t in self.workflow.get('transitions', []):
            if t['name'] == transition_name:
                transition = t
                break

        if not transition or 'quality_gates' not in transition:
            # No quality gates for this transition
            return

        logger.info(f"🔒 Applying quality gates for transition: {transition_name}")

        quality_gates = transition['quality_gates']
        audit_reports = []

        # Run blocking quality gates first
        for gate in quality_gates:
            if gate.get('blocking', False):
                audit_report = self.invoke_auditor(
                    check_type=gate['check'],
                    manifest=manifest,
                    severity=gate.get('severity', 'critical'),
                    blocking=True
                )
                audit_reports.append(audit_report)

        # Run async quality gates (fire and forget)
        for gate in quality_gates:
            if not gate.get('blocking', False):
                try:
                    audit_report = self.invoke_auditor(
                        check_type=gate['check'],
                        manifest=manifest,
                        severity=gate.get('severity', 'info'),
                        blocking=False
                    )
                    audit_reports.append(audit_report)
                except Exception as e:
                    logger.warning(f"Async audit failed (non-blocking): {e}")

        # Store audit reports in manifest
        if audit_reports:
            if 'quality_gate_reports' not in manifest.artifacts:
                manifest.artifacts['quality_gate_reports'] = {}
            manifest.artifacts['quality_gate_reports'][transition_name] = audit_reports

        logger.info(f"✅ Quality gates passed for: {transition_name}")

    def run_horizontal_audits(
        self,
        manifest: ProjectManifest
    ) -> List[Dict[str, Any]]:
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

        for state in self.workflow.get('states', []):
            if state['name'] == phase_name:
                phase_config = state
                break

        if not phase_config or 'horizontal_audits' not in phase_config:
            logger.info(f"No horizontal audits defined for phase: {phase_name}")
            return []

        logger.info(f"🔍 Running horizontal audits for phase: {phase_name}")

        horizontal_audits = phase_config['horizontal_audits']
        audit_results = []

        for audit in horizontal_audits:
            try:
                audit_result = self.invoke_auditor(
                    check_type=audit['name'],
                    manifest=manifest,
                    severity=audit.get('severity', 'info'),
                    blocking=audit.get('blocking', False)
                )
                audit_results.append(audit_result)
            except QualityGateFailure as e:
                # Blocking audit failed - propagate error
                logger.error(f"Horizontal audit BLOCKED phase completion: {e}")
                raise
            except Exception as e:
                logger.warning(f"Horizontal audit failed (non-blocking): {e}")
                audit_results.append({
                    'check_type': audit['name'],
                    'severity': audit.get('severity', 'info'),
                    'blocking': False,
                    'status': 'ERROR',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                })

        # Store horizontal audit results in manifest
        if audit_results:
            if 'horizontal_audits' not in manifest.artifacts:
                manifest.artifacts['horizontal_audits'] = {}
            manifest.artifacts['horizontal_audits'][phase_name] = audit_results

        logger.info(f"✅ Horizontal audits complete for phase: {phase_name}")
        return audit_results

    # -------------------------------------------------------------------------
    # PHASE EXECUTION
    # -------------------------------------------------------------------------

    def execute_phase(self, manifest: ProjectManifest) -> None:
        """
        Execute current phase using appropriate handler.

        Implements GAD-002 Decision 1: Hierarchical Architecture
        Implements GAD-002 Decision 4: Continuous Per-Phase Auditing
        """
        # Get handler for current phase
        handler = self.get_phase_handler(manifest.current_phase)

        # Execute phase
        logger.info(f"▶️  Executing phase: {manifest.current_phase.value}")
        handler.execute(manifest)

        # Run horizontal audits after phase completion (GAD-002 Decision 4)
        try:
            self.run_horizontal_audits(manifest)
        except QualityGateFailure as e:
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
        """
    )

    parser.add_argument(
        'repo_root',
        type=Path,
        help='Root directory of vibe-agency repository'
    )
    parser.add_argument(
        'project_id',
        type=str,
        help='Project ID (from project_manifest.json)'
    )
    parser.add_argument(
        '--mode',
        type=str,
        choices=['delegated', 'autonomous'],
        default='delegated',
        help='Execution mode (default: delegated)'
    )
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(message)s'
    )

    # Initialize orchestrator
    orchestrator = CoreOrchestrator(
        repo_root=args.repo_root,
        execution_mode=args.mode
    )

    # Run full SDLC
    try:
        orchestrator.run_full_sdlc(args.project_id)
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
