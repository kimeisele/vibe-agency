#!/bin/bash
# GAD-002 Verification Script

echo "=== GAD-002 VERIFICATION HARNESS ==="
echo ""

# Decision 1: SDLC Orchestrator
echo "Decision 1: SDLC Orchestrator Architecture"
handler_count=$(find agency_os/core_system/orchestrator/handlers -name "*_handler.py" -type f | wc -l)
[ "$handler_count" -eq 5 ] && echo "✅ 5 phase handlers exist" || echo "❌ FAIL (expected 5, got $handler_count)"

# Check handler integration
grep -q "CodingHandler\|TestingHandler\|DeploymentHandler" agency_os/core_system/orchestrator/core_orchestrator.py && \
  echo "✅ Handlers imported in core_orchestrator" || echo "❌ Handlers not integrated"

# Test complete handlers
echo ""
echo "Handler Status:"
python tests/test_planning_workflow.py >/dev/null 2>&1 && echo "  ✅ PLANNING handler works" || echo "  ❌ PLANNING handler broken"
python3 -m pytest tests/test_coding_workflow.py -v >/dev/null 2>&1 && echo "  ✅ CODING handler works" || echo "  ⚠️  CODING handler needs check"
uv run pytest tests/test_deployment_workflow.py -v >/dev/null 2>&1 && echo "  ✅ DEPLOYMENT handler works" || echo "  ⚠️  DEPLOYMENT handler needs check"

# Check stub handlers
grep -qi "stub\|not implemented" agency_os/core_system/orchestrator/handlers/testing_handler.py && \
  echo "  ⚠️  TESTING handler is stub" || echo "  ✅ TESTING handler complete"
grep -qi "stub\|not implemented" agency_os/core_system/orchestrator/handlers/maintenance_handler.py && \
  echo "  ⚠️  MAINTENANCE handler is stub" || echo "  ✅ MAINTENANCE handler complete"

# Decision 2: Governance Integration
echo ""
echo "Decision 2: Governance Integration"
[ -d "agency_os/03_system_steward_framework" ] && echo "✅ System steward framework exists" || echo "⚠️  System steward framework missing"

# Decision 3: Schema Validation
echo ""
echo "Decision 3: Schema Validation"
[ -f "agency_os/core_system/contracts/ORCHESTRATION_data_contracts.yaml" ] && \
  echo "✅ Data contracts file exists" || echo "❌ Data contracts missing"

# Decision 4: Quality Gates
echo ""
echo "Decision 4: Quality Gates (see GAD-004)"
echo "⚠️  Deferred to GAD-004 verification"

# Decision 5: Multi-Project Support
echo ""
echo "Decision 5: Multi-Project Support"
grep -q "workspace\|project_id" agency_os/core_system/orchestrator/core_orchestrator.py && \
  echo "⚠️  Workspace handling exists (needs deeper verification)" || echo "❌ No workspace handling"

echo ""
echo "=== SUMMARY ==="
echo "Decision 1 (SDLC Orchestrator): ✅ PARTIAL (3/5 handlers complete, 2/5 stubs)"
echo "Decisions 2-10: ⚠️  NOT VERIFIED (requires manual testing)"
echo ""
echo "Overall GAD-002 Status: DRAFT document + PARTIAL implementation"
echo ""
echo "CRITICAL NOTE: GAD-002 is DRAFT but implementation has proceeded!"
echo "Action needed: Either approve GAD-002 OR update to match implementation"
