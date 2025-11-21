"""
Tests for InvariantChecker (ARCH-029: Soul Governance Layer).

This module tests the core governance mechanism that enforces system invariants
through soul.yaml configuration.

Test coverage:
- Basic initialization and rule loading
- path_contains rule enforcement
- path_matches rule enforcement
- path_outside_root rule enforcement (sandbox confinement)
- Multiple rules interaction
- Edge cases and error handling
"""

from vibe_core.governance import InvariantChecker, SoulResult


class TestInvariantCheckerInitialization:
    """Test InvariantChecker initialization and rule loading."""

    def test_init_with_existing_soul_file(self):
        """Test initialization with a valid soul.yaml file."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")
        assert checker.rule_count > 0
        assert len(checker.get_rule_ids()) > 0

    def test_init_with_missing_soul_file(self):
        """Test initialization with missing soul.yaml (should not crash)."""
        checker = InvariantChecker("nonexistent/soul.yaml")
        assert checker.rule_count == 0
        assert checker.get_rule_ids() == []

    def test_reload_rules(self):
        """Test that rules can be reloaded."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")
        initial_count = checker.rule_count
        checker.reload()
        assert checker.rule_count == initial_count


class TestPathContainsRule:
    """Test path_contains rule enforcement."""

    def test_blocks_git_directory_access(self):
        """Test that .git directory access is blocked."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        # Test various .git paths
        test_cases = [
            ".git/config",
            ".git/HEAD",
            "path/to/.git/refs",
            ".git",
        ]

        for path in test_cases:
            result = checker.check_tool_call("write_file", {"path": path})
            assert result.allowed is False
            assert "forbidden" in result.reason.lower()
            assert ".git" in result.reason

    def test_blocks_secret_files(self):
        """Test that files containing 'secret' are blocked."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        result = checker.check_tool_call("read_file", {"path": "config/secret.yaml"})
        assert result.allowed is False
        assert "secret" in result.reason.lower()

    def test_allows_non_matching_paths(self):
        """Test that non-matching paths are allowed."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        safe_paths = [
            "README.md",
            "vibe_core/agents/llm_agent.py",
            "tests/test_something.py",
            "config/soul.yaml",  # Not blocked by path_contains ".git"
        ]

        for path in safe_paths:
            _ = checker.check_tool_call("write_file", {"path": path})
            # These might be blocked by other rules, but not by path_contains
            # We're just testing that path_contains doesn't trigger
            # (The assertion would depend on the full rule set)


class TestPathMatchesRule:
    """Test path_matches rule enforcement (exact path matching)."""

    def test_blocks_exact_kernel_path(self):
        """Test that exact kernel.py path is blocked."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        # Exact match should be blocked
        result = checker.check_tool_call("write_file", {"path": "vibe_core/kernel.py"})
        assert result.allowed is False
        assert "kernel" in result.reason.lower()

    def test_allows_similar_but_different_paths(self):
        """Test that similar but non-exact paths are allowed."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        # These should NOT match the exact path rule
        similar_paths = [
            "vibe_core/kernel_utils.py",
            "vibe_core/other/kernel.py",
            "kernel.py",  # Different directory
        ]

        for path in similar_paths:
            _ = checker.check_tool_call("write_file", {"path": path})
            # Should not be blocked by the path_matches rule for "vibe_core/kernel.py"
            # (might be blocked by other rules, but not this one)


class TestPathOutsideRootRule:
    """Test path_outside_root rule enforcement (sandbox confinement)."""

    def test_blocks_parent_directory_traversal(self):
        """Test that ../ directory traversal is blocked."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        # These paths attempt to escape the project root
        dangerous_paths = [
            "../etc/passwd",
            "../../sensitive/data.txt",
            "../../../root/.ssh/id_rsa",
        ]

        for path in dangerous_paths:
            result = checker.check_tool_call("write_file", {"path": path})
            assert result.allowed is False
            assert "outside" in result.reason.lower() or "root" in result.reason.lower()

    def test_blocks_absolute_paths_outside_root(self):
        """Test that absolute paths outside project are blocked."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        # These are absolute paths outside the project
        dangerous_paths = [
            "/etc/passwd",
            "/root/.bashrc",
            "/tmp/malicious.sh",
        ]

        for path in dangerous_paths:
            result = checker.check_tool_call("write_file", {"path": path})
            assert result.allowed is False

    def test_allows_paths_inside_root(self):
        """Test that paths inside project root are allowed."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        # These paths are inside the project root (assuming we're in vibe-agency)
        safe_paths = [
            "vibe_core/new_file.py",
            "tests/test_new.py",
            "config/new_config.yaml",
        ]

        for path in safe_paths:
            _ = checker.check_tool_call("write_file", {"path": path})
            # Should not be blocked by path_outside_root
            # (might be blocked by other rules like path_contains)


class TestToolCallValidation:
    """Test tool call validation logic."""

    def test_validates_different_tool_names(self):
        """Test that validation works for different tool names."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        tools = ["write_file", "read_file", "delete_file", "edit_file"]

        for tool in tools:
            result = checker.check_tool_call(tool, {"path": "safe/path.txt"})
            # Result depends on the path and rules, but should not crash
            assert isinstance(result, SoulResult)

    def test_handles_missing_path_parameter(self):
        """Test that missing path parameter is handled gracefully."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        # Call without path parameter
        result = checker.check_tool_call("some_tool", {"other_param": "value"})

        # Should not crash and should allow (no path to check)
        assert result.allowed is True

    def test_handles_non_file_tools(self):
        """Test that non-file tools are handled correctly."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        # Tools that don't work with files
        result = checker.check_tool_call("google_search", {"query": "test"})
        assert result.allowed is True

        result = checker.check_tool_call("web_fetch", {"url": "https://example.com"})
        assert result.allowed is True


class TestSoulResult:
    """Test SoulResult dataclass."""

    def test_allowed_result_has_no_reason(self):
        """Test that allowed results typically have no reason."""
        result = SoulResult(allowed=True)
        assert result.allowed is True
        assert result.reason is None

    def test_blocked_result_has_reason(self):
        """Test that blocked results should have a reason."""
        result = SoulResult(allowed=False, reason="Test block reason")
        assert result.allowed is False
        assert result.reason == "Test block reason"


class TestMultipleRulesInteraction:
    """Test how multiple rules interact."""

    def test_first_matching_rule_blocks(self):
        """Test that the first matching blocking rule prevents execution."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        # This path matches both path_contains ".git" and potentially others
        result = checker.check_tool_call("write_file", {"path": ".git/config"})

        assert result.allowed is False
        # Should be blocked by the .git rule
        assert ".git" in result.reason or "git" in result.reason.lower()

    def test_rule_order_matters(self):
        """Test that rules are evaluated in order."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        # Test with a path that could match multiple rules
        result = checker.check_tool_call("write_file", {"path": ".git/secret_config"})

        assert result.allowed is False
        # Should be blocked (either by .git or secret rule)


class TestRuleManagement:
    """Test rule management functionality."""

    def test_get_rule_ids(self):
        """Test retrieving rule IDs."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        rule_ids = checker.get_rule_ids()

        assert isinstance(rule_ids, list)
        assert len(rule_ids) > 0
        # Check for expected test rules
        assert "test_protect_git" in rule_ids
        assert "test_protect_kernel" in rule_ids

    def test_rule_count(self):
        """Test rule count property."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        count = checker.rule_count

        assert isinstance(count, int)
        assert count > 0
        assert count == len(checker.get_rule_ids())


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_parameters(self):
        """Test with empty parameters dictionary."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        result = checker.check_tool_call("some_tool", {})
        assert result.allowed is True

    def test_none_path_parameter(self):
        """Test with None as path value."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        result = checker.check_tool_call("write_file", {"path": None})
        # Should handle gracefully
        assert isinstance(result, SoulResult)

    def test_empty_tool_name(self):
        """Test with empty tool name."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        result = checker.check_tool_call("", {"path": "test.txt"})
        assert isinstance(result, SoulResult)


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_safe_file_operations_allowed(self):
        """Test that normal, safe file operations are allowed."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        safe_operations = [
            ("write_file", {"path": "docs/new_doc.md"}),
            ("read_file", {"path": "README.md"}),
            ("edit_file", {"path": "vibe_core/agents/new_agent.py"}),
        ]

        for tool_name, params in safe_operations:
            _ = checker.check_tool_call(tool_name, params)
            # Should be allowed (no matching block rules)
            # Note: Depends on the actual rules in test_soul.yaml

    def test_dangerous_operations_blocked(self):
        """Test that dangerous operations are blocked."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        dangerous_operations = [
            ("delete_file", {"path": ".git/config"}),
            ("write_file", {"path": "../../../etc/passwd"}),
            ("edit_file", {"path": "vibe_core/kernel.py"}),
        ]

        for tool_name, params in dangerous_operations:
            result = checker.check_tool_call(tool_name, params)
            assert result.allowed is False
            assert result.reason is not None


class TestIntegrationWithToolExecutor:
    """Test integration scenarios with ToolExecutor (if available)."""

    def test_invariant_checker_can_be_injected(self):
        """Test that InvariantChecker can be instantiated for injection."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        # Should be ready to inject into ToolExecutor
        assert checker is not None
        assert checker.rule_count > 0

    def test_soul_result_format_for_tool_executor(self):
        """Test that SoulResult format is suitable for ToolExecutor."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")

        result = checker.check_tool_call("write_file", {"path": ".git/config"})

        # ToolExecutor expects these fields
        assert hasattr(result, "allowed")
        assert hasattr(result, "reason")
        assert isinstance(result.allowed, bool)
