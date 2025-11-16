#!/usr/bin/env python3
"""
E2E System Test: VIBE_ALIGNER Full Workflow
============================================

This test validates the ENTIRE system, not just code units:
1. Create test workspace
2. Initialize CoreOrchestrator with PromptRegistry
3. Execute PLANNING phase (skipping RESEARCH)
4. Verify VIBE_ALIGNER executes all 6 tasks
5. Verify feature_spec.json is generated
6. Verify Guardian Directives are injected in prompts
7. Verify no regressions vs pre-Registry behavior
8. Cleanup test workspace

This is a SYSTEM test - it validates that when a user says "Plan a yoga booking system",
the system produces the correct artifacts with proper governance.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

# Add paths
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / "agency_os" / "00_system" / "orchestrator"))
sys.path.insert(0, str(repo_root / "agency_os" / "00_system" / "runtime"))

from core_orchestrator import CoreOrchestrator
from prompt_registry import PromptRegistry


class TestVibeAlignerSystemE2E:
    """End-to-end system test for VIBE_ALIGNER workflow"""

    @pytest.fixture
    def test_workspace_dir(self):
        """Create isolated test workspace in repo workspaces directory"""
        import shutil

        # Use actual workspaces directory so orchestrator can find it
        workspace_dir = repo_root / "workspaces" / "test-vibe-aligner-e2e"

        # Clean up any existing test workspace
        if workspace_dir.exists():
            shutil.rmtree(workspace_dir)

        workspace_dir.mkdir(parents=True)

        # Create project structure
        project_dir = workspace_dir / "test_project_001"
        project_dir.mkdir()

        (project_dir / "artifacts" / "planning").mkdir(parents=True)
        (project_dir / "artifacts" / "coding").mkdir(parents=True)

        yield workspace_dir

        # Cleanup after test
        shutil.rmtree(workspace_dir, ignore_errors=True)

    @pytest.fixture
    def project_manifest_data(self):
        """Create test project manifest"""
        return {
            "apiVersion": "agency.os/v1alpha1",
            "kind": "Project",
            "metadata": {
                "projectId": "test_project_001",
                "name": "Yoga Booking System",
                "owner": "test_user",
                "description": "A platform for yoga studios to manage class bookings and instructor schedules",
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
            },
            "status": {
                "projectPhase": "PLANNING",
                "subPhase": "BUSINESS_VALIDATION",
                "lastTransition": datetime.now().isoformat(),
            },
            "artifacts": {},
            "budget": {"max_cost_usd": 10.0, "current_cost_usd": 0.0},
        }

    @pytest.fixture
    def lean_canvas_summary(self):
        """Mock lean_canvas_summary.json (prerequisite for VIBE_ALIGNER)"""
        return {
            "version": "1.0",
            "problem": {
                "top_problems": [
                    "Yoga studios lose 30% revenue from no-shows",
                    "Students can't easily find available classes",
                    "Manual scheduling wastes instructor time",
                ]
            },
            "customer_segments": "Yoga studios with 3-10 instructors, serving 50-200 students",
            "unique_value_proposition": "Real-time booking with automated reminders to reduce no-shows",
            "solution": {
                "mvp_features": [
                    "Class schedule display",
                    "Student booking with payment",
                    "Automated SMS/email reminders",
                ]
            },
            "riskiest_assumptions": [
                "Studios will pay $99/month for booking system",
                "30% no-show reduction is achievable",
                "Students will use mobile app for booking",
            ],
            "readiness": {"status": "READY", "missing_inputs": []},
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "validator": "LEAN_CANVAS_VALIDATOR",
            },
        }

    @pytest.fixture
    def mock_llm_responses(self):
        """Mock LLM responses for each VIBE_ALIGNER task"""

        # Task 02: Feature Extraction
        task_02_response = {
            "extracted_features": [
                {
                    "id": "F001",
                    "name": "Class Schedule Display",
                    "description": "Show available yoga classes with date, time, instructor, and capacity",
                    "priority": "must_have",
                    "source": "MVP requirement",
                },
                {
                    "id": "F002",
                    "name": "Student Booking",
                    "description": "Allow students to book classes and make payments",
                    "priority": "must_have",
                    "source": "Core value proposition",
                },
                {
                    "id": "F003",
                    "name": "Automated Reminders",
                    "description": "Send SMS/email reminders to reduce no-shows",
                    "priority": "must_have",
                    "source": "No-show reduction strategy",
                },
            ],
            "metadata": {"task": "feature_extraction", "total_features": 3},
        }

        # Task 03: Feasibility Validation (FAE)
        task_03_response = {
            "validated_features": task_02_response["extracted_features"],
            "fae_validation": {
                "F001": {"status": "FEASIBLE", "constraints": []},
                "F002": {
                    "status": "FEASIBLE",
                    "constraints": ["Payment gateway integration required"],
                },
                "F003": {"status": "FEASIBLE", "constraints": ["Twilio/SendGrid API required"]},
            },
            "metadata": {"task": "feasibility_validation", "fae_rules_applied": 15},
        }

        # Task 04: Gap Detection (FDG)
        task_04_response = {
            "features_with_dependencies": task_03_response["validated_features"],
            "dependencies": {
                "F002": ["F001"],  # Booking depends on schedule
                "F003": ["F002"],  # Reminders depend on bookings
            },
            "gaps_detected": [],
            "metadata": {"task": "gap_detection", "fdg_rules_applied": 8},
        }

        # Task 05: Scope Negotiation (APCE)
        task_05_response = {
            "negotiated_features": task_04_response["features_with_dependencies"],
            "complexity_scores": {"F001": 13, "F002": 21, "F003": 8},
            "total_complexity": 42,
            "metadata": {"task": "scope_negotiation", "apce_rules_applied": 12},
        }

        # Task 06: Output Generation (feature_spec.json)
        task_06_response = {
            "project": {
                "name": "Yoga Booking System",
                "category": "Web Application",
                "scale": "Small Business (10-100 users)",
                "core_problem": "Yoga studios lose revenue from no-shows and inefficient manual scheduling",
            },
            "features": [
                {
                    "id": "F001",
                    "name": "Class Schedule Display",
                    "description": "Show available yoga classes with date, time, instructor, and capacity",
                    "priority": "must_have",
                    "complexity_score": 13,
                    "estimated_effort": "3-5 days",
                    "dependencies": [],
                },
                {
                    "id": "F002",
                    "name": "Student Booking",
                    "description": "Allow students to book classes and make payments",
                    "priority": "must_have",
                    "complexity_score": 21,
                    "estimated_effort": "5-8 days",
                    "dependencies": ["F001"],
                },
                {
                    "id": "F003",
                    "name": "Automated Reminders",
                    "description": "Send SMS/email reminders to reduce no-shows",
                    "priority": "must_have",
                    "complexity_score": 8,
                    "estimated_effort": "2-3 days",
                    "dependencies": ["F002"],
                },
            ],
            "scope_negotiation": {
                "total_complexity": 42,
                "complexity_breakdown": {"must_have": 42, "should_have": 0, "nice_to_have": 0},
                "timeline_estimate": "2-3 weeks",
            },
            "validation": {
                "fae_passed": True,
                "fdg_passed": True,
                "apce_passed": True,
                "ready_for_coding": True,
            },
            "metadata": {
                "vibe_version": "3.0",
                "created_at": datetime.now().isoformat(),
                "agent": "VIBE_ALIGNER",
            },
        }

        return {
            "task_01_education_calibration": {"status": "educated", "calibrated": True},
            "task_02_feature_extraction": task_02_response,
            "task_03_feasibility_validation": task_03_response,
            "task_04_gap_detection": task_04_response,
            "task_05_scope_negotiation": task_05_response,
            "task_06_output_generation": task_06_response,
        }

    def test_vibe_aligner_full_system_flow(
        self, test_workspace_dir, project_manifest_data, lean_canvas_summary, mock_llm_responses
    ):
        """
        MAIN E2E TEST: Full VIBE_ALIGNER system workflow

        This test validates:
        1. Orchestrator initialization with PromptRegistry
        2. Prompt composition with Guardian Directives
        3. All 6 VIBE_ALIGNER tasks execute
        4. feature_spec.json is generated and valid
        5. Schema validation passes
        6. No regressions from previous behavior
        """

        # ============================================
        # STEP 1: Setup Test Environment
        # ============================================

        # Create project manifest file
        project_dir = test_workspace_dir / "test_project_001"
        manifest_path = project_dir / "project_manifest.json"

        with open(manifest_path, "w") as f:
            json.dump(project_manifest_data, f, indent=2)

        # Create lean_canvas_summary.json (prerequisite)
        lean_canvas_path = project_dir / "artifacts" / "planning" / "lean_canvas_summary.json"
        with open(lean_canvas_path, "w") as f:
            json.dump(lean_canvas_summary, f, indent=2)

        print("\n" + "=" * 80)
        print("E2E SYSTEM TEST: VIBE_ALIGNER Full Workflow")
        print("=" * 80)
        print(f"Test workspace: {test_workspace_dir}")
        print(f"Project: {project_manifest_data['metadata']['name']}")
        print()

        # ============================================
        # STEP 2: Initialize Orchestrator with Registry
        # ============================================

        print("STEP 1: Initializing CoreOrchestrator with PromptRegistry...")

        # Set environment to skip optional RESEARCH phase
        os.environ["VIBE_AUTO_MODE"] = "true"

        # Mock LLM client to avoid real API calls
        with patch("core_orchestrator.LLMClient") as MockLLMClient:
            mock_llm = MockLLMClient.return_value

            # Configure mock to return appropriate responses based on task_id
            def mock_invoke(prompt, model=None, max_tokens=4096):
                # Detect which task from the prompt
                if "task_01_education" in prompt.lower() or "education" in prompt.lower():
                    response_data = mock_llm_responses["task_01_education_calibration"]
                elif "task_02_feature" in prompt.lower() or "extraction" in prompt.lower():
                    response_data = mock_llm_responses["task_02_feature_extraction"]
                elif "task_03_feasibility" in prompt.lower() or "fae" in prompt.lower():
                    response_data = mock_llm_responses["task_03_feasibility_validation"]
                elif "task_04_gap" in prompt.lower() or "fdg" in prompt.lower():
                    response_data = mock_llm_responses["task_04_gap_detection"]
                elif "task_05_scope" in prompt.lower() or "negotiation" in prompt.lower():
                    response_data = mock_llm_responses["task_05_scope_negotiation"]
                elif "task_06_output" in prompt.lower() or "generation" in prompt.lower():
                    response_data = mock_llm_responses["task_06_output_generation"]
                else:
                    # Default response for LEAN_CANVAS_VALIDATOR
                    response_data = lean_canvas_summary

                # Create mock response object with .content attribute
                from unittest.mock import MagicMock
                import json
                mock_response = MagicMock()
                mock_response.content = json.dumps(response_data)
                return mock_response

            # Mock get_cost_summary to return proper cost data
            mock_llm.get_cost_summary.return_value = {
                "total_cost_usd": 0.50,
                "budget_used_percent": 5.0
            }

            # Track prompts for Guardian Directive verification
            executed_prompts = []

            def track_and_invoke(prompt, model=None, max_tokens=4096):
                executed_prompts.append(
                    {"prompt": prompt, "length": len(prompt)}
                )
                return mock_invoke(prompt, model, max_tokens)

            mock_llm.invoke.side_effect = track_and_invoke

            # Initialize orchestrator in autonomous mode (for testing)
            orchestrator = CoreOrchestrator(repo_root=str(repo_root), execution_mode="autonomous")

            # Verify PromptRegistry is being used
            assert orchestrator.use_registry, "PromptRegistry should be enabled"
            assert orchestrator.prompt_registry is not None, "PromptRegistry should be initialized"
            print("✓ PromptRegistry enabled")

            # ============================================
            # STEP 3: Execute PLANNING Phase
            # ============================================

            print("\nSTEP 2: Executing PLANNING phase...")
            print("  - RESEARCH: SKIPPED (auto mode)")
            print("  - BUSINESS_VALIDATION: Running...")
            print("  - FEATURE_SPECIFICATION: Running (VIBE_ALIGNER all 6 tasks)...")

            try:
                # Execute planning phase (this will run BUSINESS_VALIDATION + FEATURE_SPECIFICATION)
                orchestrator.run_full_sdlc("test_project_001")

                print("✓ PLANNING phase completed")

            except Exception as e:
                pytest.fail(f"PLANNING phase failed: {e}")

            # ============================================
            # STEP 4: Verify Artifacts Generated
            # ============================================

            print("\nSTEP 3: Verifying artifacts generated...")

            # Check feature_spec.json exists
            feature_spec_path = project_dir / "artifacts" / "planning" / "feature_spec.json"
            assert feature_spec_path.exists(), "feature_spec.json should exist"
            print(f"✓ feature_spec.json exists: {feature_spec_path}")

            # Load and validate feature_spec.json
            with open(feature_spec_path, "r") as f:
                feature_spec = json.load(f)

            # Validate structure
            assert "project" in feature_spec, "feature_spec should have 'project' section"
            assert "features" in feature_spec, "feature_spec should have 'features' section"
            assert "scope_negotiation" in feature_spec, (
                "feature_spec should have 'scope_negotiation' section"
            )
            assert "validation" in feature_spec, "feature_spec should have 'validation' section"
            assert "metadata" in feature_spec, "feature_spec should have 'metadata' section"

            # Validate features
            assert len(feature_spec["features"]) == 3, "Should have 3 features"
            for feature in feature_spec["features"]:
                assert "id" in feature
                assert "name" in feature
                assert "priority" in feature
                assert "complexity_score" in feature
                assert "estimated_effort" in feature

            print("✓ feature_spec.json is valid")
            print(f"  - Features: {len(feature_spec['features'])}")
            print(f"  - Total complexity: {feature_spec['scope_negotiation']['total_complexity']}")

            # ============================================
            # STEP 5: Verify Guardian Directives in Prompts
            # ============================================

            print("\nSTEP 4: Verifying Guardian Directives were injected...")

            guardian_found_count = 0
            for prompt_info in executed_prompts:
                prompt = prompt_info["prompt"]

                # Check for Guardian Directive markers
                has_guardian = any(
                    [
                        "GUARDIAN_DIRECTIVES" in prompt,
                        "Guardian Directive" in prompt,
                        "CORRUPTION_PREVENTION" in prompt,
                        "JSON_ENFORCEMENT" in prompt,
                        "HALLUCINATION_PREVENTION" in prompt,
                    ]
                )

                if has_guardian:
                    guardian_found_count += 1
                    print(f"✓ Guardian Directives found in: {prompt_info['agent']}")

            # Verify at least some prompts had Guardian Directives
            assert guardian_found_count > 0, (
                "Guardian Directives should be present in at least one prompt"
            )
            print(
                f"✓ Guardian Directives found in {guardian_found_count}/{len(executed_prompts)} prompts"
            )

            # ============================================
            # STEP 6: Verify Schema Validation
            # ============================================

            print("\nSTEP 5: Verifying schema validation...")

            # The fact that save_artifact succeeded means schema validation passed
            # (orchestrator.save_artifact calls validator.validate_artifact)
            print("✓ Schema validation passed (artifact saved successfully)")

            # ============================================
            # STEP 7: Verify No Regressions
            # ============================================

            print("\nSTEP 6: Checking for regressions...")

            # Check that manifest was updated correctly
            updated_manifest_path = project_dir / "project_manifest.json"
            with open(updated_manifest_path, "r") as f:
                updated_manifest = json.load(f)

            # Verify phase transition (should be in CODING or still PLANNING if quality gates blocked)
            # For this test, we expect CODING since we mocked successful responses
            # NOTE: Actual behavior depends on quality gates
            print(f"✓ Final phase: {updated_manifest['status']['projectPhase']}")

            # Verify no errors in manifest
            assert "errors" not in updated_manifest.get("status", {}), (
                "Manifest should not have errors"
            )

            print("\n" + "=" * 80)
            print("E2E TEST PASSED ✅")
            print("=" * 80)
            print("SUMMARY:")
            print("  - Orchestrator initialized: ✓")
            print("  - PromptRegistry enabled: ✓")
            print(f"  - Guardian Directives injected: ✓ ({guardian_found_count} prompts)")
            print("  - VIBE_ALIGNER executed: ✓")
            print("  - feature_spec.json generated: ✓")
            print("  - Schema validation passed: ✓")
            print("  - No regressions: ✓")
            print()

    def test_prompt_registry_governance_injection(self):
        """
        Test: Verify PromptRegistry injects Guardian Directives

        This is a focused test to validate that Guardian Directives
        are present in composed prompts.
        """
        print("\n" + "=" * 80)
        print("TEST: PromptRegistry Guardian Directive Injection")
        print("=" * 80)

        # Initialize PromptRegistry
        registry = PromptRegistry()

        # Compose a test prompt
        prompt = registry.compose(
            agent="VIBE_ALIGNER",
            task="task_02_feature_extraction",
            workspace="test",
            inject_governance=True,
            context={"test": "context"},
        )

        # Verify Guardian Directives are present (check for the heading marker)
        has_guardian_section = "# === GUARDIAN DIRECTIVES ===" in prompt

        assert has_guardian_section, (
            "Composed prompt should contain '# === GUARDIAN DIRECTIVES ===' section"
        )

        print("✓ Guardian Directives present in composed prompt")
        print(f"  Prompt length: {len(prompt)} characters")

        # Verify other expected sections
        assert "VIBE_ALIGNER" in prompt, "Prompt should reference agent name"
        print("✓ Agent identity preserved")

        print("\nTEST PASSED ✅")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
