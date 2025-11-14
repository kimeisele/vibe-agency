#!/bin/bash
set -e

echo "======================================================================="
echo "REAL-WORLD APPLICATION TEST"
echo "======================================================================="
echo ""
echo "Scenario: Agency receives 2 new clients and needs to manage both"
echo "          projects simultaneously with complete isolation."
echo ""

# Test 1: List all workspaces
echo "========================================="
echo "TEST 1: List all available workspaces"
echo "========================================="
./vibe-cli.py workspaces
echo ""

# Test 2: Switch to prabhupad_os workspace
echo "========================================="
echo "TEST 2: Activate prabhupad_os workspace"
echo "========================================="
./vibe-cli.py workspace prabhupad_os
echo ""

# Test 3: Generate prompt for prabhupad_os
echo "========================================="
echo "TEST 3: Generate prompt for prabhupad_os"
echo "========================================="
./vibe-cli.py generate VIBE_ALIGNER 01_education_calibration -o /tmp/prabhupad_prompt.md
echo ""

# Test 4: Verify prabhupad_os paths in prompt
echo "========================================="
echo "TEST 4: Verify workspace paths in prompt"
echo "========================================="
if grep -q "workspaces/prabhupad_os/artifacts" /tmp/prabhupad_prompt.md; then
    echo "✅ prabhupad_os paths found in prompt"
else
    echo "❌ FAIL: prabhupad_os paths NOT in prompt"
    exit 1
fi
echo ""

# Test 5: Switch to agency_toolkit workspace
echo "========================================="
echo "TEST 5: Switch to agency_toolkit"  
echo "========================================="
./vibe-cli.py workspace agency_toolkit
echo ""

# Test 6: Generate prompt for agency_toolkit
echo "========================================="
echo "TEST 6: Generate prompt for agency_toolkit"
echo "========================================="
./vibe-cli.py generate VIBE_ALIGNER 01_education_calibration -o /tmp/agency_toolkit_prompt.md
echo ""

# Test 7: Verify agency_toolkit paths
echo "========================================="
echo "TEST 7: Verify different workspace paths"
echo "========================================="
if grep -q "workspaces/agency_toolkit/artifacts" /tmp/agency_toolkit_prompt.md; then
    echo "✅ agency_toolkit paths found in prompt"
else
    echo "❌ FAIL: agency_toolkit paths NOT in prompt"
    exit 1
fi
echo ""

# Test 8: Verify isolation - ensure prabhupad paths NOT in agency prompt
echo "========================================="
echo "TEST 8: Verify workspace isolation"
echo "========================================="
if grep -q "workspaces/prabhupad_os" /tmp/agency_toolkit_prompt.md; then
    echo "❌ FAIL: Cross-contamination! prabhupad paths in agency prompt"
    exit 1
else
    echo "✅ Workspace isolation verified"
fi
echo ""

# Summary
echo "======================================================================="
echo "REAL-WORLD TEST RESULTS"
echo "======================================================================="
echo ""
echo "✅ Multi-workspace management: WORKING"
echo "✅ Workspace switching: WORKING"
echo "✅ Path resolution per workspace: WORKING"
echo "✅ Workspace isolation: WORKING"
echo ""
echo "🎉 FRAMEWORK IS PRODUCTION-READY FOR MULTI-CLIENT USE!"
echo ""

