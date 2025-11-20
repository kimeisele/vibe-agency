#!/bin/bash

###############################################################################
# verify-claude-md.sh - CLAUDE.md Consistency Verification
#
# Purpose: Validate that CLAUDE.md operational claims match reality
# Rationale: Prevent documentation drift (like show-context.sh → .py transition)
#
# Usage: ./bin/verify-claude-md.sh
# Exit: 0 if all claims verified, 1 if drift detected
###############################################################################

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

# Counters
TOTAL=0
PASSED=0
FAILED=0
SKIPPED=0

# Report file
REPORT_FILE=".claude_md_verification_report.json"

###############################################################################
# Helper Functions
###############################################################################

test_command() {
    local name="$1"
    local command="$2"
    local expected="$3"

    TOTAL=$((TOTAL + 1))

    echo -ne "Testing: $name ... "

    # Execute command and capture output
    output=$(eval "$command" 2>&1 || echo "FAILED")

    # Check if output contains expected pattern
    if echo "$output" | grep -q "$expected"; then
        echo -e "${GREEN}✅ PASS${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        FAILED=$((FAILED + 1))
        echo "  Expected pattern: '$expected'"
        echo "  Got: $(echo "$output" | head -1)"
        return 1
    fi
}

test_file_exists() {
    local name="$1"
    local file="$2"

    TOTAL=$((TOTAL + 1))

    echo -ne "Checking: $name ... "

    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ EXISTS${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ MISSING${NC}"
        FAILED=$((FAILED + 1))
        echo "  Expected file: $file"
        return 1
    fi
}

test_executable() {
    local name="$1"
    local file="$2"

    TOTAL=$((TOTAL + 1))

    echo -ne "Checking: $name ... "

    if [ -x "$file" ]; then
        echo -e "${GREEN}✅ EXECUTABLE${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ NOT EXECUTABLE${NC}"
        FAILED=$((FAILED + 1))
        echo "  File: $file"
        return 1
    fi
}

test_skip() {
    local name="$1"
    local reason="$2"

    TOTAL=$((TOTAL + 1))
    SKIPPED=$((SKIPPED + 1))

    echo -e "Skipping: $name ... ${YELLOW}⏭️  SKIP${NC}"
    echo "  Reason: $reason"
}

print_section() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}"
}

###############################################################################
# VERIFICATION TESTS
###############################################################################

print_section "SDLC PHASE HANDLERS"

test_command "PLANNING workflow" \
    "uv run pytest tests/test_planning_workflow.py -v" \
    "passed"

test_command "CODING workflow" \
    "uv run pytest tests/test_coding_workflow.py -v" \
    "passed"

test_command "DEPLOYMENT workflow" \
    "uv run pytest tests/test_deployment_workflow.py -v" \
    "passed"

# TESTING handler is a stub (expected to be minimal)
test_file_exists "TESTING handler stub" \
    "agency_os/core_system/orchestrator/handlers/testing_handler.py"

# MAINTENANCE handler is a stub (expected to be minimal)
test_file_exists "MAINTENANCE handler stub" \
    "agency_os/core_system/orchestrator/handlers/maintenance_handler.py"

print_section "CORE COMPONENTS (SDLC + Quality)"

test_command "Core Orchestrator state machine" \
    "uv run pytest tests/test_orchestrator_state_machine.py -v" \
    "passed"

test_command "File-Based Delegation (GAD-003)" \
    "uv run python tests/manual_planning_test.py" \
    "✅\|SUCCESS\|PASSED\|OK"

test_command "Session Handoff Integration" \
    "test -f '.session_handoff.json' && echo 'EXISTS'" \
    "EXISTS"

test_command "Workflow-Scoped Quality Gates (GAD-004 Phase 2)" \
    "uv run pytest tests/test_quality_gate_recording.py -v" \
    "passed"

test_command "Deployment-Scoped Validation (GAD-004 Phase 3)" \
    "uv run pytest tests/e2e/test_orchestrator_e2e.py -v" \
    "passed"

test_command "Multi-Layer Integration (GAD-004 Phase 4)" \
    "uv run pytest tests/test_multi_layer_integration.py -v" \
    "passed"

print_section "RUNTIME ENGINEERING (GAD-005)"

test_command "Unavoidable MOTD (Week 1)" \
    "uv run python tests/test_motd.py 2>&1" \
    "PASSED\|passed"

test_command "Pre-Action Kernel (Week 2)" \
    "uv run python tests/test_kernel_checks.py 2>&1" \
    "PASSED\|passed"

test_command "GAD-005 Integration (HARNESS)" \
    "uv run python tests/test_runtime_engineering.py 2>&1" \
    "PASSED\|passed"

print_section "SYSTEM INTEGRITY (GAD-005-ADDITION)"

test_command "Layer 0 Integrity Verification" \
    "uv run pytest tests/test_layer0_integrity.py -v" \
    "passed"

test_command "Layer 1 Boot Integration" \
    "uv run pytest tests/test_layer1_boot_integration.py -v" \
    "passed"

print_section "CANONICAL SCHEMAS (GAD-100 Phase 2)"

test_command "Canonical Schema Definition" \
    "uv run pytest tests/test_canonical_schemas.py -v" \
    "passed"

print_section "GOVERNANCE & AGENTS"

test_command "Prompt Registry" \
    "uv run pytest tests/test_prompt_registry.py -v" \
    "passed"

test_file_exists "VIBE_ALIGNER agent" \
    "agency_os/01_planning_framework/agents/VIBE_ALIGNER/_prompt_core.md"

test_file_exists "LEAN_CANVAS_VALIDATOR agent" \
    "agency_os/01_planning_framework/agents/LEAN_CANVAS_VALIDATOR/_prompt_core.md"

test_file_exists "GENESIS_BLUEPRINT agent" \
    "agency_os/01_planning_framework/agents/GENESIS_BLUEPRINT/_prompt_core.md"

test_file_exists "MARKET_RESEARCHER agent" \
    "agency_os/01_planning_framework/agents/research/MARKET_RESEARCHER/_prompt_core.md"

test_file_exists "TECH_RESEARCHER agent" \
    "agency_os/01_planning_framework/agents/research/TECH_RESEARCHER/_prompt_core.md"

test_file_exists "FACT_VALIDATOR agent" \
    "agency_os/01_planning_framework/agents/research/FACT_VALIDATOR/_prompt_core.md"

test_file_exists "USER_RESEARCHER agent" \
    "agency_os/01_planning_framework/agents/research/USER_RESEARCHER/_prompt_core.md"

print_section "KNOWLEDGE BASES"

test_file_exists "FAE_constraints.yaml" \
    "agency_os/01_planning_framework/knowledge/FAE_constraints.yaml"

test_file_exists "FDG_dependencies.yaml" \
    "agency_os/01_planning_framework/knowledge/FDG_dependencies.yaml"

test_file_exists "APCE_rules.yaml" \
    "agency_os/01_planning_framework/knowledge/APCE_rules.yaml"

print_section "CRITICAL SCRIPTS"

test_executable "show-context.py script" \
    "bin/show-context.py"

test_executable "pre-push-check.sh script" \
    "bin/pre-push-check.sh"

test_executable "cold-boot test script" \
    "tests/test_cold_boot.sh"

test_executable "commit-and-push.sh script" \
    "bin/commit-and-push.sh"

print_section "PERSISTENCE & HANDOFF"

test_skip "Cold Boot Test (fresh environment)" \
    "Expensive test (removes .venv, reinstalls deps). Run manually: ./tests/test_cold_boot.sh"

test_file_exists "Session Handoff JSON" \
    ".session_handoff.json"

test_file_exists "Session Handoff Schema" \
    "config/schemas/session_handoff.schema.json"

test_file_exists "Persistence Checklist in CLAUDE.md" \
    "CLAUDE.md"

print_section "DOCUMENTATION"

test_file_exists "Agent Policies Document" \
    "docs/policies/AGENT_DECISIONS.md"

test_file_exists "Test-First Policy" \
    "docs/policies/TEST_FIRST.md"

test_file_exists "Architecture Document" \
    "docs/architecture/ARCHITECTURE_MAP.md"

###############################################################################
# SUMMARY & REPORT
###############################################################################

print_section "VERIFICATION SUMMARY"

echo ""
echo -e "Total tests:     ${BLUE}$TOTAL${NC}"
echo -e "Passed:          ${GREEN}$PASSED${NC}"
echo -e "Failed:          ${RED}$FAILED${NC}"
echo -e "Skipped:         ${YELLOW}$SKIPPED${NC}"

pass_rate=$((PASSED * 100 / (TOTAL - SKIPPED)))
echo -e "Pass rate:       ${BLUE}$pass_rate%${NC}"

# Generate JSON report
cat > "$REPORT_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "total": $TOTAL,
  "passed": $PASSED,
  "failed": $FAILED,
  "skipped": $SKIPPED,
  "pass_rate": $pass_rate,
  "status": "$([ $FAILED -eq 0 ] && echo 'PASS' || echo 'FAIL')"
}
EOF

echo ""
echo -e "${BLUE}Report saved to: $REPORT_FILE${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CLAUDE.MD CLAIMS VERIFIED${NC}"
    echo ""
    echo "Documentation is in sync with reality."
    echo "No drift detected between CLAUDE.md and codebase."
    echo ""
    exit 0
else
    echo -e "${RED}❌ DOCUMENTATION DRIFT DETECTED${NC}"
    echo ""
    echo "The following claims in CLAUDE.md are FALSE:"
    echo "1. Review failed tests above"
    echo "2. Update CLAUDE.md to match reality OR"
    echo "3. Fix the code to match documentation"
    echo ""
    echo "Use this as a checklist before claiming 'VERIFIED' in CLAUDE.md."
    echo ""
    exit 1
fi
