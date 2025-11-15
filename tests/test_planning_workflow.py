#!/usr/bin/env python3
"""
Test script for validating the Planning Workflow integration.

Tests:
1. State Machine YAML is valid
2. Sub-states are properly defined
3. Transitions T0 and T1 are correct
4. Data contracts for lean_canvas_summary.json exist
5. Agent task files have correct references
"""

import os
import sys
import yaml
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_test(name: str):
    """Print test name"""
    print(f"\n{Colors.BLUE}Testing: {name}{Colors.RESET}")


def print_success(message: str):
    """Print success message"""
    print(f"  {Colors.GREEN}✅ {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message"""
    print(f"  {Colors.RED}❌ {message}{Colors.RESET}")


def print_warning(message: str):
    """Print warning message"""
    print(f"  {Colors.YELLOW}⚠️  {message}{Colors.RESET}")


def test_state_machine_yaml():
    """Test 1: Validate State Machine YAML structure"""
    print_test("State Machine YAML validation")

    yaml_path = PROJECT_ROOT / "agency_os/00_system/state_machine/ORCHESTRATION_workflow_design.yaml"

    if not yaml_path.exists():
        print_error(f"State machine YAML not found at {yaml_path}")
        return False

    try:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        print_success("YAML is valid and parseable")
    except yaml.YAMLError as e:
        print_error(f"YAML parsing error: {e}")
        return False

    # Check for PLANNING state
    states = data.get('states', [])
    planning_state = None
    for state in states:
        if state.get('name') == 'PLANNING':
            planning_state = state
            break

    if not planning_state:
        print_error("PLANNING state not found")
        return False

    print_success("PLANNING state found")

    # Check for sub_states
    sub_states = planning_state.get('sub_states', [])
    if not sub_states:
        print_error("No sub_states defined for PLANNING")
        return False

    print_success(f"Found {len(sub_states)} sub-states")

    # Validate sub-states
    expected_substates = ['BUSINESS_VALIDATION', 'FEATURE_SPECIFICATION', 'ARCHITECTURE_DESIGN']
    found_substates = [s.get('name') for s in sub_states]

    for expected in expected_substates:
        if expected in found_substates:
            print_success(f"Sub-state '{expected}' exists")
        else:
            print_error(f"Sub-state '{expected}' missing")
            return False

    return True


def test_transitions():
    """Test 2: Validate T0 and T1 transitions"""
    print_test("Transition validation")

    yaml_path = PROJECT_ROOT / "agency_os/00_system/state_machine/ORCHESTRATION_workflow_design.yaml"

    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)

    transitions = data.get('transitions', [])

    # Check T0_BusinessToFeatures
    t0 = None
    for t in transitions:
        if t.get('name') == 'T0_BusinessToFeatures':
            t0 = t
            break

    if not t0:
        print_error("Transition T0_BusinessToFeatures not found")
        return False

    print_success("T0_BusinessToFeatures exists")

    # Validate T0 structure
    if t0.get('from_state') != 'PLANNING.BUSINESS_VALIDATION':
        print_error(f"T0 from_state incorrect: {t0.get('from_state')}")
        return False

    if t0.get('to_state') != 'PLANNING.FEATURE_SPECIFICATION':
        print_error(f"T0 to_state incorrect: {t0.get('to_state')}")
        return False

    print_success("T0 from/to states are correct")

    # Check T1_StartCoding
    t1 = None
    for t in transitions:
        if t.get('name') == 'T1_StartCoding':
            t1 = t
            break

    if not t1:
        print_error("Transition T1_StartCoding not found")
        return False

    print_success("T1_StartCoding exists")

    # Validate T1 from_state (should transition from ARCHITECTURE_DESIGN)
    if t1.get('from_state') != 'PLANNING.ARCHITECTURE_DESIGN':
        print_error(f"T1 from_state incorrect (should be PLANNING.ARCHITECTURE_DESIGN): {t1.get('from_state')}")
        return False

    print_success("T1 from_state correctly set to PLANNING.ARCHITECTURE_DESIGN")

    # Check T0c_FeaturesToArchitecture
    t0c = None
    for t in transitions:
        if t.get('name') == 'T0c_FeaturesToArchitecture':
            t0c = t
            break

    if not t0c:
        print_error("Transition T0c_FeaturesToArchitecture not found")
        return False

    print_success("T0c_FeaturesToArchitecture exists")

    # Validate T0c structure
    if t0c.get('from_state') != 'PLANNING.FEATURE_SPECIFICATION':
        print_error(f"T0c from_state incorrect: {t0c.get('from_state')}")
        return False

    if t0c.get('to_state') != 'PLANNING.ARCHITECTURE_DESIGN':
        print_error(f"T0c to_state incorrect: {t0c.get('to_state')}")
        return False

    print_success("T0c from/to states are correct")

    return True


def test_data_contracts():
    """Test 3: Validate lean_canvas_summary data contract"""
    print_test("Data contract validation")

    contracts_path = PROJECT_ROOT / "agency_os/00_system/contracts/ORCHESTRATION_data_contracts.yaml"

    if not contracts_path.exists():
        print_error(f"Data contracts file not found at {contracts_path}")
        return False

    with open(contracts_path, 'r') as f:
        data = yaml.safe_load(f)

    schemas = data.get('schemas', [])

    # Find lean_canvas_summary schema
    lean_canvas_schema = None
    for schema in schemas:
        if schema.get('name') == 'lean_canvas_summary.schema.json':
            lean_canvas_schema = schema
            break

    if not lean_canvas_schema:
        print_error("lean_canvas_summary.schema.json not found in data contracts")
        return False

    print_success("lean_canvas_summary schema exists")

    # Validate required fields
    fields = lean_canvas_schema.get('fields', [])
    required_fields = ['version', 'canvas_fields', 'riskiest_assumptions', 'readiness']

    field_names = [f.get('name') for f in fields]

    for req_field in required_fields:
        if req_field in field_names:
            print_success(f"Required field '{req_field}' exists")
        else:
            print_error(f"Required field '{req_field}' missing")
            return False

    return True


def test_agent_integrations():
    """Test 4: Validate agent task file updates"""
    print_test("Agent integration validation")

    # Test VIBE_ALIGNER _prompt_core.md
    vibe_prompt = PROJECT_ROOT / "agency_os/01_planning_framework/agents/VIBE_ALIGNER/_prompt_core.md"

    if not vibe_prompt.exists():
        print_error("VIBE_ALIGNER _prompt_core.md not found")
        return False

    with open(vibe_prompt, 'r') as f:
        content = f.read()

    if "lean_canvas_summary.json" in content:
        print_success("VIBE_ALIGNER references lean_canvas_summary.json")
    else:
        print_error("VIBE_ALIGNER does not reference lean_canvas_summary.json")
        return False

    if "LEAN_CANVAS_VALIDATOR" in content:
        print_success("VIBE_ALIGNER references LEAN_CANVAS_VALIDATOR")
    else:
        print_warning("VIBE_ALIGNER does not explicitly mention LEAN_CANVAS_VALIDATOR")

    # Test VIBE_ALIGNER task_01
    vibe_task01 = PROJECT_ROOT / "agency_os/01_planning_framework/agents/VIBE_ALIGNER/tasks/task_01_education_calibration.md"

    if not vibe_task01.exists():
        print_error("VIBE_ALIGNER task_01 not found")
        return False

    with open(vibe_task01, 'r') as f:
        content = f.read()

    if "INPUT CONTEXT CHECK" in content:
        print_success("VIBE_ALIGNER task_01 has INPUT CONTEXT CHECK")
    else:
        print_error("VIBE_ALIGNER task_01 missing INPUT CONTEXT CHECK")
        return False

    # Test LEAN_CANVAS_VALIDATOR task_03
    lcv_task03 = PROJECT_ROOT / "agency_os/01_planning_framework/agents/LEAN_CANVAS_VALIDATOR/tasks/task_03_handoff.md"

    if not lcv_task03.exists():
        print_error("LEAN_CANVAS_VALIDATOR task_03 not found")
        return False

    with open(lcv_task03, 'r') as f:
        content = f.read()

    if "VIBE_ALIGNER" in content:
        print_success("LEAN_CANVAS_VALIDATOR task_03 references VIBE_ALIGNER")
    else:
        print_error("LEAN_CANVAS_VALIDATOR task_03 missing VIBE_ALIGNER reference")
        return False

    # Test ORCHESTRATOR task_01
    orch_task01 = PROJECT_ROOT / "agency_os/00_system/agents/AGENCY_OS_ORCHESTRATOR/tasks/task_01_handle_planning.md"

    if not orch_task01.exists():
        print_error("ORCHESTRATOR task_01_handle_planning.md not found")
        return False

    with open(orch_task01, 'r') as f:
        content = f.read()

    if "BUSINESS_VALIDATION" in content and "FEATURE_SPECIFICATION" in content:
        print_success("ORCHESTRATOR task_01 has both sub-states")
    else:
        print_error("ORCHESTRATOR task_01 missing sub-state references")
        return False

    if "ROUTING DECISION TREE" in content:
        print_success("ORCHESTRATOR task_01 has routing logic")
    else:
        print_warning("ORCHESTRATOR task_01 missing routing decision tree")

    return True


def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"Planning Workflow Integration Test Suite")
    print(f"{'='*60}{Colors.RESET}\n")

    tests = [
        ("State Machine YAML", test_state_machine_yaml),
        ("Transitions", test_transitions),
        ("Data Contracts", test_data_contracts),
        ("Agent Integrations", test_agent_integrations),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"Test Summary")
    print(f"{'='*60}{Colors.RESET}\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{Colors.GREEN}✅ PASSED{Colors.RESET}" if result else f"{Colors.RED}❌ FAILED{Colors.RESET}"
        print(f"  {name}: {status}")

    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.RESET}\n")

    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Sprint 1 integration is complete.{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Some tests failed. Please review the errors above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
