"""
STEWARD Protocol Compliance for Vibe-Agency Agents (ARCH-026 Phase 3).

This module generates machine-readable STEWARD manifests from VibeAgent instances,
enabling agents to declare their identity, capabilities, and compliance level
to other agents in the system.

Architecture:
- ManifestGenerator: Converts VibeAgent → steward.json (STEWARD Compliance Level 1)
- AgentManifest: Wrapper for STEWARD manifest with validation
- Registry: In-memory registry of agent manifests

Design:
- Minimal first: Generate valid Level 1 (agent identity + capabilities only)
- Extensible: Easy to add Level 2 (runtime introspection) and Level 3+ later
- Testable: Each component is independently unit-testable
- Non-invasive: Doesn't require changes to existing VibeAgent subclasses

Example Usage:
    >>> from vibe_core.agents import SimpleLLMAgent
    >>> from vibe_core.identity import ManifestGenerator
    >>>
    >>> agent = SimpleLLMAgent(agent_id="assistant", provider=...)
    >>> generator = ManifestGenerator()
    >>> manifest_dict = generator.generate(agent)
    >>> print(manifest_dict["agent"]["id"])  # "assistant"
    >>> print(manifest_dict["agent"]["class"])  # "orchestration_operator"
"""

import json
import logging
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

from vibe_core.agent_protocol import VibeAgent

logger = logging.getLogger(__name__)


class ManifestGenerator:
    """
    Generates STEWARD-compliant manifests from VibeAgent instances.

    This class implements STEWARD Protocol Level 1 Compliance:
    - Agent identity (id, name, version, class)
    - Capabilities (operations list)
    - Credentials (mandate, constraints, prime_directive)
    - Basic governance metadata

    Design:
    - Works with any VibeAgent subclass
    - Determines agent class (orchestration_operator vs task_executor) by inspection
    - Handles SimpleLLMAgent and SpecialistAgent cases
    - Generates valid JSON per STEWARD_JSON_SCHEMA.json

    Future: Extend for Level 2 (runtime introspection) and Level 3+ (federation)
    """

    # Agent class mapping: Python type → STEWARD class
    AGENT_CLASS_MAPPING = {
        "SimpleLLMAgent": "orchestration_operator",  # LLM agents think/orchestrate
        "SpecialistAgent": "task_executor",  # Specialists execute workflow phases
    }

    # Specialization mapping: Agent type → domain
    SPECIALIZATION_MAPPING = {
        "SimpleLLMAgent": "cognitive_orchestration",
        "SpecialistAgent": "workflow_execution",
    }

    def __init__(self, issuing_org: str = "vibe-agency", version: str = "1.0.0"):
        """
        Initialize the manifest generator.

        Args:
            issuing_org: Organization issuing the manifest (for governance.principal)
            version: STEWARD protocol version (semver)

        Example:
            >>> generator = ManifestGenerator(issuing_org="my-company", version="1.0.0")
        """
        self.issuing_org = issuing_org
        self.protocol_version = version

    def generate(self, agent: VibeAgent) -> dict[str, Any]:
        """
        Generate a STEWARD-compliant manifest for an agent.

        This method produces a valid steward.json dict that includes:
        1. steward_version: Protocol version (1.0.0 for Level 1)
        2. agent: Identity (id, name, version, class, specialization, status)
        3. credentials: Mandate, constraints, prime_directive
        4. capabilities: Operations list (derived from agent.capabilities)
        5. runtime: Introspection endpoints (optional for Level 1)
        6. governance: Issuing org, transparency level

        Args:
            agent: VibeAgent instance to generate manifest for

        Returns:
            dict: Valid steward.json structure per STEWARD_JSON_SCHEMA.json

        Raises:
            TypeError: If agent is not a VibeAgent instance

        Example:
            >>> agent = MyAgent()
            >>> manifest = generator.generate(agent)
            >>> # Manifest is ready to be:
            >>> # - Stored to disk (data/registry/agent_id.steward.json)
            >>> # - Signed (steward sign manifest.json)
            >>> # - Registered (steward registry publish manifest.json)
        """
        if not isinstance(agent, VibeAgent):
            raise TypeError(f"Expected VibeAgent, got {type(agent).__name__}")

        agent_class_name = agent.__class__.__name__
        agent_type = self.AGENT_CLASS_MAPPING.get(
            agent_class_name,
            "orchestration_operator",  # Default to orchestration
        )

        specialization = self.SPECIALIZATION_MAPPING.get(agent_class_name, "general")

        # Build the manifest
        manifest = {
            "steward_version": self.protocol_version,
            "agent": self._build_agent_section(agent, agent_type, specialization),
            "credentials": self._build_credentials_section(),
            "capabilities": self._build_capabilities_section(agent),
            "runtime": self._build_runtime_section(agent),
            "governance": self._build_governance_section(),
        }

        logger.debug(f"Generated STEWARD manifest for {agent.agent_id}")
        return manifest

    def _build_agent_section(
        self, agent: VibeAgent, agent_type: str, specialization: str
    ) -> dict[str, Any]:
        """
        Build the 'agent' section of the manifest.

        This includes identity information like:
        - id: Agent unique identifier
        - name: Human-readable name
        - version: Agent version (default: 1.0.0)
        - class: STEWARD agent class (orchestration_operator, task_executor, etc.)
        - specialization: Domain of expertise
        - status: Operational status (default: "active")
        - issued_by: Organization issuing the manifest
        - issued_date: ISO 8601 timestamp

        Args:
            agent: The VibeAgent instance
            agent_type: STEWARD class (orchestration_operator, task_executor)
            specialization: Domain of expertise

        Returns:
            dict: Agent section with required fields
        """
        now = datetime.now(timezone.utc).isoformat()  # noqa: UP017 (UTC not available in Python 3.11)

        return {
            "id": agent.agent_id,
            "name": self._humanize_agent_id(agent.agent_id),
            "version": "1.0.0",  # Default version for all agents
            "class": agent_type,
            "specialization": specialization,
            "status": "active",  # All registered agents are active
            "issued_by": self.issuing_org,
            "issued_date": now,
        }

    def _build_credentials_section(self) -> dict[str, Any]:
        """
        Build the 'credentials' section (mandate, constraints, prime_directive).

        This defines what the agent is authorized to do and what it's forbidden from doing.
        For Level 1, we use vibe-agency's core principles.

        Returns:
            dict: Credentials section with mandate, constraints, prime_directive

        Example:
            >>> creds = generator._build_credentials_section()
            >>> print(creds["prime_directive"])
            "Trust tests over claims, verify over assume"
        """
        return {
            "mandate": [
                {
                    "capability": "*",  # Agent can use all its declared capabilities
                    "scope": ["*"],  # Universal scope
                }
            ],
            "constraints": [
                {
                    "forbidden": "bypass_tests",
                    "reason": "Test-first discipline mandatory",
                },
                {
                    "forbidden": "access_production_without_approval",
                    "reason": "Safety-first principle",
                },
            ],
            "prime_directive": (
                "Trust tests over claims, verify over assume. "
                "When in doubt, RUN THE VERIFICATION COMMAND."
            ),
        }

    def _build_capabilities_section(self, agent: VibeAgent) -> dict[str, Any]:
        """
        Build the 'capabilities' section (interfaces and operations).

        This describes what the agent can do:
        - interfaces: How to communicate with the agent (CLI, API, etc.)
        - operations: List of supported operations with input/output schemas

        For Level 1, we support simple capability declaration without full
        JSON schema. Future versions can add detailed schemas.

        Args:
            agent: The VibeAgent instance

        Returns:
            dict: Capabilities section with interfaces and operations

        Example:
            >>> agent = SimpleLLMAgent(agent_id="assistant", ...)
            >>> caps = generator._build_capabilities_section(agent)
            >>> print(caps["operations"])
            [{"name": "process", "description": "Process task via LLM", ...}]
        """
        capabilities = agent.capabilities  # List[str]

        # Build operations list from capabilities
        operations = []
        for cap_name in capabilities:
            operations.append(
                {
                    "name": cap_name,
                    "description": f"Agent capability: {cap_name}",
                    "input_schema": {
                        "type": "object",
                        "description": f"Input for {cap_name} operation",
                    },
                    "output_schema": {
                        "type": "object",
                        "description": f"Output from {cap_name} operation",
                    },
                    "idempotent": False,  # Conservative default
                    "versioned": False,
                }
            )

        # Also add a generic "process" operation (all agents support this)
        if not any(op["name"] == "process" for op in operations):
            operations.append(
                {
                    "name": "process",
                    "description": "Process a task via the agent",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "task": {"type": "object", "description": "Task to process"}
                        },
                        "description": "Task processing operation",
                    },
                    "output_schema": {
                        "type": "object",
                        "description": "Agent response (AgentResponse format)",
                    },
                    "idempotent": False,
                    "versioned": False,
                }
            )

        return {
            "interfaces": [
                {
                    "type": "cli",
                    "protocol": "python",
                    "endpoint": f"vibe_core.agents.{agent.__class__.__module__}",
                }
            ],
            "operations": operations,
        }

    def _build_runtime_section(self, agent: VibeAgent) -> dict[str, Any]:
        """
        Build the 'runtime' section (introspection endpoints).

        This describes how to query the agent's runtime state. For Level 1,
        we provide minimal info. Level 2+ can add:
        - Live health checks
        - State query endpoints
        - Log access

        Args:
            agent: The VibeAgent instance

        Returns:
            dict: Runtime section with introspection metadata
        """
        return {
            "introspection_endpoint": f"kernel.get_agent_manifest('{agent.agent_id}')",
            "state_query": f"kernel.get_agent_status('{agent.agent_id}')",
            "logs": "kernel.ledger.query(agent_id='{agent.agent_id}')",
        }

    def _build_governance_section(self) -> dict[str, Any]:
        """
        Build the 'governance' section (organization and transparency).

        This declares who controls the agent and what transparency level is offered.

        Returns:
            dict: Governance section with principal, contact, transparency
        """
        return {
            "principal": f"{self.issuing_org}-core-team",
            "contact": "https://github.com/kimeisele/vibe-agency",
            "audit_trail": "vibe_core/ledger.db",
            "transparency": "public",
        }

    @staticmethod
    def _humanize_agent_id(agent_id: str) -> str:
        """
        Convert kebab-case agent_id to Title Case.

        Args:
            agent_id: Agent ID (e.g., "specialist-planning")

        Returns:
            str: Human-readable name (e.g., "Specialist Planning")

        Example:
            >>> ManifestGenerator._humanize_agent_id("specialist-planning")
            "Specialist Planning"
        """
        return agent_id.replace("-", " ").title()


class AgentManifest:
    """
    Wrapper for a STEWARD manifest with validation and access methods.

    This class provides:
    - Validation against STEWARD_JSON_SCHEMA
    - Convenient property access (manifest.agent_id, manifest.capabilities)
    - Serialization (to_json, to_dict)
    - Fingerprinting (for signing)

    Example:
        >>> generator = ManifestGenerator()
        >>> agent = SimpleLLMAgent(...)
        >>> manifest_dict = generator.generate(agent)
        >>> manifest = AgentManifest(manifest_dict)
        >>> print(manifest.agent_id)  # agent's ID
        >>> print(manifest.capabilities)  # List[str] of capabilities
        >>> print(manifest.to_json())  # JSON string
    """

    def __init__(self, manifest_dict: dict[str, Any]):
        """
        Initialize an AgentManifest from a dictionary.

        Args:
            manifest_dict: The manifest dictionary (from ManifestGenerator.generate())

        Raises:
            ValueError: If manifest is invalid per STEWARD_JSON_SCHEMA

        Example:
            >>> manifest = AgentManifest({"steward_version": "1.0.0", ...})
        """
        self.manifest = manifest_dict
        self._validate()
        logger.debug(f"Initialized AgentManifest for {self.agent_id}")

    @property
    def agent_id(self) -> str:
        """Return the agent's unique identifier."""
        return self.manifest["agent"]["id"]

    @property
    def agent_class(self) -> str:
        """Return the STEWARD agent class (orchestration_operator, task_executor, etc.)."""
        return self.manifest["agent"]["class"]

    @property
    def capabilities(self) -> list[str]:
        """Return list of operation names from the manifest."""
        return [op["name"] for op in self.manifest["capabilities"]["operations"]]

    @property
    def version(self) -> str:
        """Return the agent's version."""
        return self.manifest["agent"]["version"]

    @property
    def specialization(self) -> str:
        """Return the agent's specialization domain."""
        return self.manifest["agent"]["specialization"]

    def fingerprint(self) -> str:
        """
        Generate a SHA256 fingerprint of the manifest.

        This is used for signing and verifying agent identity.

        Returns:
            str: SHA256 fingerprint in format "sha256:hex"

        Example:
            >>> manifest = AgentManifest(...)
            >>> fingerprint = manifest.fingerprint()
            >>> print(fingerprint)  # "sha256:abc123def456..."
        """
        # Create a canonical JSON representation for hashing
        canonical = json.dumps(self.manifest, sort_keys=True, separators=(",", ":"))
        digest = sha256(canonical.encode()).hexdigest()
        return f"sha256:{digest}"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert manifest to dictionary.

        Returns:
            dict: The manifest dictionary
        """
        return self.manifest

    def to_json(self, pretty: bool = True) -> str:
        """
        Convert manifest to JSON string.

        Args:
            pretty: If True, format with indentation. If False, compact.

        Returns:
            str: JSON-serialized manifest

        Example:
            >>> manifest = AgentManifest(...)
            >>> json_str = manifest.to_json()
            >>> # Can be written to disk or transmitted
        """
        indent = 2 if pretty else None
        return json.dumps(self.manifest, indent=indent)

    def _validate(self) -> None:
        """
        Validate the manifest against STEWARD_JSON_SCHEMA.

        For now, this is a basic sanity check.
        Future: Integrate with jsonschema library for full validation.

        Raises:
            ValueError: If required fields are missing
        """
        # Check required top-level keys
        required_keys = ["steward_version", "agent", "credentials", "capabilities"]
        for key in required_keys:
            if key not in self.manifest:
                raise ValueError(f"Missing required field: {key}")

        # Check required agent fields
        required_agent_fields = [
            "id",
            "name",
            "version",
            "class",
            "specialization",
            "status",
        ]
        agent = self.manifest.get("agent", {})
        for field in required_agent_fields:
            if field not in agent:
                raise ValueError(f"Missing required agent field: {field}")


class AgentRegistry:
    """
    In-memory registry of agent manifests.

    This is the kernel's registry for STEWARD manifests. It provides:
    - Storage of manifests indexed by agent_id
    - Lookup by agent_id or capability
    - Serialization to/from disk
    - Integration with kernel boot

    Design:
    - Simple dict-based storage (Level 1)
    - Can be persisted to disk (data/registry/)
    - Can be queried by agent_id or capability
    - Thread-safe for reads (single-threaded kernel OK for now)

    Example:
        >>> registry = AgentRegistry()
        >>> manifest = AgentManifest(...)
        >>> registry.register(manifest)
        >>> found = registry.lookup("agent-id")
        >>> agents_with_cap = registry.find_by_capability("read_file")
    """

    def __init__(self):
        """
        Initialize an empty registry.

        Example:
            >>> registry = AgentRegistry()
        """
        self.manifests: dict[str, AgentManifest] = {}
        logger.debug("Initialized AgentRegistry")

    def register(self, manifest: AgentManifest) -> None:
        """
        Register an agent manifest.

        Args:
            manifest: The AgentManifest to register

        Raises:
            ValueError: If an agent with the same ID is already registered

        Example:
            >>> registry = AgentRegistry()
            >>> manifest = AgentManifest(...)
            >>> registry.register(manifest)
        """
        agent_id = manifest.agent_id

        if agent_id in self.manifests:
            raise ValueError(f"Agent '{agent_id}' is already registered")

        self.manifests[agent_id] = manifest
        logger.info(f"Registered manifest for {agent_id}")

    def lookup(self, agent_id: str) -> AgentManifest | None:
        """
        Look up a manifest by agent ID.

        Args:
            agent_id: The agent's unique identifier

        Returns:
            AgentManifest if found, None otherwise

        Example:
            >>> manifest = registry.lookup("specialist-planning")
            >>> if manifest:
            ...     print(manifest.capabilities)
        """
        return self.manifests.get(agent_id)

    def find_by_capability(self, capability: str) -> list[AgentManifest]:
        """
        Find all agents with a specific capability.

        Args:
            capability: The capability name to search for

        Returns:
            list[AgentManifest]: All manifests with the capability

        Example:
            >>> agents = registry.find_by_capability("read_file")
            >>> print(f"Found {len(agents)} agents with read_file capability")
        """
        return [
            manifest for manifest in self.manifests.values() if capability in manifest.capabilities
        ]

    def list_all(self) -> list[AgentManifest]:
        """
        Return all registered manifests.

        Returns:
            list[AgentManifest]: All registered manifests

        Example:
            >>> all_agents = registry.list_all()
            >>> print(f"Total agents: {len(all_agents)}")
        """
        return list(self.manifests.values())

    def to_dict(self) -> dict[str, dict[str, Any]]:
        """
        Export registry as nested dict (agent_id → manifest dict).

        Returns:
            dict: Mapping of agent_id to manifest dicts

        Example:
            >>> registry_dict = registry.to_dict()
            >>> json.dump(registry_dict, open("registry.json", "w"))
        """
        return {agent_id: manifest.to_dict() for agent_id, manifest in self.manifests.items()}


def generate_manifest_for_agent(agent: VibeAgent) -> AgentManifest:
    """
    Convenience function: Generate and wrap a manifest for an agent.

    This is the main entry point for converting an agent to STEWARD format.

    Args:
        agent: The VibeAgent to generate a manifest for

    Returns:
        AgentManifest: The validated manifest

    Example:
        >>> agent = SimpleLLMAgent(...)
        >>> manifest = generate_manifest_for_agent(agent)
        >>> print(manifest.to_json())
    """
    generator = ManifestGenerator()
    manifest_dict = generator.generate(agent)
    return AgentManifest(manifest_dict)
