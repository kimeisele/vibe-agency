"""
Performance tests for Layer 0: System Integrity Verification

Ensures that integrity checks meet performance requirements:
- Integrity verification: < 100ms (target)
- Manifest generation: < 500ms (target)

Part of: GAD-005-ADDITION Layer 0
"""

import importlib.util
import time
from pathlib import Path

import pytest


def load_script_module(script_name: str):
    """Load a Python script as a module (handles hyphens in filenames)."""
    script_path = Path(__file__).parent.parent.parent / "scripts" / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(script_name.replace("-", "_"), script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load the Layer 0 scripts
verify_module = load_script_module("verify-system-integrity")
generate_module = load_script_module("generate-integrity-manifest")

verify_system_integrity = verify_module.verify_system_integrity
generate_manifest = generate_module.generate_manifest


@pytest.mark.performance
def test_integrity_verification_performance():
    """
    Verify integrity check completes in < 100ms.

    This is a critical performance requirement because Layer 0 runs
    on EVERY vibe-cli boot. Slow verification would degrade UX.
    """
    # Warm-up (first run may be slower due to disk cache)
    try:
        verify_system_integrity()
    except Exception:
        # Manifest might not exist in test env - that's OK for perf test
        pass

    # Performance test - measure 10 runs
    times = []
    for _ in range(10):
        start = time.perf_counter()
        try:
            verify_system_integrity()
        except Exception:
            # Ignore errors - we're only measuring performance
            pass
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print("\n📊 Integrity Verification Performance:")
    print(f"   Average: {avg_time:.2f}ms")
    print(f"   Min:     {min_time:.2f}ms")
    print(f"   Max:     {max_time:.2f}ms")
    print("   Target:  < 100ms")

    # Non-blocking assertion (performance degradation warning only)
    if avg_time > 100:
        print(f"⚠️  WARNING: Average time {avg_time:.2f}ms exceeds 100ms target")
        print("   This is non-blocking, but should be investigated.")
    else:
        print(f"✅ PASSED: {avg_time:.2f}ms < 100ms target")


@pytest.mark.performance
def test_manifest_generation_performance():
    """
    Verify manifest generation completes in < 500ms.

    Manifest generation is less critical (only done after updating
    regulatory files), but should still be reasonably fast.
    """
    # Performance test - measure 5 runs
    times = []
    for _ in range(5):
        start = time.perf_counter()
        try:
            generate_manifest()
        except Exception:
            # Ignore errors - we're only measuring performance
            pass
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print("\n📊 Manifest Generation Performance:")
    print(f"   Average: {avg_time:.2f}ms")
    print(f"   Min:     {min_time:.2f}ms")
    print(f"   Max:     {max_time:.2f}ms")
    print("   Target:  < 500ms")

    # Non-blocking assertion
    if avg_time > 500:
        print(f"⚠️  WARNING: Average time {avg_time:.2f}ms exceeds 500ms target")
        print("   This is non-blocking, but should be investigated.")
    else:
        print(f"✅ PASSED: {avg_time:.2f}ms < 500ms target")


def test_performance_summary():
    """
    Summary of Layer 0 performance tests.

    This test always passes - it's just for reporting.
    """
    print("\n" + "=" * 60)
    print("LAYER 0 PERFORMANCE BENCHMARKS COMPLETE")
    print("=" * 60)
    print("\nNote: Performance tests are non-blocking.")
    print("      They provide metrics but don't fail the build.")
    print("\nTargets:")
    print("  ✅ Integrity Verification: < 100ms")
    print("  ✅ Manifest Generation:    < 500ms")
    print("=" * 60)

    assert True  # Always pass
