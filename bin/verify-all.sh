#!/usr/bin/env bash
#
# verify-all.sh - Complete verification suite
#
# BURN THE GHEE Phase 3: Single source of truth for all verification commands
# Replaces 23 scattered bash blocks in CLAUDE.md
#
# Usage: ./bin/verify-all.sh
# Exit: 0 if all tests pass, 1 if any fail

set -euo pipefail

echo "🔍 VIBE AGENCY - COMPLETE VERIFICATION SUITE"
echo "===================================================================="
echo ""

FAILED=0
TOTAL=0
PASSED=0

run_test() {
    local name="$1"
    local cmd="$2"

    TOTAL=$((TOTAL + 1))
    echo "[$TOTAL] $name..."

    if eval "$cmd" > /dev/null 2>&1; then
        echo "  ✅ PASSED"
        PASSED=$((PASSED + 1))
    else
        echo "  ❌ FAILED"
        echo "     Debug: $cmd"
        FAILED=1
    fi
}

# Layer 0: System Integrity
echo "━━━ LAYER 0: SYSTEM INTEGRITY ━━━"
run_test "Layer 0 Integrity Tests" "pytest tests/test_layer0_integrity.py -v"
run_test "Layer 0 Performance Tests" "pytest tests/performance/test_layer0_performance.py -v"
echo ""

# Layer 1: Boot Integration
echo "━━━ LAYER 1: BOOT INTEGRATION ━━━"
run_test "Layer 1 Boot Tests" "pytest tests/test_layer1_boot_integration.py -v"
echo ""

# GAD-005: Runtime Engineering
echo "━━━ GAD-005: RUNTIME ENGINEERING ━━━"
run_test "MOTD Display Tests" "uv run python tests/test_motd.py"
run_test "Kernel Check Tests" "uv run python tests/test_kernel_checks.py"
run_test "Runtime Integration Tests" "uv run python tests/test_runtime_engineering.py"
run_test "Runtime Performance Tests" "uv run python tests/performance/test_runtime_performance.py"
echo ""

# Core Workflows
echo "━━━ CORE WORKFLOWS ━━━"
run_test "Planning Workflow" "pytest tests/test_planning_workflow.py -v"
run_test "Coding Workflow" "pytest tests/test_coding_workflow.py -v"
run_test "Deployment Workflow" "pytest tests/test_deployment_workflow.py -v"
echo ""

# GAD-004: Multi-Layer Quality Enforcement
echo "━━━ GAD-004: QUALITY ENFORCEMENT ━━━"
run_test "Quality Gate Recording" "pytest tests/test_quality_gate_recording.py -v"
run_test "Multi-Layer Integration" "pytest tests/test_multi_layer_integration.py -v"
run_test "E2E Orchestrator Tests" "pytest tests/e2e/test_orchestrator_e2e.py -v"
echo ""

# Prompt Registry
echo "━━━ PROMPT REGISTRY ━━━"
run_test "Prompt Registry Tests" "pytest tests/test_prompt_registry.py -v"
echo ""

# File-Based Delegation (GAD-003)
echo "━━━ FILE-BASED DELEGATION (GAD-003) ━━━"
run_test "Manual Planning Test" "uv run python manual_planning_test.py"
echo ""

# System Health (from health-check.sh)
echo "━━━ SYSTEM HEALTH ━━━"
run_test "System Integrity" "python scripts/verify-system-integrity.py"
run_test "Linting" "uv run ruff check . --quiet"
run_test "Formatting" "uv run ruff format --check . --quiet"
echo ""

echo "===================================================================="
echo ""
echo "📊 RESULTS:"
echo "   Total tests: $TOTAL"
echo "   Passed: $PASSED"
echo "   Failed: $((TOTAL - PASSED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ ALL VERIFICATIONS PASSED"
    echo ""
    echo "System is production-ready! 🚀"
    exit 0
else
    echo "❌ SOME VERIFICATIONS FAILED"
    echo ""
    echo "Review failed tests above and fix issues."
    echo "Run individual tests with the debug commands shown."
    exit 1
fi
