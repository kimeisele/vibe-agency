"""
Unit tests for Layer 0: System Integrity Verification

Tests the "Who watches the watchmen?" meta-layer that ensures
the regulatory framework itself has not been tampered with.

Part of: GAD-005-ADDITION Layer 0
"""

# Import functions from the scripts using importlib (scripts have hyphens in names)
import importlib.util
import os
import shutil
import tempfile
from pathlib import Path

import pytest


def load_script_module(script_name: str):
    """Load a Python script as a module (handles hyphens in filenames)."""
    script_path = Path(__file__).parent.parent / "scripts" / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(script_name.replace("-", "_"), script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load the two Layer 0 scripts
generate_module = load_script_module("generate-integrity-manifest")
verify_module = load_script_module("verify-system-integrity")

# Extract functions we need
generate_manifest = generate_module.generate_manifest
calculate_sha256 = verify_module.calculate_sha256
verify_system_integrity = verify_module.verify_system_integrity
SystemIntegrityError = verify_module.SystemIntegrityError


@pytest.fixture
def temp_workspace():
    """Create temporary workspace for testing."""
    tmpdir = tempfile.mkdtemp()
    orig_dir = os.getcwd()
    os.chdir(tmpdir)

    # Create test file structure
    os.makedirs("scripts", exist_ok=True)
    os.makedirs(".vibe", exist_ok=True)
    os.makedirs("bin", exist_ok=True)

    # Create dummy files for testing
    Path("scripts/verify-system-integrity.py").write_text("# verify script\n")
    Path("scripts/generate-integrity-manifest.py").write_text("# generate script\n")
    Path("bin/update-system-status.sh").write_text("#!/bin/bash\n# update status\n")

    yield tmpdir

    # Cleanup
    os.chdir(orig_dir)
    shutil.rmtree(tmpdir)


class TestCalculateSha256:
    """Test SHA256 checksum calculation."""

    def test_calculates_checksum_correctly(self, temp_workspace):
        """Verify SHA256 checksum is calculated correctly."""
        test_file = Path("test.txt")
        test_file.write_text("Hello, World!")

        checksum = calculate_sha256(str(test_file))

        # Expected SHA256 of "Hello, World!"
        expected = "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
        assert checksum == expected

    def test_different_content_different_checksum(self, temp_workspace):
        """Different file content produces different checksum."""
        file1 = Path("file1.txt")
        file2 = Path("file2.txt")

        file1.write_text("Content A")
        file2.write_text("Content B")

        checksum1 = calculate_sha256(str(file1))
        checksum2 = calculate_sha256(str(file2))

        assert checksum1 != checksum2


class TestGenerateManifest:
    """Test integrity manifest generation."""

    def test_manifest_generated_successfully(self, temp_workspace):
        """Manifest generation creates valid JSON file."""
        manifest = generate_manifest()

        # Check manifest structure
        assert "manifestVersion" in manifest
        assert "generatedAt" in manifest
        assert "trustedBaseline" in manifest

        # Check file was written
        assert Path(".vibe/system_integrity_manifest.json").exists()

    def test_manifest_contains_checksums(self, temp_workspace):
        """Manifest contains SHA256 checksums for critical files."""
        manifest = generate_manifest()

        baseline = manifest["trustedBaseline"]

        # Should have categories
        assert "scripts" in baseline or "configs" in baseline or "core" in baseline

        # Each entry should have checksum
        for category in baseline.values():
            for file_spec in category.values():
                assert "sha256" in file_spec
                assert len(file_spec["sha256"]) == 64  # SHA256 is 64 hex chars

    def test_manifest_includes_metadata(self, temp_workspace):
        """Manifest includes file metadata (path, purpose, critical flag)."""
        manifest = generate_manifest()

        baseline = manifest["trustedBaseline"]

        for category in baseline.values():
            for file_spec in category.values():
                assert "path" in file_spec
                assert "purpose" in file_spec
                assert "critical" in file_spec


class TestVerifyIntegrity:
    """Test system integrity verification."""

    def test_clean_system_passes_verification(self, temp_workspace):
        """System with unmodified files passes integrity check."""
        # Generate baseline manifest
        generate_manifest()

        # Verify integrity
        success, report = verify_system_integrity()

        assert success is True
        assert len(report["failed"]) == 0
        assert len(report["missing"]) == 0
        assert len(report["verified"]) > 0

    def test_tampered_file_fails_verification(self, temp_workspace):
        """System with tampered file fails integrity check."""
        # Generate baseline manifest
        generate_manifest()

        # Tamper with a critical file
        Path("scripts/verify-system-integrity.py").write_text("# TAMPERED\n")

        # Verify integrity
        success, report = verify_system_integrity()

        assert success is False
        assert len(report["failed"]) > 0

        # Check failure details
        failure = report["failed"][0]
        assert "scripts/verify-system-integrity.py" in failure["file"]
        assert "expected" in failure
        assert "actual" in failure
        assert failure["expected"] != failure["actual"]

    def test_missing_file_fails_verification(self, temp_workspace):
        """System with missing critical file fails integrity check."""
        # Generate baseline manifest
        generate_manifest()

        # Remove a critical file
        Path("scripts/verify-system-integrity.py").unlink()

        # Verify integrity
        success, report = verify_system_integrity()

        assert success is False
        assert len(report["missing"]) > 0

        # Check missing file details
        missing = report["missing"][0]
        assert "scripts/verify-system-integrity.py" in missing["file"]

    def test_missing_manifest_raises_error(self, temp_workspace):
        """Verification fails gracefully when manifest is missing."""
        # Don't generate manifest

        with pytest.raises(SystemIntegrityError) as exc_info:
            verify_system_integrity()

        assert "manifest not found" in str(exc_info.value).lower()


class TestIntegrityReportFormat:
    """Test integrity report formatting."""

    def test_report_has_required_keys(self, temp_workspace):
        """Integrity report contains required keys."""
        generate_manifest()
        success, report = verify_system_integrity()

        assert "verified" in report
        assert "failed" in report
        assert "missing" in report

        # All values should be lists
        assert isinstance(report["verified"], list)
        assert isinstance(report["failed"], list)
        assert isinstance(report["missing"], list)

    def test_failed_report_includes_critical_flag(self, temp_workspace):
        """Failed files report includes critical flag from manifest."""
        generate_manifest()

        # Tamper with file
        Path("scripts/verify-system-integrity.py").write_text("# TAMPERED\n")

        success, report = verify_system_integrity()

        # Check critical flag is present
        failure = report["failed"][0]
        assert "critical" in failure


class TestAttackSimulation:
    """Simulate attacks to verify Layer 0 protection."""

    def test_attack_modify_verification_script(self, temp_workspace):
        """Layer 0 detects modification to verification script itself."""
        generate_manifest()

        # Attacker modifies the verification script
        Path("scripts/verify-system-integrity.py").write_text(
            "# Bypass integrity check\ndef verify_system_integrity(): return True, {}\n"
        )

        # Layer 0 should detect this
        success, report = verify_system_integrity()
        assert success is False

    def test_attack_modify_manifest_generator(self, temp_workspace):
        """Layer 0 detects modification to manifest generator."""
        generate_manifest()

        # Attacker modifies the generator to create fake manifests
        Path("scripts/generate-integrity-manifest.py").write_text("# Fake generator\n")

        # Layer 0 should detect this
        success, report = verify_system_integrity()
        assert success is False


# Summary test to verify all requirements
def test_layer0_requirements_met(temp_workspace):
    """
    Meta-test: Verify Layer 0 meets all requirements.

    Requirements:
    1. ✅ Generate integrity manifest with SHA256 checksums
    2. ✅ Verify system integrity against manifest
    3. ✅ Detect tampered files (checksum mismatch)
    4. ✅ Detect missing files
    5. ✅ Detect tampering of Layer 0 scripts themselves
    6. ✅ Graceful error handling (missing manifest)
    """
    # Requirement 1: Generate manifest
    generate_manifest()
    assert Path(".vibe/system_integrity_manifest.json").exists()

    # Requirement 2: Verify integrity
    success, report = verify_system_integrity()
    assert success is True

    # Requirement 3: Detect tampered files
    Path("scripts/verify-system-integrity.py").write_text("# TAMPERED\n")
    success, report = verify_system_integrity()
    assert success is False
    assert len(report["failed"]) > 0

    # Requirement 4: Detect missing files
    generate_manifest()  # Regenerate clean manifest
    Path("scripts/generate-integrity-manifest.py").unlink()
    success, report = verify_system_integrity()
    assert success is False
    assert len(report["missing"]) > 0

    # Requirement 5: Self-protection (verified above in test_attack_* tests)
    # Requirement 6: Graceful errors (verified in test_missing_manifest_raises_error)

    print("✅ Layer 0 requirements verified")
