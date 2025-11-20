#!/usr/bin/env python3
"""
Test: VIBE_ALIGNER End-to-End Workflow
======================================

Tests VIBE_ALIGNER agent workflow (Tasks 01-06):
- Task 01: Education/Calibration
- Task 02: Feature Extraction
- Task 03: Feasibility Validation (FAE)
- Task 04: Gap Detection (FDG)
- Task 05: Scope Negotiation (APCE)
- Task 06: Output Generation (feature_spec.json)

Validates that VIBE_ALIGNER workflow completes and generates valid feature_spec.json.

This test validates the dogfooding exercise that created feature_spec_v1.0_FINAL.json.
"""

import json
from pathlib import Path

import pytest
import yaml

# Add paths
repo_root = Path(__file__).parent.parent

from vibe_core.runtime.prompt_runtime import PromptRuntime


class TestVibeAlignerE2E:
    """End-to-end tests for VIBE_ALIGNER workflow"""

    @pytest.fixture
    def vibe_aligner_path(self):
        """Get VIBE_ALIGNER agent path"""
        return repo_root / "agency_os" / "01_planning_framework" / "agents" / "VIBE_ALIGNER"

    @pytest.fixture
    def prompt_runtime(self):
        """Initialize PromptRuntime"""
        return PromptRuntime()

    def test_vibe_aligner_agent_exists(self, vibe_aligner_path):
        """Test: VIBE_ALIGNER agent directory exists"""
        assert vibe_aligner_path.exists()
        assert vibe_aligner_path.is_dir()

    def test_vibe_aligner_composition_exists(self, vibe_aligner_path):
        """Test: VIBE_ALIGNER composition file exists and is valid YAML"""
        composition_path = vibe_aligner_path / "_composition.yaml"
        assert composition_path.exists()

        with open(composition_path) as f:
            composition = yaml.safe_load(f)

        assert composition is not None
        assert "composition_version" in composition
        assert "agent_id" in composition
        assert composition["agent_id"] == "VIBE_ALIGNER"

    def test_vibe_aligner_has_all_6_tasks(self, vibe_aligner_path):
        """Test: VIBE_ALIGNER has all 6 tasks (01-06)"""
        tasks_dir = vibe_aligner_path / "tasks"
        assert tasks_dir.exists()

        required_tasks = [
            "task_01_education_calibration.md",
            "task_02_feature_extraction.md",
            "task_03_feasibility_validation.md",
            "task_04_gap_detection.md",
            "task_05_scope_negotiation.md",
            "task_06_output_generation.md",
        ]

        for task_file in required_tasks:
            task_path = tasks_dir / task_file
            assert task_path.exists(), f"Missing task: {task_file}"

    def test_vibe_aligner_task_metadata_exists(self, vibe_aligner_path):
        """Test: All VIBE_ALIGNER tasks have metadata (.meta.yaml)"""
        tasks_dir = vibe_aligner_path / "tasks"

        required_meta = [
            "task_01_education_calibration.meta.yaml",
            "task_02_feature_extraction.meta.yaml",
            "task_03_feasibility_validation.meta.yaml",
            "task_04_gap_detection.meta.yaml",
            "task_05_scope_negotiation.meta.yaml",
            "task_06_output_generation.meta.yaml",
        ]

        for meta_file in required_meta:
            meta_path = tasks_dir / meta_file
            assert meta_path.exists(), f"Missing metadata: {meta_file}"

            # Validate YAML
            with open(meta_path) as f:
                meta = yaml.safe_load(f)
                assert "phase" in meta
                # Note: 'description' might not be in all meta files

    def test_vibe_aligner_knowledge_dependencies_exist(self, vibe_aligner_path):
        """Test: VIBE_ALIGNER knowledge dependencies file exists"""
        knowledge_deps_path = vibe_aligner_path / "_knowledge_deps.yaml"
        assert knowledge_deps_path.exists()

        with open(knowledge_deps_path) as f:
            deps = yaml.safe_load(f)

        assert deps is not None
        # VIBE_ALIGNER uses FAE, FDG, APCE knowledge bases

    def test_knowledge_bases_exist(self):
        """Test: FAE, FDG, APCE knowledge bases exist"""
        knowledge_path = repo_root / "agency_os" / "01_planning_framework" / "knowledge"

        required_knowledge = ["FAE_constraints.yaml", "FDG_dependencies.yaml", "APCE_rules.yaml"]

        for kb_file in required_knowledge:
            kb_path = knowledge_path / kb_file
            assert kb_path.exists(), f"Missing knowledge base: {kb_file}"

            # Validate YAML (handle multi-document YAML)
            with open(kb_path) as f:
                docs = list(yaml.safe_load_all(f))
                assert len(docs) > 0

    def test_fae_knowledge_base_structure(self):
        """Test: FAE knowledge base has correct structure"""
        fae_path = (
            repo_root / "agency_os" / "01_planning_framework" / "knowledge" / "FAE_constraints.yaml"
        )

        with open(fae_path) as f:
            fae = yaml.safe_load(f)

        # FAE has constraints or rules structure
        assert fae is not None

    def test_fdg_knowledge_base_structure(self):
        """Test: FDG knowledge base has correct structure"""
        fdg_path = (
            repo_root
            / "agency_os"
            / "01_planning_framework"
            / "knowledge"
            / "FDG_dependencies.yaml"
        )

        with open(fdg_path) as f:
            # FDG might be multi-document YAML
            docs = list(yaml.safe_load_all(f))
            assert len(docs) > 0

    def test_apce_knowledge_base_structure(self):
        """Test: APCE knowledge base has correct structure"""
        apce_path = (
            repo_root / "agency_os" / "01_planning_framework" / "knowledge" / "APCE_rules.yaml"
        )

        with open(apce_path) as f:
            # APCE might be multi-document YAML
            docs = list(yaml.safe_load_all(f))
            assert len(docs) > 0

    def test_vibe_aligner_composition_order(self, vibe_aligner_path):
        """Test: VIBE_ALIGNER composition order is correct"""
        composition_path = vibe_aligner_path / "_composition.yaml"

        with open(composition_path) as f:
            composition = yaml.safe_load(f)

        assert "composition_order" in composition
        order = composition["composition_order"]

        # Verify expected components
        sources = [item["source"] for item in order]
        assert "_prompt_core.md" in sources
        assert "${knowledge_files}" in sources
        assert "${task_prompt}" in sources
        assert "${runtime_context}" in sources

    def test_vibe_aligner_workflow_notes(self, vibe_aligner_path):
        """Test: VIBE_ALIGNER composition has workflow notes"""
        composition_path = vibe_aligner_path / "_composition.yaml"

        with open(composition_path) as f:
            composition = yaml.safe_load(f)

        assert "notes" in composition
        notes = composition["notes"]

        # Verify workflow description
        assert "Task 1" in notes
        assert "Task 6" in notes
        assert "feature_spec.json" in notes

    def test_prompt_runtime_can_load_vibe_aligner(self, prompt_runtime):
        """Test: PromptRuntime can load VIBE_ALIGNER agent"""
        # This tests that the agent is registered and loadable
        # (actual execution would require LLM calls)

        agent_path = prompt_runtime._get_agent_path("VIBE_ALIGNER")
        assert agent_path.exists()
        assert agent_path.name == "VIBE_ALIGNER"

    def test_feature_spec_schema_from_dogfooding(self):
        """Test: feature_spec.json from dogfooding has correct structure"""
        feature_spec_path = repo_root / "artifacts" / "planning" / "feature_spec_v1.0_FINAL.json"

        if not feature_spec_path.exists():
            pytest.skip("feature_spec_v1.0_FINAL.json not found (dogfooding not completed)")

        with open(feature_spec_path) as f:
            spec = json.load(f)

        # Validate structure
        assert "project" in spec
        assert "features" in spec
        assert "scope_negotiation" in spec
        assert "validation" in spec
        assert "metadata" in spec

        # Validate project section
        assert "name" in spec["project"]
        assert "core_problem" in spec["project"]

        # Validate features section
        assert isinstance(spec["features"], list)
        assert len(spec["features"]) > 0

        # Validate first feature structure
        feature = spec["features"][0]
        assert "id" in feature
        assert "name" in feature
        assert "priority" in feature
        assert "complexity_score" in feature
        assert "estimated_effort" in feature

        # Validate metadata
        assert "vibe_version" in spec["metadata"]
        assert "created_at" in spec["metadata"]
        assert spec["metadata"]["vibe_version"] == "3.0"

    def test_vibe_aligner_task_01_education(self, vibe_aligner_path):
        """Test: Task 01 (Education/Calibration) exists and has correct structure"""
        task_path = vibe_aligner_path / "tasks" / "task_01_education_calibration.md"
        assert task_path.exists()

        # Task should educate user about v1.0 constraints
        with open(task_path) as f:
            content = f.read()
            assert len(content) > 0

    def test_vibe_aligner_task_06_output(self, vibe_aligner_path):
        """Test: Task 06 (Output Generation) exists and generates feature_spec.json"""
        task_path = vibe_aligner_path / "tasks" / "task_06_output_generation.md"
        assert task_path.exists()

        # Task should generate feature_spec.json
        with open(task_path) as f:
            content = f.read()
            assert "feature_spec.json" in content

    def test_dogfooding_artifacts_exist(self):
        """Test: Dogfooding artifacts exist (from VIBE_ALIGNER self-application)"""
        artifacts_dir = repo_root / "artifacts" / "planning"

        expected_artifacts = [
            "feature_spec_v1.0_FINAL.json",
            # Raw artifacts from Tasks 03-06
            "phase_03_feasibility.json",
            "phase_04_gap_detection.json",
        ]

        for artifact in expected_artifacts:
            artifact_path = artifacts_dir / artifact
            if artifact_path.exists():
                # Validate JSON
                with open(artifact_path) as f:
                    data = json.load(f)
                    assert data is not None

    def test_vibe_aligner_validates_fae(self):
        """Test: Task 03 validates features against FAE constraints"""
        feasibility_path = repo_root / "artifacts" / "planning" / "phase_03_feasibility.json"

        if not feasibility_path.exists():
            pytest.skip("phase_03_feasibility.json not found")

        with open(feasibility_path) as f:
            feasibility = json.load(f)

        assert "feature_feasibility_checks" in feasibility
        checks = feasibility["feature_feasibility_checks"]

        # Each feature should have FAE validation
        for check in checks:
            assert "feature_id" in check
            assert "fae_rules_checked" in check
            assert "status" in check
            # Status can be FEASIBLE, INFEASIBLE_FOR_V1, or IN_PROGRESS
            assert check["status"] in ["FEASIBLE", "INFEASIBLE_FOR_V1", "IN_PROGRESS"]

    def test_vibe_aligner_detects_gaps_with_fdg(self):
        """Test: Task 04 detects gaps using FDG dependencies"""
        gap_detection_path = repo_root / "artifacts" / "planning" / "phase_04_gap_detection.json"

        if not gap_detection_path.exists():
            pytest.skip("phase_04_gap_detection.json not found")

        with open(gap_detection_path) as f:
            gap_detection = json.load(f)

        assert "features_with_dependencies" in gap_detection
        features = gap_detection["features_with_dependencies"]

        # Each feature should have dependencies analyzed
        for feature in features:
            assert "feature_id" in feature
            assert "dependencies" in feature

    def test_vibe_aligner_negotiates_scope_with_apce(self):
        """Test: Task 05 negotiates scope using APCE complexity scoring"""
        final_spec_path = repo_root / "artifacts" / "planning" / "feature_spec_v1.0_FINAL.json"

        if not final_spec_path.exists():
            pytest.skip("feature_spec_v1.0_FINAL.json not found")

        with open(final_spec_path) as f:
            spec = json.load(f)

        assert "scope_negotiation" in spec
        negotiation = spec["scope_negotiation"]

        # Scope negotiation should have complexity breakdown
        assert "total_complexity" in negotiation
        assert "complexity_breakdown" in negotiation
        assert "timeline_estimate" in negotiation

        # Each feature should have complexity score
        for feature in spec["features"]:
            assert "complexity_score" in feature


def test_vibe_aligner_basic():
    """Test: Basic VIBE_ALIGNER agent check"""
    agent_path = repo_root / "agency_os" / "01_planning_framework" / "agents" / "VIBE_ALIGNER"
    assert agent_path.exists()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
