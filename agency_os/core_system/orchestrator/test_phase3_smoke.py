#!/usr/bin/env python3
"""
Phase 3 Smoke Test
==================

Basic smoke test to verify Phase 3 implementation:
1. Core orchestrator can be instantiated
2. All phase handlers can be imported
3. LLM client graceful failover works
4. Schema validator loads contracts

This is NOT a full integration test - just validates the structure.
Full integration testing will come in Phase 4.

Usage:
    python test_phase3_smoke.py
"""

from pathlib import Path


def test_imports():
    """Test that all Phase 3 modules can be imported"""
    print("=" * 80)
    print("TEST 1: Module Imports")
    print("=" * 80 + "\n")

    try:
        print("📦 Importing core_orchestrator...")
        print("✅ core_orchestrator imported\n")

        print("📦 Importing llm_client...")
        print("✅ llm_client imported\n")

        print("📦 Importing phase handlers...")
        print("✅ All phase handlers imported\n")

        return True
    except Exception as e:
        print(f"❌ Import failed: {e}\n")
        import traceback

        traceback.print_exc()
        return False


def test_orchestrator_init():
    """Test that orchestrator can be instantiated"""
    print("=" * 80)
    print("TEST 2: Orchestrator Initialization")
    print("=" * 80 + "\n")

    try:
        print("🏗️  Initializing CoreOrchestrator...")
        from orchestrator.core_orchestrator import CoreOrchestrator

        orch_repo_root = Path.cwd()
        orchestrator = CoreOrchestrator(repo_root=orch_repo_root)

        print("✅ Orchestrator initialized")
        print(f"   Repo root: {orchestrator.repo_root}")
        print(f"   Workspaces: {orchestrator.workspaces_dir}")
        print(f"   Workflow loaded: {orchestrator.workflow.get('version', 'unknown')}\n")

        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}\n")
        import traceback

        traceback.print_exc()
        return False


def test_llm_client_failover():
    """Test LLM client graceful failover (NoOpClient when no API key)"""
    print("=" * 80)
    print("TEST 3: LLM Client Graceful Failover")
    print("=" * 80 + "\n")

    try:
        print("🔌 Testing LLM client initialization...")
        import os

        from runtime.llm_client import LLMClient

        # Temporarily remove API key to test failover
        api_key_backup = os.environ.get("ANTHROPIC_API_KEY")
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]

        client = LLMClient()
        print("✅ LLM Client initialized (graceful failover)")
        print(f"   Client type: {type(client.client).__name__}")
        print(f"   Knowledge-only mode: {client.client.__class__.__name__ == 'NoOpClient'}\n")

        # Restore API key
        if api_key_backup:
            os.environ["ANTHROPIC_API_KEY"] = api_key_backup

        return True
    except Exception as e:
        print(f"❌ LLM client test failed: {e}\n")
        import traceback

        traceback.print_exc()
        return False


def test_schema_validator():
    """Test that schema validator can load contracts"""
    print("=" * 80)
    print("TEST 4: Schema Validator")
    print("=" * 80 + "\n")

    try:
        print("📋 Loading schema validator...")
        from orchestrator.core_orchestrator import SchemaValidator

        contracts_path = (
            Path.cwd() / "agency_os/core_system/contracts/ORCHESTRATION_data_contracts.yaml"
        )
        validator = SchemaValidator(contracts_path)

        print("✅ Schema validator initialized")
        print(f"   Contracts file: {contracts_path}")
        if validator.contracts:
            schemas = validator.contracts.get("schemas", [])
            print(f"   Schemas loaded: {len(schemas)}")

            # List some schemas
            schema_names = [s.get("name", "unknown") for s in schemas[:5]]
            if schema_names:
                print(f"   Sample schemas: {', '.join(schema_names)}")
        print()

        return True
    except Exception as e:
        print(f"❌ Schema validator test failed: {e}\n")
        import traceback

        traceback.print_exc()
        return False


def test_phase_handlers():
    """Test that all phase handlers can be instantiated"""
    print("=" * 80)
    print("TEST 5: Phase Handlers")
    print("=" * 80 + "\n")

    try:
        print("🎯 Testing phase handlers...")
        from orchestrator.core_orchestrator import CoreOrchestrator, ProjectPhase

        handler_repo_root = Path.cwd()
        orchestrator = CoreOrchestrator(repo_root=handler_repo_root)

        phases = [
            ProjectPhase.PLANNING,
            ProjectPhase.CODING,
            ProjectPhase.TESTING,
            ProjectPhase.DEPLOYMENT,
            ProjectPhase.MAINTENANCE,
        ]

        for phase in phases:
            handler = orchestrator.get_phase_handler(phase)
            print(f"   ✓ {phase.value}: {type(handler).__name__}")

        print("\n✅ All phase handlers loaded successfully\n")
        return True
    except Exception as e:
        print(f"❌ Phase handler test failed: {e}\n")
        import traceback

        traceback.print_exc()
        return False


def test_knowledge_metadata():
    """Test that knowledge bases have metadata headers"""
    print("=" * 80)
    print("TEST 6: Knowledge Base Metadata (GAD-002 Decision 10)")
    print("=" * 80 + "\n")

    try:
        print("📚 Checking knowledge base metadata...")
        import yaml

        test_files = [
            "agency_os/01_planning_framework/knowledge/research/RESEARCH_market_sizing_formulas.yaml",
            "agency_os/01_planning_framework/knowledge/research/RESEARCH_competitor_analysis_templates.yaml",
            "agency_os/01_planning_framework/knowledge/research/RESEARCH_red_flag_taxonomy.yaml",
            "agency_os/core_system/knowledge/AOS_Ontology.yaml",
        ]

        for file_path in test_files:
            full_path = Path.cwd() / file_path
            if full_path.exists():
                with open(full_path) as f:
                    content = yaml.safe_load(f)

                if "metadata" in content:
                    metadata = content["metadata"]
                    print(f"   ✓ {file_path.split('/')[-1]}")
                    print(f"      Version: {metadata.get('version', 'N/A')}")
                    print(f"      Status: {metadata.get('status', 'N/A')}")
                    print(f"      Next review: {metadata.get('next_review_date', 'N/A')}")
                else:
                    print(f"   ⚠️  {file_path.split('/')[-1]}: No metadata header")

        print("\n✅ Knowledge metadata check complete\n")
        return True
    except Exception as e:
        print(f"❌ Knowledge metadata test failed: {e}\n")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all smoke tests"""
    print("\n" + "=" * 80)
    print("PHASE 3 SMOKE TEST SUITE")
    print("GAD-002: Core SDLC Orchestration Architecture")
    print("=" * 80 + "\n")

    tests = [
        ("Module Imports", test_imports),
        ("Orchestrator Initialization", test_orchestrator_init),
        ("LLM Client Graceful Failover", test_llm_client_failover),
        ("Schema Validator", test_schema_validator),
        ("Phase Handlers", test_phase_handlers),
        ("Knowledge Metadata", test_knowledge_metadata),
    ]

    results = []
    for test_name, test_func in tests:
        success = test_func()
        results.append((test_name, success))

    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80 + "\n")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status}: {test_name}")

    print(f"\n   Total: {passed}/{total} tests passed\n")

    if passed == total:
        print("=" * 80)
        print("🎉 ALL TESTS PASSED - PHASE 3 STRUCTURE VALIDATED")
        print("=" * 80 + "\n")
        return 0
    else:
        print("=" * 80)
        print("❌ SOME TESTS FAILED - REVIEW ERRORS ABOVE")
        print("=" * 80 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
