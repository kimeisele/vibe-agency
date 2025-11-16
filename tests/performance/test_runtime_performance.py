#!/usr/bin/env python3
"""Performance tests for GAD-005 Runtime Engineering"""

import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agency_os/00_system/orchestrator"))


def benchmark_motd_display():
    """Benchmark: MOTD display time should be < 1 second"""

    start = time.time()
    subprocess.run(["./vibe-cli", "--help"], capture_output=True, timeout=5)
    duration = time.time() - start

    print(f"📊 MOTD display time: {duration:.3f}s")

    if duration > 1.0:
        print("   ⚠️  WARNING: MOTD slower than target (1s)")
    else:
        print("   ✅ MOTD within target")

    return duration


def benchmark_kernel_check():
    """Benchmark: Kernel check should be < 50ms"""

    from core_orchestrator import CoreOrchestrator

    orchestrator = CoreOrchestrator(repo_root=Path.cwd())

    # Warm up
    orchestrator._kernel_check_save_artifact("feature_spec.json")

    # Benchmark
    start = time.time()
    for _ in range(100):
        orchestrator._kernel_check_save_artifact("feature_spec.json")
    duration = (time.time() - start) / 100 * 1000  # Convert to ms

    print(f"📊 Kernel check latency: {duration:.2f}ms (avg over 100 runs)")

    if duration > 50.0:
        print("   ⚠️  WARNING: Kernel check slower than target (50ms)")
    else:
        print("   ✅ Kernel check within target")

    return duration


def benchmark_system_status_load():
    """Benchmark: System status load should be < 200ms"""

    from core_orchestrator import CoreOrchestrator

    orchestrator = CoreOrchestrator(repo_root=Path.cwd())

    # Warm up
    orchestrator._get_system_status()

    # Benchmark
    start = time.time()
    for _ in range(50):
        orchestrator._get_system_status()
    duration = (time.time() - start) / 50 * 1000  # Convert to ms

    print(f"📊 System status load time: {duration:.2f}ms (avg over 50 runs)")

    if duration > 200.0:
        print("   ⚠️  WARNING: System status load slower than target (200ms)")
    else:
        print("   ✅ System status load within target")

    return duration


if __name__ == "__main__":
    print("⚡ GAD-005 Performance Benchmarks")
    print("=" * 60)
    print()

    try:
        # Run benchmarks
        print("1️⃣  Benchmarking MOTD display...")
        motd_time = benchmark_motd_display()
        print()

        print("2️⃣  Benchmarking Kernel checks...")
        kernel_time = benchmark_kernel_check()
        print()

        print("3️⃣  Benchmarking System status loading...")
        status_time = benchmark_system_status_load()
        print()

        # Summary
        print("=" * 60)
        print("📈 BENCHMARK SUMMARY")
        print("=" * 60)
        print(f"  MOTD Display:        {motd_time:.3f}s  (target: <1.0s)")
        print(f"  Kernel Check:        {kernel_time:.2f}ms (target: <50ms)")
        print(f"  System Status Load:  {status_time:.2f}ms (target: <200ms)")
        print()

        # Performance tests are NON-BLOCKING (always exit 0)
        print("✅ PERFORMANCE BENCHMARKS COMPLETE (non-blocking)")

        # Exit 0 even if targets not met (benchmarks are informational)
        exit(0)

    except Exception as e:
        print(f"\n❌ BENCHMARK FAILED: {e}")
        import traceback

        traceback.print_exc()

        # Still exit 0 (non-blocking)
        print("\n⚠️  Performance benchmarks failed, but non-blocking (exit 0)")
        exit(0)
