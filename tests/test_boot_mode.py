"""
Tests for vibe-cli boot mode and playbook routing.

Tests cover:
- Playbook registry loading
- Keyword-based intent matching (Tier 1)
- Context injection from playbook YAML
- Boot prompt display
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import yaml


class TestPlaybookRegistry:
    """Tests for playbook registry loading and structure."""

    def test_registry_exists(self):
        """Verify playbook registry file exists."""
        registry_path = project_root / "docs" / "playbook" / "_registry.yaml"
        assert registry_path.exists(), "Playbook registry should exist"

    def test_registry_valid_yaml(self):
        """Verify registry is valid YAML."""
        registry_path = project_root / "docs" / "playbook" / "_registry.yaml"

        with open(registry_path) as f:
            registry = yaml.safe_load(f)

        assert registry is not None, "Registry should be valid YAML"
        assert isinstance(registry, dict), "Registry should be a dictionary"

    def test_registry_has_routes(self):
        """Verify registry has routes defined."""
        registry_path = project_root / "docs" / "playbook" / "_registry.yaml"

        with open(registry_path) as f:
            registry = yaml.safe_load(f)

        assert "routes" in registry, "Registry should have routes"
        assert len(registry["routes"]) > 0, "Registry should have at least one route"

    def test_registry_routes_structure(self):
        """Verify each route has required fields."""
        registry_path = project_root / "docs" / "playbook" / "_registry.yaml"

        with open(registry_path) as f:
            registry = yaml.safe_load(f)

        routes = registry.get("routes", [])

        for route in routes:
            assert "name" in route, f"Route should have 'name': {route}"
            assert "description" in route, f"Route should have 'description': {route}"
            assert "intent_patterns" in route, f"Route should have 'intent_patterns': {route}"
            assert "target_chain" in route, f"Route should have 'target_chain': {route}"

            # Verify intent_patterns is a list
            assert isinstance(route["intent_patterns"], list), (
                f"intent_patterns should be a list: {route['name']}"
            )
            assert len(route["intent_patterns"]) > 0, (
                f"intent_patterns should not be empty: {route['name']}"
            )


class TestKeywordMatching:
    """Tests for Tier 1 keyword-based playbook matching."""

    @pytest.fixture
    def registry(self):
        """Load registry for tests."""
        registry_path = project_root / "docs" / "playbook" / "_registry.yaml"
        with open(registry_path) as f:
            return yaml.safe_load(f)

    def _match_playbook(self, user_input: str, registry: dict):
        """Simple keyword matching (same as vibe-cli implementation)."""
        routes = registry.get("routes", [])
        user_lower = user_input.lower()

        for route in routes:
            patterns = route.get("intent_patterns", [])
            for pattern in patterns:
                if pattern.lower() in user_lower:
                    return route

        return None

    def test_match_restaurant_app(self, registry):
        """Test matching restaurant app intent."""
        matched = self._match_playbook("I want to build a restaurant app", registry)

        assert matched is not None, "Should match restaurant_app route"
        assert matched["name"] == "restaurant_app"

    def test_match_session_resume(self, registry):
        """Test matching session resume intent."""
        matched = self._match_playbook("continue work", registry)

        assert matched is not None, "Should match session_resume route"
        assert matched["name"] == "session_resume"

    def test_match_status_check(self, registry):
        """Test matching status check intent."""
        matched = self._match_playbook("show me progress", registry)

        assert matched is not None, "Should match status_check route"
        assert matched["name"] == "status_check"

    def test_match_healthcare(self, registry):
        """Test matching healthcare app intent."""
        matched = self._match_playbook("healthcare app for patient records", registry)

        assert matched is not None, "Should match healthcare_app route"
        assert matched["name"] == "healthcare_app"

    def test_match_ecommerce(self, registry):
        """Test matching e-commerce app intent."""
        matched = self._match_playbook("I need an online store", registry)

        assert matched is not None, "Should match ecommerce_app route"
        assert matched["name"] == "ecommerce_app"

    def test_no_match_random_input(self, registry):
        """Test that random input doesn't match any route."""
        matched = self._match_playbook("xyz random input abc", registry)

        assert matched is None, "Random input should not match any route"

    def test_case_insensitive_matching(self, registry):
        """Test that matching is case insensitive."""
        matched1 = self._match_playbook("RESTAURANT APP", registry)
        matched2 = self._match_playbook("restaurant app", registry)
        matched3 = self._match_playbook("Restaurant App", registry)

        assert matched1 is not None
        assert matched2 is not None
        assert matched3 is not None
        assert matched1["name"] == matched2["name"] == matched3["name"]


class TestPlaybookFiles:
    """Tests for playbook YAML files referenced in registry."""

    @pytest.fixture
    def registry(self):
        """Load registry for tests."""
        registry_path = project_root / "docs" / "playbook" / "_registry.yaml"
        with open(registry_path) as f:
            return yaml.safe_load(f)

    def test_restaurant_playbook_exists(self, registry):
        """Verify restaurant playbook file exists."""
        # Find restaurant route
        routes = registry.get("routes", [])
        restaurant = next((r for r in routes if r["name"] == "restaurant_app"), None)

        assert restaurant is not None, "restaurant_app route should exist"

        # Check file exists
        target_chain = restaurant["target_chain"]
        playbook_path = project_root / "docs" / "playbook" / target_chain

        assert playbook_path.exists(), f"Playbook file should exist: {playbook_path}"

    def test_restaurant_playbook_valid_yaml(self):
        """Verify restaurant playbook is valid YAML with expected structure."""
        playbook_path = (
            project_root / "docs" / "playbook" / "domains" / "hospitality" / "restaurant.yaml"
        )

        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)

        assert playbook is not None, "Playbook should be valid YAML"
        assert "metadata" in playbook, "Playbook should have metadata"
        assert "target_agent" in playbook, "Playbook should specify target_agent"

        # Check metadata
        metadata = playbook.get("metadata", {})
        assert "domain" in metadata, "Metadata should specify domain"
        assert metadata["domain"] == "hospitality"

    def test_restaurant_playbook_has_pre_questions(self):
        """Verify restaurant playbook has pre-enrichment questions."""
        playbook_path = (
            project_root / "docs" / "playbook" / "domains" / "hospitality" / "restaurant.yaml"
        )

        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)

        pre_enrichment = playbook.get("pre_enrichment", {})
        pre_questions = pre_enrichment.get("pre_questions", [])

        assert len(pre_questions) > 0, "Playbook should have pre-questions"

        # Verify question structure
        for q in pre_questions:
            assert "question" in q, "Each pre-question should have 'question' field"

    def test_restaurant_playbook_has_quality_gates(self):
        """Verify restaurant playbook has quality gates."""
        playbook_path = (
            project_root / "docs" / "playbook" / "domains" / "hospitality" / "restaurant.yaml"
        )

        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)

        quality_gates = playbook.get("quality_gates", [])

        assert len(quality_gates) > 0, "Playbook should have quality gates"

        # Verify gate structure
        for gate in quality_gates:
            assert "gate" in gate, "Each quality gate should have 'gate' field"
            assert "description" in gate, "Each quality gate should have 'description' field"


class TestBootPromptDocumentation:
    """Tests for boot prompt documentation."""

    def test_boot_prompt_doc_exists(self):
        """Verify STEWARD_BOOT_PROMPT.md exists."""
        doc_path = project_root / "docs" / "playbook" / "STEWARD_BOOT_PROMPT.md"
        assert doc_path.exists(), "Boot prompt documentation should exist"

    def test_boot_prompt_doc_has_content(self):
        """Verify boot prompt documentation has content."""
        doc_path = project_root / "docs" / "playbook" / "STEWARD_BOOT_PROMPT.md"

        with open(doc_path) as f:
            content = f.read()

        assert len(content) > 100, "Documentation should have substantial content"

        # Check for key sections
        assert "# STEWARD Boot Prompt" in content
        assert "User Prompt" in content
        assert "Playbook Routing" in content
        assert "Integration Architecture" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
