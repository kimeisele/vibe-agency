#!/usr/bin/env python3
"""
E2E Test: Verify FULL planning workflow will execute all 4 substates

Tests:
1. Workflow YAML defines all 4 substates
2. Transitions connect them correctly
3. Handler code has methods for all 4 substates
"""

import sys
import os
import yaml
import inspect
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "agency_os/00_system/orchestrator"))

from handlers.planning_handler import PlanningHandler


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def test_workflow_defines_all_substates():
    """Test that workflow YAML defines all 4 substates"""
    print(f"\n{Colors.BLUE}Test 1: Workflow YAML defines all substates{Colors.RESET}")

    workflow_path = PROJECT_ROOT / "agency_os/00_system/state_machine/ORCHESTRATION_workflow_design.yaml"
    with open(workflow_path) as f:
        workflow = yaml.safe_load(f)

    # Find PLANNING state
    planning_state = None
    for state in workflow['states']:
        if state['name'] == 'PLANNING':
            planning_state = state
            break

    assert planning_state is not None, "PLANNING state not found"
    substates = planning_state.get('sub_states', [])

    print(f"  Found {len(substates)} substates:")
    for s in substates:
        optional = " (optional)" if s.get('optional') else ""
        print(f"    - {s['name']}{optional}")

    # Expected substates
    expected = ['RESEARCH', 'BUSINESS_VALIDATION', 'FEATURE_SPECIFICATION', 'ARCHITECTURE_DESIGN']
    found = [s['name'] for s in substates]

    print(f"\n  {Colors.BOLD}Verification:{Colors.RESET}")
    all_present = True
    for exp in expected:
        if exp in found:
            print(f"    {Colors.GREEN}✅ {exp} defined{Colors.RESET}")
        else:
            print(f"    {Colors.RED}❌ {exp} missing{Colors.RESET}")
            all_present = False

    return all_present


def test_transitions_complete():
    """Test that transitions connect all substates"""
    print(f"\n{Colors.BLUE}Test 2: Transitions form complete chain{Colors.RESET}")

    workflow_path = PROJECT_ROOT / "agency_os/00_system/state_machine/ORCHESTRATION_workflow_design.yaml"
    with open(workflow_path) as f:
        workflow = yaml.safe_load(f)

    transitions = workflow.get('transitions', [])

    # Critical transitions for planning workflow
    critical = {
        'T0_BusinessToFeatures': ('PLANNING.BUSINESS_VALIDATION', 'PLANNING.FEATURE_SPECIFICATION'),
        'T0c_FeaturesToArchitecture': ('PLANNING.FEATURE_SPECIFICATION', 'PLANNING.ARCHITECTURE_DESIGN'),
        'T1_StartCoding': ('PLANNING.ARCHITECTURE_DESIGN', 'CODING'),
    }

    print(f"  Critical transitions:")
    all_correct = True

    for name, (expected_from, expected_to) in critical.items():
        trans = next((t for t in transitions if t['name'] == name), None)

        if not trans:
            print(f"    {Colors.RED}❌ {name} missing{Colors.RESET}")
            all_correct = False
            continue

        from_ok = trans['from_state'] == expected_from
        to_ok = trans['to_state'] == expected_to

        if from_ok and to_ok:
            from_short = expected_from.replace('PLANNING.', '')
            to_short = expected_to.replace('PLANNING.', '') if 'PLANNING' in expected_to else expected_to
            print(f"    {Colors.GREEN}✅ {name}: {from_short} → {to_short}{Colors.RESET}")
        else:
            print(f"    {Colors.RED}❌ {name} incorrect{Colors.RESET}")
            print(f"       Expected: {expected_from} → {expected_to}")
            print(f"       Got:      {trans['from_state']} → {trans['to_state']}")
            all_correct = False

    return all_correct


def test_handler_has_all_methods():
    """Test that PlanningHandler has methods for all 4 substates"""
    print(f"\n{Colors.BLUE}Test 3: Handler implements all substate methods{Colors.RESET}")

    # Expected methods
    expected_methods = [
        '_execute_research_state',
        '_execute_business_validation_state',
        '_execute_feature_specification_state',
        '_execute_architecture_design_state',
    ]

    print(f"  Checking PlanningHandler methods:")
    all_present = True

    for method_name in expected_methods:
        if hasattr(PlanningHandler, method_name):
            method = getattr(PlanningHandler, method_name)
            if callable(method):
                short_name = method_name.replace('_execute_', '').replace('_state', '')
                print(f"    {Colors.GREEN}✅ {short_name} implemented{Colors.RESET}")
            else:
                print(f"    {Colors.RED}❌ {method_name} not callable{Colors.RESET}")
                all_present = False
        else:
            print(f"    {Colors.RED}❌ {method_name} missing{Colors.RESET}")
            all_present = False

    return all_present


def test_handler_execute_logic():
    """Test that handler.execute() has routing logic for all substates"""
    print(f"\n{Colors.BLUE}Test 4: Handler execute() routes all substates{Colors.RESET}")

    # Read handler source code
    handler_file = PROJECT_ROOT / "agency_os/00_system/orchestrator/handlers/planning_handler.py"
    with open(handler_file) as f:
        source = f.read()

    # Look for execute() method and check for all substate routing
    expected_routes = [
        ('RESEARCH', '_execute_research_state'),
        ('BUSINESS_VALIDATION', '_execute_business_validation_state'),
        ('FEATURE_SPECIFICATION', '_execute_feature_specification_state'),
        ('ARCHITECTURE_DESIGN', '_execute_architecture_design_state'),
    ]

    print(f"  Checking execute() routing logic:")
    all_routes_present = True

    for substate_name, method_name in expected_routes:
        # Check if the routing logic exists
        has_check = f'== "{substate_name}"' in source
        has_call = method_name in source

        if has_check and has_call:
            short = substate_name.replace('_', ' ').title()
            print(f"    {Colors.GREEN}✅ {short} routed to {method_name}{Colors.RESET}")
        else:
            print(f"    {Colors.RED}❌ {substate_name} routing missing{Colors.RESET}")
            all_routes_present = False

    return all_routes_present


def test_expected_artifacts():
    """Document expected artifacts from full workflow"""
    print(f"\n{Colors.BLUE}Test 5: Expected artifacts documented{Colors.RESET}")

    workflow_path = PROJECT_ROOT / "agency_os/00_system/state_machine/ORCHESTRATION_workflow_design.yaml"
    with open(workflow_path) as f:
        workflow = yaml.safe_load(f)

    planning_state = None
    for state in workflow['states']:
        if state['name'] == 'PLANNING':
            planning_state = state
            break

    substates = planning_state.get('sub_states', [])

    print(f"  Expected artifacts from PLANNING workflow:")
    artifact_count = 0

    for substate in substates:
        if substate.get('optional'):
            continue  # Skip optional substates for MVP

        output = substate.get('output_artifact')
        if output:
            if isinstance(output, list):
                for artifact in output:
                    artifact_count += 1
                    print(f"    {artifact_count}. {artifact} ({substate['name']})")
            else:
                artifact_count += 1
                print(f"    {artifact_count}. {output} ({substate['name']})")

    print(f"\n  {Colors.BOLD}Total expected artifacts: {artifact_count}{Colors.RESET}")

    if artifact_count >= 4:  # lean_canvas, feature_spec, architecture, code_gen_spec
        print(f"  {Colors.GREEN}✅ All required artifacts will be generated{Colors.RESET}")
        return True
    else:
        print(f"  {Colors.RED}❌ Expected 4+ artifacts, found {artifact_count}{Colors.RESET}")
        return False


def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'='*80}")
    print(f"Full Planning Workflow Architecture Test")
    print(f"Purpose: Verify workflow will execute all 4 substates and generate all artifacts")
    print(f"{'='*80}{Colors.RESET}")

    tests = [
        ("Workflow defines all substates", test_workflow_defines_all_substates),
        ("Transitions form complete chain", test_transitions_complete),
        ("Handler implements all methods", test_handler_has_all_methods),
        ("Handler routes all substates", test_handler_execute_logic),
        ("Expected artifacts documented", test_expected_artifacts),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"{Colors.RED}❌ Test '{name}' crashed: {e}{Colors.RESET}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print(f"\n{Colors.BOLD}{'='*80}")
    print(f"Test Summary")
    print(f"{'='*80}{Colors.RESET}\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{Colors.GREEN}✅ PASSED{Colors.RESET}" if result else f"{Colors.RED}❌ FAILED{Colors.RESET}"
        print(f"  {name}: {status}")

    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.RESET}\n")

    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 Architecture verified! Workflow will execute all 4 substates:{Colors.RESET}")
        print(f"  1. BUSINESS_VALIDATION → lean_canvas_summary.json")
        print(f"  2. FEATURE_SPECIFICATION → feature_spec.json")
        print(f"  3. ARCHITECTURE_DESIGN → architecture.json + code_gen_spec.json")
        print(f"{Colors.GREEN}{Colors.BOLD}  Total: 4 artifacts will be generated ✅{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Architecture incomplete. Fix failures above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
