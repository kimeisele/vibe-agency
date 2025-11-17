"""Test canonical schemas validate existing state files.

These tests ensure that:
1. All schemas are valid JSON Schema Draft 07
2. All existing state files validate against their canonical schemas
3. Schemas catch invalid data (negative tests)
"""

import json
from pathlib import Path

import jsonschema
import pytest
from jsonschema.validators import Draft7Validator


@pytest.fixture
def repo_root():
    """Repository root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def project_manifest_schema(repo_root):
    """Load project_manifest.schema.json."""
    schema_path = repo_root / "config" / "schemas" / "project_manifest.schema.json"
    with schema_path.open() as f:
        return json.load(f)


@pytest.fixture
def session_handoff_schema(repo_root):
    """Load session_handoff.schema.json."""
    schema_path = repo_root / "config" / "schemas" / "session_handoff.schema.json"
    with schema_path.open() as f:
        return json.load(f)


class TestSchemaValidity:
    """Test that schemas themselves are valid JSON Schema Draft 07."""

    def test_project_manifest_schema_is_valid(self, project_manifest_schema):
        """project_manifest.schema.json is valid JSON Schema Draft 07."""
        Draft7Validator.check_schema(project_manifest_schema)

    def test_session_handoff_schema_is_valid(self, session_handoff_schema):
        """session_handoff.schema.json is valid JSON Schema Draft 07."""
        Draft7Validator.check_schema(session_handoff_schema)


class TestProjectManifestValidation:
    """Test that all existing project_manifest.json files validate."""

    @pytest.fixture
    def project_manifests(self, repo_root):
        """Find all project_manifest.json files."""
        return list(repo_root.glob("workspaces/*/project_manifest.json"))

    def test_all_manifests_validate(
        self, project_manifests, project_manifest_schema
    ):
        """All existing project_manifest.json files validate against schema."""
        validator = Draft7Validator(project_manifest_schema)
        errors = []

        for manifest_path in project_manifests:
            with manifest_path.open() as f:
                manifest_data = json.load(f)

            validation_errors = list(validator.iter_errors(manifest_data))
            if validation_errors:
                errors.append(
                    (
                        manifest_path.relative_to(manifest_path.parent.parent.parent),
                        validation_errors,
                    )
                )

        if errors:
            error_msg = "Schema validation failed for:\n"
            for path, errs in errors:
                error_msg += f"\n{path}:\n"
                for err in errs:
                    error_msg += f"  - {err.message} (at {'.'.join(map(str, err.path))})\n"
            pytest.fail(error_msg)

    def test_manifest_count(self, project_manifests):
        """Verify we found expected number of manifests."""
        # Should match the audit report count (7 files)
        assert len(project_manifests) >= 7, (
            f"Expected at least 7 manifests, found {len(project_manifests)}"
        )


class TestSessionHandoffValidation:
    """Test that session handoff file validates."""

    def test_session_handoff_validates(self, repo_root, session_handoff_schema):
        """The .session_handoff.json file validates against schema."""
        handoff_path = repo_root / ".session_handoff.json"
        assert handoff_path.exists(), "No .session_handoff.json found"

        with handoff_path.open() as f:
            handoff_data = json.load(f)

        validator = Draft7Validator(session_handoff_schema)
        errors = list(validator.iter_errors(handoff_data))

        if errors:
            error_msg = "Session handoff validation failed:\n"
            for err in errors:
                error_msg += (
                    f"  - {err.message} (at {'.'.join(map(str, err.path))})\n"
                )
            pytest.fail(error_msg)


class TestProjectManifestNegative:
    """Test that schema catches invalid project manifests."""

    def test_rejects_missing_required_field(self, project_manifest_schema):
        """Schema rejects manifest missing required field."""
        invalid_manifest = {
            "apiVersion": "agency.os/v1alpha1",
            "kind": "Project",
            # Missing 'metadata' (required)
            "spec": {"vibe": {}},
            "status": {
                "projectPhase": "PLANNING",
                "lastUpdate": "2025-11-17T00:00:00Z",
                "message": "Test",
            },
            "artifacts": {},
        }

        with pytest.raises(jsonschema.ValidationError, match="'metadata'.*required"):
            jsonschema.validate(invalid_manifest, project_manifest_schema)

    def test_rejects_invalid_project_phase(self, project_manifest_schema):
        """Schema rejects invalid projectPhase enum value."""
        invalid_manifest = {
            "apiVersion": "agency.os/v1alpha1",
            "kind": "Project",
            "metadata": {
                "projectId": "test",
                "name": "Test",
                "description": "Test",
                "owner": "test@example.com",
                "createdAt": "2025-11-17T00:00:00Z",
                "lastUpdatedAt": "2025-11-17T00:00:00Z",
            },
            "spec": {"vibe": {}},
            "status": {
                "projectPhase": "INVALID_PHASE",  # Invalid enum
                "lastUpdate": "2025-11-17T00:00:00Z",
                "message": "Test",
            },
            "artifacts": {},
        }

        with pytest.raises(jsonschema.ValidationError, match="'INVALID_PHASE' is not one of"):
            jsonschema.validate(invalid_manifest, project_manifest_schema)

    def test_rejects_negative_budget(self, project_manifest_schema):
        """Schema rejects negative budget values."""
        invalid_manifest = {
            "apiVersion": "agency.os/v1alpha1",
            "kind": "Project",
            "metadata": {
                "projectId": "test",
                "name": "Test",
                "description": "Test",
                "owner": "test@example.com",
                "createdAt": "2025-11-17T00:00:00Z",
                "lastUpdatedAt": "2025-11-17T00:00:00Z",
            },
            "spec": {"vibe": {}},
            "status": {
                "projectPhase": "PLANNING",
                "lastUpdate": "2025-11-17T00:00:00Z",
                "message": "Test",
            },
            "artifacts": {},
            "budget": {
                "max_cost_usd": -100.0,  # Negative value
                "current_cost_usd": 0.0,
                "alert_threshold": 0.8,
            },
        }

        with pytest.raises(jsonschema.ValidationError, match="-100.*minimum"):
            jsonschema.validate(invalid_manifest, project_manifest_schema)

    def test_accepts_flexible_vibe_fields(self, project_manifest_schema):
        """Schema accepts arbitrary fields in spec.vibe (flexible)."""
        valid_manifest = {
            "apiVersion": "agency.os/v1alpha1",
            "kind": "Project",
            "metadata": {
                "projectId": "test",
                "name": "Test",
                "description": "Test",
                "owner": "test@example.com",
                "createdAt": "2025-11-17T00:00:00Z",
                "lastUpdatedAt": "2025-11-17T00:00:00Z",
            },
            "spec": {
                "vibe": {
                    # Arbitrary fields should be accepted
                    "custom_field": "value",
                    "another_field": 123,
                    "nested": {"deep": "value"},
                }
            },
            "status": {
                "projectPhase": "PLANNING",
                "lastUpdate": "2025-11-17T00:00:00Z",
                "message": "Test",
            },
            "artifacts": {},
        }

        # Should not raise
        jsonschema.validate(valid_manifest, project_manifest_schema)


class TestSessionHandoffNegative:
    """Test that schema catches invalid session handoffs."""

    def test_rejects_missing_layer(self, session_handoff_schema):
        """Schema rejects handoff missing required layer."""
        invalid_handoff = {
            "_schema_version": "2.0_4layer",
            "_token_budget": 450,
            "_optimization": "Test",
            "layer0_bedrock": {
                "from": "Test",
                "date": "2025-11-17",
                "state": "complete",
                "blocker": None,
            },
            # Missing 'layer1_runtime' (required)
            "layer2_detail": {
                "completed": [],
                "key_decisions": [],
                "warnings": [],
                "next_steps_detail": [],
            },
        }

        with pytest.raises(jsonschema.ValidationError, match="'layer1_runtime'.*required"):
            jsonschema.validate(invalid_handoff, session_handoff_schema)

    def test_rejects_invalid_state(self, session_handoff_schema):
        """Schema rejects invalid layer0_bedrock.state enum value."""
        invalid_handoff = {
            "_schema_version": "2.0_4layer",
            "_token_budget": 450,
            "_optimization": "Test",
            "layer0_bedrock": {
                "from": "Test",
                "date": "2025-11-17",
                "state": "invalid_state",  # Invalid enum
                "blocker": None,
            },
            "layer1_runtime": {
                "completed_summary": "Test",
                "todos": [],
                "critical_files": [],
            },
            "layer2_detail": {
                "completed": [],
                "key_decisions": [],
                "warnings": [],
                "next_steps_detail": [],
            },
        }

        with pytest.raises(jsonschema.ValidationError, match="'invalid_state' is not one of"):
            jsonschema.validate(invalid_handoff, session_handoff_schema)

    def test_rejects_negative_token_budget(self, session_handoff_schema):
        """Schema rejects negative token budget."""
        invalid_handoff = {
            "_schema_version": "2.0_4layer",
            "_token_budget": -100,  # Negative value
            "_optimization": "Test",
            "layer0_bedrock": {
                "from": "Test",
                "date": "2025-11-17",
                "state": "complete",
                "blocker": None,
            },
            "layer1_runtime": {
                "completed_summary": "Test",
                "todos": [],
                "critical_files": [],
            },
            "layer2_detail": {
                "completed": [],
                "key_decisions": [],
                "warnings": [],
                "next_steps_detail": [],
            },
        }

        with pytest.raises(jsonschema.ValidationError, match="-100.*minimum"):
            jsonschema.validate(invalid_handoff, session_handoff_schema)


class TestArtifactMetadata:
    """Test artifact metadata standardization."""

    def test_artifact_requires_path(self, project_manifest_schema):
        """Artifact metadata requires 'path' field."""
        invalid_manifest = {
            "apiVersion": "agency.os/v1alpha1",
            "kind": "Project",
            "metadata": {
                "projectId": "test",
                "name": "Test",
                "description": "Test",
                "owner": "test@example.com",
                "createdAt": "2025-11-17T00:00:00Z",
                "lastUpdatedAt": "2025-11-17T00:00:00Z",
            },
            "spec": {"vibe": {}},
            "status": {
                "projectPhase": "PLANNING",
                "lastUpdate": "2025-11-17T00:00:00Z",
                "message": "Test",
            },
            "artifacts": {
                "planning": {
                    "blueprint": {
                        # Missing 'path' (required)
                        "created_at": "2025-11-17T00:00:00Z"
                    }
                }
            },
        }

        with pytest.raises(jsonschema.ValidationError, match="'path'.*required"):
            jsonschema.validate(invalid_manifest, project_manifest_schema)

    def test_artifact_accepts_both_formats(self, project_manifest_schema):
        """Artifact metadata accepts both file-based and git-based formats."""
        # File-based format
        file_based_manifest = {
            "apiVersion": "agency.os/v1alpha1",
            "kind": "Project",
            "metadata": {
                "projectId": "test",
                "name": "Test",
                "description": "Test",
                "owner": "test@example.com",
                "createdAt": "2025-11-17T00:00:00Z",
                "lastUpdatedAt": "2025-11-17T00:00:00Z",
            },
            "spec": {"vibe": {}},
            "status": {
                "projectPhase": "PLANNING",
                "lastUpdate": "2025-11-17T00:00:00Z",
                "message": "Test",
            },
            "artifacts": {
                "planning": {
                    "blueprint": {
                        "path": "workspaces/test/artifacts/blueprint.json",
                        "created_at": "2025-11-17T00:00:00Z",
                    }
                }
            },
        }
        jsonschema.validate(file_based_manifest, project_manifest_schema)

        # Git-based format
        git_based_manifest = {
            "apiVersion": "agency.os/v1alpha1",
            "kind": "Project",
            "metadata": {
                "projectId": "test",
                "name": "Test",
                "description": "Test",
                "owner": "test@example.com",
                "createdAt": "2025-11-17T00:00:00Z",
                "lastUpdatedAt": "2025-11-17T00:00:00Z",
            },
            "spec": {"vibe": {}},
            "status": {
                "projectPhase": "PLANNING",
                "lastUpdate": "2025-11-17T00:00:00Z",
                "message": "Test",
            },
            "artifacts": {
                "planning": {
                    "architecture": {
                        "path": "/artifacts/planning/architecture.json",
                        "ref": "ef1c122a4a57d07036f70cb2b5460c199f25059f",
                    }
                }
            },
        }
        jsonschema.validate(git_based_manifest, project_manifest_schema)
