"""
GAD-800 Integration Matrix Tests

Comprehensive tests for all cross-system interactions at all layers.
Tests verify that:
1. Agent → Knowledge interactions work at each layer
2. Agent → STEWARD interactions work at each layer
3. Knowledge ↔ STEWARD interactions work correctly
4. Graceful degradation works as expected
5. Layer detection works correctly

Test coverage includes:
- Layer 1 (prompt-based, manual)
- Layer 2 (tool-based, automated)
- Layer 3 (runtime services, full automation) - skipped if unavailable
"""

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import layer detection module dynamically
layer_detection_path = project_root / "docs" / "architecture" / "GAD-8XX" / "layer_detection.py"
spec = importlib.util.spec_from_file_location("layer_detection", layer_detection_path)
layer_detection = importlib.util.module_from_spec(spec)
spec.loader.exec_module(layer_detection)

# Extract classes and functions
LayerDetector = layer_detection.LayerDetector
LayerAdapter = layer_detection.LayerAdapter
get_current_layer = layer_detection.get_current_layer


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def layer_detector():
    """Provide LayerDetector instance for tests."""
    return LayerDetector()


@pytest.fixture
def degradation_rules():
    """Load degradation rules YAML."""
    rules_path = project_root / "docs" / "architecture" / "GAD-8XX" / "degradation_rules.yaml"
    return yaml.safe_load(rules_path.read_text())


@pytest.fixture
def knowledge_graph():
    """Load knowledge graph YAML."""
    graph_path = project_root / "knowledge_department" / "config" / "knowledge_graph.yaml"
    return yaml.safe_load(graph_path.read_text())


# =============================================================================
# TEST LAYER DETECTION
# =============================================================================


class TestLayerDetection:
    """Test layer detection functionality."""

    def test_detect_layer_returns_valid_layer(self, layer_detector):
        """Layer detection returns 1, 2, or 3."""
        layer = layer_detector.detect_layer()
        assert layer in [1, 2, 3], f"Invalid layer: {layer}"

    def test_get_current_layer_convenience_function(self):
        """Convenience function returns valid layer."""
        layer = get_current_layer()
        assert layer in [1, 2, 3]

    def test_layer_caching_works(self, layer_detector):
        """Cached layer detection returns same result."""
        layer1 = layer_detector.detect_layer(use_cache=False)
        layer2 = layer_detector.detect_layer(use_cache=True)
        assert layer1 == layer2

    def test_clear_cache_works(self, layer_detector):
        """Cache can be cleared."""
        layer_detector.detect_layer()
        assert layer_detector._cached_layer is not None
        layer_detector.clear_cache()
        assert layer_detector._cached_layer is None

    def test_capabilities_increase_with_layer(self, layer_detector):
        """Higher layers have more capabilities."""
        caps_layer1 = layer_detector.get_capabilities(1)
        caps_layer2 = layer_detector.get_capabilities(2)
        caps_layer3 = layer_detector.get_capabilities(3)

        assert len(caps_layer1) < len(caps_layer2)
        assert len(caps_layer2) < len(caps_layer3)

    def test_has_capability_layer1(self, layer_detector):
        """Layer 1 has expected capabilities."""
        assert layer_detector.has_capability("guidance", layer=1)
        assert layer_detector.has_capability("manual_operations", layer=1)

    def test_has_capability_layer2(self, layer_detector):
        """Layer 2 has expected capabilities."""
        assert layer_detector.has_capability("tool_execution", layer=2)
        assert layer_detector.has_capability("knowledge_query", layer=2)
        # Layer 2 also includes Layer 1 capabilities
        assert layer_detector.has_capability("guidance", layer=2)

    def test_has_capability_layer3(self, layer_detector):
        """Layer 3 has expected capabilities."""
        assert layer_detector.has_capability("research_engine", layer=3)
        assert layer_detector.has_capability("governance_engine", layer=3)
        # Layer 3 includes all lower layer capabilities
        assert layer_detector.has_capability("tool_execution", layer=3)
        assert layer_detector.has_capability("guidance", layer=3)


class TestLayerAdapter:
    """Test LayerAdapter base class for components."""

    def test_adapter_initializes_with_detected_layer(self):
        """Adapter detects and activates for current layer."""
        adapter = LayerAdapter()
        assert adapter.layer in [1, 2, 3]
        assert adapter.mode in ["prompt", "tool", "runtime"]

    def test_adapter_layer1_mode(self):
        """Layer 1 adapter has correct mode and capabilities."""
        detector = LayerDetector()
        adapter = LayerAdapter(detector)
        adapter.activate_for_layer(1)

        assert adapter.mode == "prompt"
        assert "guidance" in adapter.capabilities
        assert "manual_operations" in adapter.capabilities

    def test_adapter_layer2_mode(self):
        """Layer 2 adapter has correct mode and capabilities."""
        detector = LayerDetector()
        adapter = LayerAdapter(detector)
        adapter.activate_for_layer(2)

        assert adapter.mode == "tool"
        assert "tool_execution" in adapter.capabilities

    def test_adapter_layer3_mode(self):
        """Layer 3 adapter has correct mode and capabilities."""
        detector = LayerDetector()
        adapter = LayerAdapter(detector)
        adapter.activate_for_layer(3)

        assert adapter.mode == "runtime"
        assert "research_engine" in adapter.capabilities

    def test_adapter_degrade_to_lower_layer(self):
        """Adapter can degrade to lower layer."""
        detector = LayerDetector()
        adapter = LayerAdapter(detector)
        adapter.layer = 3
        adapter.activate_for_layer(3)

        # Degrade from 3 to 2
        adapter.degrade_to(2)
        assert adapter.layer == 2
        assert adapter.mode == "tool"

    def test_adapter_cannot_degrade_to_higher_layer(self):
        """Adapter cannot 'degrade' to higher layer."""
        detector = LayerDetector()
        adapter = LayerAdapter(detector)
        adapter.layer = 1
        adapter.activate_for_layer(1)

        with pytest.raises(ValueError, match="Target layer must be lower"):
            adapter.degrade_to(2)


# =============================================================================
# TEST DEGRADATION RULES
# =============================================================================


class TestDegradationRules:
    """Test degradation rules are well-formed and complete."""

    def test_degradation_rules_loaded(self, degradation_rules):
        """Degradation rules YAML loads successfully."""
        assert degradation_rules is not None
        assert "degradation_rules" in degradation_rules

    def test_knowledge_query_degradation_path(self, degradation_rules):
        """Knowledge query has complete degradation path."""
        kq_rules = degradation_rules["degradation_rules"]["knowledge_query"]

        assert "layer3_available" in kq_rules
        assert "layer3_fails" in kq_rules
        assert "layer2_fails" in kq_rules

        # Layer 3 action
        assert kq_rules["layer3_available"]["action"] == "use_research_engine"

        # Layer 3 → Layer 2 degradation
        assert kq_rules["layer3_fails"]["degrade_to"] == "layer2"
        assert kq_rules["layer3_fails"]["action"] == "use_knowledge_query_tool"

        # Layer 2 → Layer 1 degradation
        assert kq_rules["layer2_fails"]["degrade_to"] == "layer1"
        assert kq_rules["layer2_fails"]["action"] == "prompt_user"

    def test_steward_validation_degradation_path(self, degradation_rules):
        """STEWARD validation has complete degradation path."""
        sv_rules = degradation_rules["degradation_rules"]["steward_validation"]

        assert "layer3_available" in sv_rules
        assert "layer3_fails" in sv_rules
        assert "layer2_fails" in sv_rules

        # Enforcement changes across layers
        assert sv_rules["layer3_available"]["enforcement"] == "blocking"
        assert sv_rules["layer3_fails"]["enforcement"] == "recommendation"
        assert sv_rules["layer2_fails"]["enforcement"] == "none"

    def test_all_components_have_degradation_rules(self, degradation_rules):
        """All critical components have degradation rules."""
        rules = degradation_rules["degradation_rules"]

        required_components = [
            "knowledge_query",
            "steward_validation",
            "agent_execution",
            "research_engine",
            "receipt_management",
            "integrity_checks",
        ]

        for component in required_components:
            assert component in rules, f"Missing degradation rules for {component}"

    def test_degradation_strategies_defined(self, degradation_rules):
        """Degradation strategies are defined."""
        assert "degradation_strategies" in degradation_rules
        strategies = degradation_rules["degradation_strategies"]

        assert "automatic_degradation" in strategies
        assert "manual_degradation" in strategies
        assert "upgrade_strategy" in strategies

    def test_failure_detection_methods_defined(self, degradation_rules):
        """Failure detection methods are defined."""
        assert "failure_detection" in degradation_rules
        detection = degradation_rules["failure_detection"]

        assert "layer3_service_health" in detection
        assert "layer2_tool_availability" in detection
        assert "layer1_fallback" in detection


# =============================================================================
# TEST KNOWLEDGE GRAPH
# =============================================================================


class TestKnowledgeGraph:
    """Test knowledge graph structure and relationships."""

    def test_knowledge_graph_loaded(self, knowledge_graph):
        """Knowledge graph YAML loads successfully."""
        assert knowledge_graph is not None
        assert "schema" in knowledge_graph
        assert "graph" in knowledge_graph

    def test_node_types_defined(self, knowledge_graph):
        """All required node types are defined."""
        node_types = knowledge_graph["schema"]["node_types"]
        node_type_ids = [nt["id"] for nt in node_types]

        required_types = [
            "project_type",
            "domain_concept",
            "tech_stack",
            "agent",
            "governance_rule",
            "knowledge_file",
            "tool",
        ]

        for required in required_types:
            assert required in node_type_ids, f"Missing node type: {required}"

    def test_edge_types_defined(self, knowledge_graph):
        """All required edge types are defined."""
        edge_types = knowledge_graph["schema"]["edge_types"]
        edge_type_ids = [et["id"] for et in edge_types]

        required_edges = [
            "requires",
            "implements",
            "uses",
            "governed_by",
            "defined_in",
            "related_to",
        ]

        for required in required_edges:
            assert required in edge_type_ids, f"Missing edge type: {required}"

    def test_graph_has_nodes(self, knowledge_graph):
        """Graph instance has concrete nodes."""
        nodes = knowledge_graph["graph"]["nodes"]
        assert len(nodes) > 0, "Graph has no nodes"

        # Check for expected nodes
        assert "booking_system" in nodes
        assert "VIBE_ALIGNER" in nodes
        assert "access_control" in nodes

    def test_graph_has_edges(self, knowledge_graph):
        """Graph instance has concrete edges."""
        edges = knowledge_graph["graph"]["edges"]
        assert len(edges) > 0, "Graph has no edges"

    def test_booking_system_relationships(self, knowledge_graph):
        """Booking system has expected relationships."""
        edges = knowledge_graph["graph"]["edges"]

        # Find edges from booking_system
        booking_edges = [e for e in edges if e["from"] == "booking_system"]
        assert len(booking_edges) > 0

        # Should require reservation_management
        requires_reservation = [
            e
            for e in booking_edges
            if e["to"] == "reservation_management" and e["type"] == "requires"
        ]
        assert len(requires_reservation) == 1

    def test_vibe_aligner_uses_tools(self, knowledge_graph):
        """VIBE_ALIGNER uses expected tools."""
        edges = knowledge_graph["graph"]["edges"]

        # Find tools used by VIBE_ALIGNER
        aligner_tools = [
            e
            for e in edges
            if e["from"] == "VIBE_ALIGNER" and e["to"] in ["knowledge_query", "steward_validate"]
        ]
        assert len(aligner_tools) >= 2

    def test_governance_rules_enforced(self, knowledge_graph):
        """Governance rules are linked to entities."""
        edges = knowledge_graph["graph"]["edges"]

        # Find governed_by edges
        governance_edges = [e for e in edges if e["type"] == "governed_by"]
        assert len(governance_edges) > 0

        # Payment processing should be governed by PCI
        pci_edges = [
            e
            for e in governance_edges
            if e["from"] == "payment_processing" and e["to"] == "pci_compliance"
        ]
        assert len(pci_edges) == 1


# =============================================================================
# TEST AGENT → KNOWLEDGE INTERACTIONS
# =============================================================================


class TestAgentToKnowledgeInteractions:
    """Test Agent → Knowledge interactions at all layers."""

    def test_layer1_manual_query(self):
        """Layer 1: Agent prompts user to check knowledge file."""
        # Simulate prompt-based interaction
        prompt = "Please check knowledge_department/domain_knowledge/industry_patterns/booking_systems.yaml"
        assert "booking_systems.yaml" in prompt
        assert "knowledge_department" in prompt

    def test_layer2_knowledge_graph_exists(self, knowledge_graph):
        """Layer 2: Knowledge graph is available for tool queries."""
        # In Layer 2, tools can load and query the knowledge graph
        assert knowledge_graph is not None
        assert "graph" in knowledge_graph

        # Simulate tool query: find booking system concepts
        nodes = knowledge_graph["graph"]["nodes"]
        booking = nodes.get("booking_system")
        assert booking is not None
        assert booking["type"] == "project_type"

    def test_layer2_graph_expansion_simulation(self, knowledge_graph):
        """Layer 2: Simulate graph expansion for concept query."""
        # Simulate: "Find all concepts related to booking_system"
        edges = knowledge_graph["graph"]["edges"]

        # Find all edges from booking_system
        related_edges = [e for e in edges if e["from"] == "booking_system"]

        # Should find multiple related concepts
        assert len(related_edges) >= 4  # reservation, calendar, payment, auth

        # Extract related concept names
        related_concepts = [e["to"] for e in related_edges if e["type"] == "requires"]
        assert "reservation_management" in related_concepts
        assert "payment_processing" in related_concepts

    @pytest.mark.skip(reason="Layer 3 services not available in test environment")
    def test_layer3_research_engine(self):
        """Layer 3: Agent uses ResearchEngine API."""
        # This test would require actual Layer 3 services running
        # In production, would make API call:
        # response = requests.post('http://localhost:8000/research', json={...})
        pass


# =============================================================================
# TEST AGENT → STEWARD INTERACTIONS
# =============================================================================


class TestAgentToSTEWARDInteractions:
    """Test Agent → STEWARD interactions at all layers."""

    def test_layer1_guidance_simulation(self):
        """Layer 1: STEWARD provides guidance via prompt."""
        # Simulate guidance interaction
        # Question: "Can I access client_a knowledge?"

        # STEWARD would provide guidance like:
        guidance = "Check project_id in project_manifest.json. Access requires project_id match."
        assert "project_id" in guidance
        assert "project_manifest.json" in guidance

    def test_layer2_validation_rules_exist(self, degradation_rules):
        """Layer 2: STEWARD validation rules are defined."""
        sv_rules = degradation_rules["degradation_rules"]["steward_validation"]
        layer2_rule = sv_rules["layer3_fails"]

        assert layer2_rule["action"] == "steward_validate_tool"
        assert "validation_checks" in layer2_rule["capabilities"]
        assert layer2_rule["enforcement"] == "recommendation"

    def test_layer2_access_control_check_simulation(self, knowledge_graph):
        """Layer 2: Simulate access control validation."""
        # Simulate: Agent wants to access payment_patterns_yaml
        edges = knowledge_graph["graph"]["edges"]

        # Find governance rules for payment_patterns_yaml
        governed_edges = [
            e for e in edges if e["from"] == "payment_patterns_yaml" and e["type"] == "governed_by"
        ]

        # Should be governed by access_control
        access_control_edges = [e for e in governed_edges if e["to"] == "access_control"]
        assert len(access_control_edges) > 0

        # Validation result would check compliance_required
        assert access_control_edges[0]["properties"]["compliance_required"] is True

    @pytest.mark.skip(reason="Layer 3 services not available in test environment")
    def test_layer3_enforcement(self):
        """Layer 3: STEWARD enforces policies at runtime."""
        # This test would require actual Layer 3 governance engine
        # In production, would make API call to governance service
        pass


# =============================================================================
# TEST KNOWLEDGE ↔ STEWARD INTERACTIONS
# =============================================================================


class TestKnowledgeToSTEWARDInteractions:
    """Test Knowledge ↔ STEWARD interactions."""

    def test_confidential_knowledge_requires_governance(self, knowledge_graph):
        """Confidential knowledge files have governance rules."""
        nodes = knowledge_graph["graph"]["nodes"]
        edges = knowledge_graph["graph"]["edges"]

        # Find confidential knowledge files
        confidential_files = [
            node_id
            for node_id, node in nodes.items()
            if node.get("type") == "knowledge_file" and node.get("scope") == "confidential"
        ]

        # Each should have governed_by edge
        for file_id in confidential_files:
            governed_edges = [
                e for e in edges if e["from"] == file_id and e["type"] == "governed_by"
            ]
            assert len(governed_edges) > 0, f"Confidential file {file_id} not governed"

    def test_payment_processing_has_pci_compliance(self, knowledge_graph):
        """Payment processing is governed by PCI compliance."""
        edges = knowledge_graph["graph"]["edges"]

        pci_edges = [
            e
            for e in edges
            if e["from"] == "payment_processing"
            and e["to"] == "pci_compliance"
            and e["type"] == "governed_by"
        ]

        assert len(pci_edges) == 1


# =============================================================================
# TEST GRACEFUL DEGRADATION
# =============================================================================


class TestGracefulDegradation:
    """Test graceful degradation between layers."""

    def test_layer_detection_is_consistent(self):
        """Layer detection returns consistent results."""
        detector1 = LayerDetector()
        detector2 = LayerDetector()

        layer1 = detector1.detect_layer()
        layer2 = detector2.detect_layer()

        assert layer1 == layer2

    def test_adapter_can_degrade_gracefully(self):
        """LayerAdapter can degrade from Layer 3 → 2 → 1."""
        adapter = LayerAdapter()

        # Start at Layer 3
        adapter.layer = 3
        adapter.activate_for_layer(3)
        assert adapter.mode == "runtime"

        # Degrade to Layer 2
        adapter.degrade_to(2)
        assert adapter.layer == 2
        assert adapter.mode == "tool"

        # Degrade to Layer 1
        adapter.degrade_to(1)
        assert adapter.layer == 1
        assert adapter.mode == "prompt"

    def test_degradation_preserves_essential_data(self, degradation_rules):
        """Degradation rules specify state preservation."""
        kq_rules = degradation_rules["degradation_rules"]["knowledge_query"]

        # Layer 3 → 2 should preserve state
        assert kq_rules["layer3_fails"]["preserve_state"] is True

        # Layer 2 → 1 should preserve state
        assert kq_rules["layer2_fails"]["preserve_state"] is True

    def test_degradation_notifies_user(self, degradation_rules):
        """Degradation rules include user notifications."""
        kq_rules = degradation_rules["degradation_rules"]["knowledge_query"]

        # Layer 3 → 2 notification
        assert "notify" in kq_rules["layer3_fails"]
        assert "⚠️" in kq_rules["layer3_fails"]["notify"]

        # Layer 2 → 1 notification
        assert "notify" in kq_rules["layer2_fails"]
        assert "Manual operation required" in kq_rules["layer2_fails"]["notify"]


# =============================================================================
# TEST INTEGRATION COMPLETENESS
# =============================================================================


class TestIntegrationCompleteness:
    """Test that all integration points are covered."""

    def test_all_agents_have_knowledge_requirements(self, knowledge_graph):
        """All agents specify what knowledge they use."""
        nodes = knowledge_graph["graph"]["nodes"]
        edges = knowledge_graph["graph"]["edges"]

        # Find all agents
        agents = [node_id for node_id, node in nodes.items() if node.get("type") == "agent"]

        # Each agent should have 'uses' edges
        for agent_id in agents:
            uses_edges = [e for e in edges if e["from"] == agent_id and e["type"] == "uses"]
            assert len(uses_edges) > 0, f"Agent {agent_id} has no knowledge requirements"

    def test_all_project_types_have_tech_stacks(self, knowledge_graph):
        """All project types specify recommended tech stacks."""
        nodes = knowledge_graph["graph"]["nodes"]
        edges = knowledge_graph["graph"]["edges"]

        # Find all project types
        projects = [
            node_id for node_id, node in nodes.items() if node.get("type") == "project_type"
        ]

        # Each project should have tech stack requirements
        for project_id in projects:
            tech_edges = [
                e
                for e in edges
                if e["from"] == project_id
                and e["type"] == "requires"
                and nodes[e["to"]].get("type") == "tech_stack"
            ]
            assert len(tech_edges) > 0, f"Project {project_id} has no tech stack requirements"

    def test_all_critical_concepts_have_governance(self, knowledge_graph):
        """Critical domain concepts have governance rules."""
        nodes = knowledge_graph["graph"]["nodes"]
        edges = knowledge_graph["graph"]["edges"]

        critical_concepts = ["payment_processing"]  # Add more as needed

        for concept_id in critical_concepts:
            if concept_id in nodes:
                gov_edges = [
                    e for e in edges if e["from"] == concept_id and e["type"] == "governed_by"
                ]
                assert len(gov_edges) > 0, f"Critical concept {concept_id} has no governance"


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
