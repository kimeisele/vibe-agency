#!/bin/bash
# Cold Boot Test - Simulates fresh environment, prevents session-only fixes
# Purpose: Catch regressions like the yaml dependency issue that don't persist
#
# This test:
# 1. Removes .venv (simulates fresh session)
# 2. Runs system-boot.sh (fresh install)
# 3. Runs core tests (verify functionality)
# 4. Reports success/failure

set -e

echo "════════════════════════════════════════════════════════════════"
echo "🧊 COLD BOOT TEST - Fresh Environment Verification"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Configuration
VENV_DIR=".venv"
TEST_TIMEOUT=300  # 5 minutes
FAILED_TESTS=""
PASSED_TESTS=""

# Test 1: Verify boot script exists
echo "✓ Checking system-boot.sh exists..."
if [ ! -f "./bin/system-boot.sh" ]; then
    echo "❌ FAILED: system-boot.sh not found"
    exit 1
fi

# Test 2: Remove .venv (simulate fresh environment)
echo "✓ Removing .venv to simulate fresh environment..."
if [ -d "$VENV_DIR" ]; then
    rm -rf "$VENV_DIR"
    echo "  → Removed existing .venv"
else
    echo "  → .venv already absent (fresh state)"
fi

# Test 3: Run system-boot.sh
echo "✓ Running system-boot.sh..."
if timeout $TEST_TIMEOUT ./bin/system-boot.sh > /tmp/cold_boot.log 2>&1; then
    echo "  ✅ system-boot.sh completed successfully"
else
    echo "  ❌ system-boot.sh failed"
    tail -20 /tmp/cold_boot.log
    exit 1
fi

# Test 4: Verify .venv was created
echo "✓ Verifying .venv was created..."
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ FAILED: .venv not created by boot script"
    exit 1
fi
echo "  ✅ .venv created successfully"

# Test 5: Run core tests (critical path)
echo "✓ Running core test suite..."
CORE_TESTS=(
    "tests/test_layer0_integrity.py"
    "tests/test_planning_workflow.py"
    "tests/test_canonical_schemas.py"
)

for test in "${CORE_TESTS[@]}"; do
    if [ ! -f "$test" ]; then
        echo "  ⚠️  Skipping $test (not found)"
        continue
    fi

    echo "  Running $test..."
    if timeout $TEST_TIMEOUT uv run pytest "$test" -v --tb=short > /tmp/core_test.log 2>&1; then
        echo "    ✅ PASSED"
        PASSED_TESTS="$PASSED_TESTS\n    - $test"
    else
        echo "    ❌ FAILED"
        FAILED_TESTS="$FAILED_TESTS\n    - $test"
        tail -10 /tmp/core_test.log
    fi
done

# Test 6: Verify critical dependencies
echo "✓ Verifying critical dependencies..."
DEPS=(
    "bs4:BeautifulSoup"
    "yaml:yaml"
    "jsonschema:jsonschema"
)

for dep in "${DEPS[@]}"; do
    IFS=':' read -r import_name check_name <<< "$dep"
    if uv run python -c "import $import_name" 2>/dev/null; then
        echo "  ✅ $check_name installed"
    else
        echo "  ❌ $check_name MISSING (regression detected!)"
        FAILED_TESTS="$FAILED_TESTS\n    - Dependency: $check_name"
    fi
done

# Report results
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📊 COLD BOOT TEST RESULTS"
echo "════════════════════════════════════════════════════════════════"

if [ -z "$FAILED_TESTS" ]; then
    echo "✅ ALL TESTS PASSED"
    echo ""
    echo "Passed tests:$PASSED_TESTS"
    echo ""
    echo "Conclusion: System can boot from fresh environment successfully."
    echo "No regressions detected."
    exit 0
else
    echo "❌ SOME TESTS FAILED"
    echo ""
    echo "Failed tests:$FAILED_TESTS"
    echo ""
    echo "Conclusion: Cold boot test found regressions. See failures above."
    exit 1
fi
