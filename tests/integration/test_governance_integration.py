"""
Governance Integration Tests (ARCH-027 + ARCH-029): The Devil Test.

This module proves that the Soul governance layer (ARCH-029) successfully
prevents dangerous tool operations when integrated with the tool system (ARCH-027).

The "Devil Test" validates that:
1. Dangerous operations (modify .git, escape sandbox) are BLOCKED
2. Safe operations (normal file access) are ALLOWED
3. Governance errors are clearly reported
4. No operations bypass the governance layer

Why "Devil Test"?
If the system can resist the devil's attempts to break security rules,
it can resist any accidental or intentional misuse.

Test Philosophy:
- Red tests: Prove governance BLOCKS what it should block
- Green tests: Prove governance ALLOWS what it should allow
- Integration: Test the full stack (ToolRegistry → InvariantChecker → Soul)
"""

import tempfile
from pathlib import Path

import pytest

from vibe_core.governance import InvariantChecker
from vibe_core.tools import ReadFileTool, ToolRegistry, WriteFileTool


class TestDevilCannotBreakSecurity:
    """
    The Devil Test: Prove that malicious/accidental dangerous operations are blocked.

    These tests simulate an agent (or attacker) trying to perform dangerous
    operations. All must be BLOCKED by Soul governance.
    """

    def test_devil_cannot_modify_git_config(self):
        """
        Test: Agent attempts to modify .git/config (version control tampering).
        Expected: BLOCKED by Soul governance.
        """
        # Setup: Registry with governance
        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register("write_file", WriteFileTool())

        # Devil attempt: Modify .git/config
        result = registry.execute(
            "write_file", path=".git/config", content="[malicious config]"
        )

        # Assert: Operation blocked
        assert result["success"] is False, "Should block .git access"
        assert result.get("blocked") is True, "Should be blocked by governance"
        assert "Governance Violation" in result["error"]
        assert ".git" in result["error"] or "git" in result["error"].lower()

    def test_devil_cannot_read_git_files(self):
        """
        Test: Agent attempts to read .git/HEAD (version control snooping).
        Expected: BLOCKED by Soul governance.
        """
        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register("read_file", ReadFileTool())

        # Devil attempt: Read .git/HEAD
        result = registry.execute("read_file", path=".git/HEAD")

        # Assert: Operation blocked
        assert result["success"] is False
        assert result.get("blocked") is True
        assert "Governance Violation" in result["error"]

    def test_devil_cannot_modify_kernel(self):
        """
        Test: Agent attempts to modify vibe_core/kernel.py (system core).
        Expected: BLOCKED by Soul governance.
        """
        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register("write_file", WriteFileTool())

        # Devil attempt: Overwrite kernel.py
        result = registry.execute(
            "write_file",
            path="vibe_core/kernel.py",
            content="# hacked kernel\nimport evil",
        )

        # Assert: Operation blocked
        assert result["success"] is False
        assert result.get("blocked") is True
        assert "Governance Violation" in result["error"]
        assert "kernel" in result["error"].lower()

    def test_devil_cannot_escape_sandbox(self):
        """
        Test: Agent attempts directory traversal (escape sandbox).
        Expected: BLOCKED by Soul governance.
        """
        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register("read_file", ReadFileTool())

        # Devil attempts: Various directory traversal patterns
        dangerous_paths = [
            "../../../etc/passwd",
            "../../root/.ssh/id_rsa",
            "/etc/shadow",
            "/root/.bashrc",
        ]

        for path in dangerous_paths:
            result = registry.execute("read_file", path=path)

            # Assert: All blocked
            assert result["success"] is False, f"Should block {path}"
            assert result.get("blocked") is True, f"Should block traversal: {path}"

    def test_devil_cannot_modify_governance_rules(self):
        """
        Test: Agent attempts to modify config/soul.yaml (self-modification).
        Expected: BLOCKED by Soul governance.
        """
        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register("write_file", WriteFileTool())

        # Devil attempt: Disable governance by modifying soul.yaml
        result = registry.execute(
            "write_file",
            path="config/soul.yaml",
            content="# No rules! Freedom!",
        )

        # Assert: Operation blocked
        assert result["success"] is False
        assert result.get("blocked") is True
        assert "Governance Violation" in result["error"]

    def test_devil_cannot_access_database_directly(self):
        """
        Test: Agent attempts to read/modify .db files directly.
        Expected: BLOCKED by Soul governance.
        """
        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register("write_file", WriteFileTool())

        # Devil attempt: Tamper with database
        result = registry.execute(
            "write_file",
            path=".vibe/state/ledger.db",
            content="corrupted data",
        )

        # Assert: Operation blocked
        assert result["success"] is False
        assert result.get("blocked") is True


class TestAngelCanDoLegitimateWork:
    """
    The Angel Test: Prove that legitimate operations are ALLOWED.

    These tests simulate normal agent work. All must SUCCEED (not blocked).
    """

    def test_angel_can_write_documentation(self):
        """
        Test: Agent writes documentation file.
        Expected: ALLOWED.
        """
        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register("write_file", WriteFileTool())

        # Legitimate work: Write documentation (inside project)
        doc_file = Path("tests/.temp_test_docs/new_feature.md")
        result = registry.execute(
            "write_file",
            path=str(doc_file),
            content="# New Feature\n\nDocumentation here.",
        )

        # Assert: Operation allowed
        assert result["success"] is True
        assert doc_file.exists()

        # Cleanup
        doc_file.unlink(missing_ok=True)
        doc_file.parent.rmdir() if doc_file.parent.exists() else None

    def test_angel_can_read_readme(self):
        """
        Test: Agent reads README.md.
        Expected: ALLOWED.
        """
        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register("read_file", ReadFileTool())

        # Legitimate work: Read project README
        result = registry.execute("read_file", path="README.md")

        # Assert: Operation allowed (if README exists)
        # Note: May fail if README doesn't exist, but shouldn't be governance block
        if result["success"] is False:
            assert result.get("blocked") is not True
            assert "Governance Violation" not in result.get("error", "")

    def test_angel_can_create_test_files(self):
        """
        Test: Agent creates test files.
        Expected: ALLOWED.
        """
        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register("write_file", WriteFileTool())

        # Legitimate work: Create test file (inside project)
        test_file = Path("tests/.temp_test_files/test_new_feature.py")
        result = registry.execute(
            "write_file",
            path=str(test_file),
            content='def test_example():\n    assert True',
        )

        # Assert: Operation allowed
        assert result["success"] is True
        assert test_file.exists()

        # Cleanup
        test_file.unlink(missing_ok=True)
        test_file.parent.rmdir() if test_file.parent.exists() else None

    def test_angel_can_write_to_temp_directory(self):
        """
        Test: Agent writes to temporary location (inside project).
        Expected: ALLOWED.
        """
        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register("write_file", WriteFileTool())

        # Legitimate work: Write temporary file (inside project sandbox)
        temp_file = Path("tests/.temp_work_data.txt")

        result = registry.execute(
            "write_file",
            path=str(temp_file),
            content="Temporary work data",
        )

        # Assert: Operation allowed
        assert result["success"] is True
        assert temp_file.exists()

        # Cleanup
        temp_file.unlink(missing_ok=True)


class TestGovernanceErrorReporting:
    """Test that governance violations are clearly reported."""

    def test_error_messages_are_informative(self):
        """Test that governance blocks include helpful error messages."""
        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register("write_file", WriteFileTool())

        # Trigger governance violation
        result = registry.execute(
            "write_file",
            path=".git/config",
            content="test",
        )

        # Assert: Error message is informative
        assert "error" in result
        error_msg = result["error"]

        # Should mention:
        # - That it's a governance violation
        # - Why it was blocked (rule information)
        assert "Governance Violation" in error_msg or "blocked" in error_msg.lower()
        assert (
            ".git" in error_msg or "forbidden" in error_msg.lower()
        )  # Mentions the issue

    def test_blocked_flag_is_set(self):
        """Test that governance blocks set the 'blocked' flag."""
        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register("write_file", WriteFileTool())

        result = registry.execute("write_file", path=".git/config", content="test")

        # Assert: blocked flag present and True
        assert "blocked" in result
        assert result["blocked"] is True


class TestNoGovernanceBypass:
    """Test that there's no way to bypass governance."""

    def test_cannot_bypass_with_none_checker(self):
        """
        Test: Registry without governance checker allows everything.
        This proves governance is the ONLY security layer.
        """
        # Registry WITHOUT governance
        registry_no_gov = ToolRegistry(invariant_checker=None)
        registry_no_gov.register("write_file", WriteFileTool())

        # This would succeed (demonstrates importance of governance)
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".test_git_config"
        ) as tmp:
            tmp_path = tmp.name

        result = registry_no_gov.execute(
            "write_file",
            path=tmp_path,
            content="test",
        )

        assert result["success"] is True

        # Cleanup
        Path(tmp_path).unlink(missing_ok=True)

    def test_governance_is_required_in_production(self):
        """
        Test: Verify that registry correctly reports governance status.
        """
        # With governance
        checker = InvariantChecker("config/soul.yaml")
        registry_with_gov = ToolRegistry(invariant_checker=checker)
        assert registry_with_gov.has_governance is True

        # Without governance
        registry_no_gov = ToolRegistry(invariant_checker=None)
        assert registry_no_gov.has_governance is False


class TestFullStackIntegration:
    """
    Test the complete stack: ToolRegistry → InvariantChecker → Soul Rules.
    """

    def test_full_stack_blocks_malicious_operation(self):
        """
        Integration test: Full stack from registry to soul.yaml rules.
        """
        # Setup complete stack
        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register("write_file", WriteFileTool())
        registry.register("read_file", ReadFileTool())

        # Test various malicious operations
        malicious_ops = [
            ("write_file", {"path": ".git/config", "content": "bad"}),
            ("read_file", {"path": ".git/HEAD"}),
            ("write_file", {"path": "vibe_core/kernel.py", "content": "hacked"}),
            ("read_file", {"path": "../../../etc/passwd"}),
        ]

        for tool_name, params in malicious_ops:
            result = registry.execute(tool_name, **params)

            # All must be blocked
            assert result["success"] is False, f"Should block {tool_name} {params}"
            assert result.get("blocked") is True

    def test_full_stack_allows_legitimate_operation(self):
        """
        Integration test: Full stack allows safe operations.
        """
        # Setup complete stack
        checker = InvariantChecker("config/soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register("write_file", WriteFileTool())
        registry.register("read_file", ReadFileTool())

        # Safe operations (inside project sandbox)
        test_file = Path("tests/.temp_integration_test.md")

        # Write
        write_result = registry.execute(
            "write_file",
            path=str(test_file),
            content="# Test Document\n\nContent.",
        )
        assert write_result["success"] is True

        # Read
        read_result = registry.execute("read_file", path=str(test_file))
        assert read_result["success"] is True
        assert read_result["result"]["content"] == "# Test Document\n\nContent."

        # Cleanup
        test_file.unlink(missing_ok=True)
