"""
Tests for STEWARD Protocol identity and manifest generation (ARCH-026 Phase 3).

This test suite validates:
1. ManifestGenerator: Converts VibeAgent → steward.json
2. AgentManifest: Validates and wraps STEWARD manifests
3. AgentRegistry: In-memory registry of manifests
4. Integration: Kernel.get_agent_manifest() and capability discovery
"""

import json
import sys
from unittest.mock import MagicMock

import pytest

# Mock yaml module before importing agents (which require yaml)
sys.modules["yaml"] = MagicMock()

# Now import agents
from tests.mocks.llm import MockLLMProvider
from vibe_core.agents.llm_agent import SimpleLLMAgent
from vibe_core.identity import (
    AgentManifest,
    AgentRegistry,
    ManifestGenerator,
    generate_manifest_for_agent,
)
from vibe_core.kernel import VibeKernel


class TestManifestGenerator:
    """Tests for ManifestGenerator class."""

    def test_init(self):
        """Test ManifestGenerator initialization."""
        gen = ManifestGenerator(issuing_org="test-org", version="1.0.0")
        assert gen.issuing_org == "test-org"
        assert gen.protocol_version == "1.0.0"

    def test_generate_llm_agent(self):
        """Test generating manifest for SimpleLLMAgent."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)

        gen = ManifestGenerator()
        manifest = gen.generate(agent)

        # Check structure
        assert manifest["steward_version"] == "1.0.0"
        assert manifest["agent"]["id"] == "test-agent"
        assert manifest["agent"]["class"] == "orchestration_operator"
        assert manifest["agent"]["specialization"] == "cognitive_orchestration"
        assert manifest["agent"]["status"] == "active"

        # Check credentials
        assert "mandate" in manifest["credentials"]
        assert "constraints" in manifest["credentials"]
        assert "prime_directive" in manifest["credentials"]

        # Check capabilities
        assert "operations" in manifest["capabilities"]
        assert "interfaces" in manifest["capabilities"]

        # Check governance
        assert manifest["governance"]["principal"] == "vibe-agency-core-team"
        assert manifest["governance"]["transparency"] == "public"


    def test_generate_invalid_agent(self):
        """Test that non-VibeAgent raises TypeError."""
        gen = ManifestGenerator()

        class NotAnAgent:
            pass

        with pytest.raises(TypeError):
            gen.generate(NotAnAgent())  # type: ignore

    def test_humanize_agent_id(self):
        """Test agent ID humanization."""
        assert ManifestGenerator._humanize_agent_id("specialist-planning") == "Specialist Planning"
        assert ManifestGenerator._humanize_agent_id("test-agent") == "Test Agent"
        assert ManifestGenerator._humanize_agent_id("assistant") == "Assistant"


class TestAgentManifest:
    """Tests for AgentManifest wrapper class."""

    def test_init_valid_manifest(self):
        """Test AgentManifest initialization with valid manifest."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)

        gen = ManifestGenerator()
        manifest_dict = gen.generate(agent)
        manifest = AgentManifest(manifest_dict)

        assert manifest.agent_id == "test-agent"
        assert manifest.version == "1.0.0"

    def test_init_invalid_manifest(self):
        """Test that invalid manifest raises ValueError."""
        # Missing required field
        invalid = {"agent": {"id": "test"}}  # Missing steward_version, etc.

        with pytest.raises(ValueError, match="Missing required field"):
            AgentManifest(invalid)

    def test_agent_id_property(self):
        """Test agent_id property."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="my-agent", provider=provider)

        manifest = generate_manifest_for_agent(agent)
        assert manifest.agent_id == "my-agent"

    def test_agent_class_property(self):
        """Test agent_class property."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test", provider=provider)

        manifest = generate_manifest_for_agent(agent)
        assert manifest.agent_class == "orchestration_operator"

    def test_capabilities_property(self):
        """Test capabilities property extracts operation names."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test", provider=provider)

        manifest = generate_manifest_for_agent(agent)
        capabilities = manifest.capabilities

        # Should include at least "process" operation
        assert isinstance(capabilities, list)
        assert "process" in capabilities

    def test_fingerprint(self):
        """Test fingerprint generation."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test", provider=provider)

        manifest = generate_manifest_for_agent(agent)
        fingerprint = manifest.fingerprint()

        # Check format: sha256:hexstring
        assert fingerprint.startswith("sha256:")
        assert len(fingerprint) == 71  # "sha256:" (7) + 64 hex chars

    def test_fingerprint_deterministic(self):
        """Test that fingerprint is deterministic for identical dictionaries."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test", provider=provider)

        gen = ManifestGenerator()
        manifest_dict = gen.generate(agent)

        # Create two identical manifests from the same dict
        manifest1 = AgentManifest(manifest_dict)
        manifest2 = AgentManifest(manifest_dict)

        # Same manifest dict should have same fingerprint
        assert manifest1.fingerprint() == manifest2.fingerprint()

    def test_to_dict(self):
        """Test conversion to dict."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test", provider=provider)

        manifest = generate_manifest_for_agent(agent)
        manifest_dict = manifest.to_dict()

        assert isinstance(manifest_dict, dict)
        assert manifest_dict["steward_version"] == "1.0.0"

    def test_to_json(self):
        """Test conversion to JSON string."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test", provider=provider)

        manifest = generate_manifest_for_agent(agent)
        json_str = manifest.to_json()

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["steward_version"] == "1.0.0"

    def test_to_json_compact(self):
        """Test compact JSON generation."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test", provider=provider)

        manifest = generate_manifest_for_agent(agent)
        json_str = manifest.to_json(pretty=False)

        # Compact JSON should not have indentation
        assert "\n" not in json_str or json_str.count("\n") < 5


class TestAgentRegistry:
    """Tests for AgentRegistry class."""

    def test_init(self):
        """Test AgentRegistry initialization."""
        registry = AgentRegistry()
        assert len(registry.list_all()) == 0

    def test_register(self):
        """Test registering a manifest."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)
        manifest = generate_manifest_for_agent(agent)

        registry = AgentRegistry()
        registry.register(manifest)

        assert len(registry.list_all()) == 1

    def test_register_duplicate_error(self):
        """Test that duplicate registration raises error."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)
        manifest = generate_manifest_for_agent(agent)

        registry = AgentRegistry()
        registry.register(manifest)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(manifest)

    def test_lookup(self):
        """Test looking up a manifest by agent_id."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)
        manifest = generate_manifest_for_agent(agent)

        registry = AgentRegistry()
        registry.register(manifest)

        found = registry.lookup("test-agent")
        assert found is not None
        assert found.agent_id == "test-agent"

    def test_lookup_not_found(self):
        """Test lookup returns None for non-existent agent."""
        registry = AgentRegistry()
        found = registry.lookup("non-existent")
        assert found is None

    def test_find_by_capability(self):
        """Test finding agents by capability."""
        provider = MockLLMProvider()

        # Create agents
        agent1 = SimpleLLMAgent(agent_id="agent-1", provider=provider)
        agent2 = SimpleLLMAgent(agent_id="agent-2", provider=provider)

        manifest1 = generate_manifest_for_agent(agent1)
        manifest2 = generate_manifest_for_agent(agent2)

        registry = AgentRegistry()
        registry.register(manifest1)
        registry.register(manifest2)

        # Find by capability
        found = registry.find_by_capability("process")
        assert len(found) == 2

    def test_find_by_capability_not_found(self):
        """Test find_by_capability returns empty list for non-existent capability."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test", provider=provider)
        manifest = generate_manifest_for_agent(agent)

        registry = AgentRegistry()
        registry.register(manifest)

        found = registry.find_by_capability("non-existent-capability")
        assert found == []

    def test_list_all(self):
        """Test listing all registered manifests."""
        provider = MockLLMProvider()

        agent1 = SimpleLLMAgent(agent_id="agent-1", provider=provider)
        agent2 = SimpleLLMAgent(agent_id="agent-2", provider=provider)

        manifest1 = generate_manifest_for_agent(agent1)
        manifest2 = generate_manifest_for_agent(agent2)

        registry = AgentRegistry()
        registry.register(manifest1)
        registry.register(manifest2)

        all_manifests = registry.list_all()
        assert len(all_manifests) == 2

    def test_to_dict(self):
        """Test exporting registry to dict."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)
        manifest = generate_manifest_for_agent(agent)

        registry = AgentRegistry()
        registry.register(manifest)

        registry_dict = registry.to_dict()

        assert isinstance(registry_dict, dict)
        assert "test-agent" in registry_dict
        assert registry_dict["test-agent"]["steward_version"] == "1.0.0"


class TestKernelIntegration:
    """Tests for Kernel integration with manifest registry."""

    def test_kernel_has_manifest_registry(self):
        """Test that kernel has manifest_registry."""
        kernel = VibeKernel(":memory:")
        assert hasattr(kernel, "manifest_registry")
        assert isinstance(kernel.manifest_registry, AgentRegistry)

    def test_kernel_boot_generates_manifests(self):
        """Test that kernel.boot() generates manifests for registered agents."""
        kernel = VibeKernel(":memory:")

        # Register an agent
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)
        kernel.register_agent(agent)

        # Boot kernel
        kernel.boot()

        # Check that manifest was registered
        assert kernel.manifest_registry.lookup("test-agent") is not None

    def test_get_agent_manifest(self):
        """Test kernel.get_agent_manifest()."""
        kernel = VibeKernel(":memory:")

        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)
        kernel.register_agent(agent)
        kernel.boot()

        manifest_dict = kernel.get_agent_manifest("test-agent")

        assert manifest_dict is not None
        assert manifest_dict["agent"]["id"] == "test-agent"
        assert manifest_dict["agent"]["class"] == "orchestration_operator"

    def test_get_agent_manifest_not_found(self):
        """Test get_agent_manifest returns None for non-existent agent."""
        kernel = VibeKernel(":memory:")
        kernel.boot()

        manifest = kernel.get_agent_manifest("non-existent")
        assert manifest is None

    def test_find_agents_by_capability(self):
        """Test kernel.find_agents_by_capability()."""
        kernel = VibeKernel(":memory:")

        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)
        kernel.register_agent(agent)
        kernel.boot()

        found = kernel.find_agents_by_capability("process")

        assert len(found) == 1
        assert found[0]["agent"]["id"] == "test-agent"

    def test_agent_get_manifest_method(self):
        """Test agent.get_manifest() method."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test-agent", provider=provider)

        manifest_dict = agent.get_manifest()

        assert isinstance(manifest_dict, dict)
        assert manifest_dict["agent"]["id"] == "test-agent"
        assert manifest_dict["steward_version"] == "1.0.0"


class TestManifestValidity:
    """Tests to ensure manifests are valid per STEWARD spec."""

    def test_manifest_has_required_top_level_keys(self):
        """Test manifest has all required top-level keys."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test", provider=provider)
        manifest = generate_manifest_for_agent(agent)

        required_keys = ["steward_version", "agent", "credentials", "capabilities"]
        for key in required_keys:
            assert key in manifest.to_dict(), f"Missing required key: {key}"

    def test_manifest_agent_section_completeness(self):
        """Test agent section has all required fields."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test", provider=provider)
        manifest = generate_manifest_for_agent(agent)

        agent_section = manifest.to_dict()["agent"]
        required_fields = ["id", "name", "version", "class", "specialization", "status"]

        for field in required_fields:
            assert field in agent_section, f"Missing agent field: {field}"

    def test_manifest_credentials_completeness(self):
        """Test credentials section has required structure."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test", provider=provider)
        manifest = generate_manifest_for_agent(agent)

        creds = manifest.to_dict()["credentials"]
        required_keys = ["mandate", "constraints", "prime_directive"]

        for key in required_keys:
            assert key in creds, f"Missing credentials field: {key}"

    def test_manifest_capabilities_completeness(self):
        """Test capabilities section has required structure."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test", provider=provider)
        manifest = generate_manifest_for_agent(agent)

        caps = manifest.to_dict()["capabilities"]
        required_keys = ["interfaces", "operations"]

        for key in required_keys:
            assert key in caps, f"Missing capabilities field: {key}"

    def test_operations_have_required_fields(self):
        """Test each operation has required fields."""
        provider = MockLLMProvider()
        agent = SimpleLLMAgent(agent_id="test", provider=provider)
        manifest = generate_manifest_for_agent(agent)

        operations = manifest.to_dict()["capabilities"]["operations"]
        required_fields = ["name", "input_schema", "output_schema"]

        for op in operations:
            for field in required_fields:
                assert field in op, f"Operation {op.get('name')} missing field: {field}"
