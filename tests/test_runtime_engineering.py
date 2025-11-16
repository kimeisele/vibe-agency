#!/usr/bin/env python3
"""Integration test for GAD-005: Runtime Engineering (Simplified)"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agency_os/00_system/orchestrator"))


def test_complete_runtime_enforcement():
    """End-to-end test: MOTD + Pre-Action Kernel"""

    print("🧪 Testing Runtime Engineering integration...")

    # COMPONENT A: Unavoidable MOTD
    print("\n1️⃣  Testing Unavoidable MOTD...")

    result = subprocess.run(["./vibe-cli", "--help"], capture_output=True, text=True, timeout=10)

    assert result.returncode == 0, "vibe-cli failed"
    assert "VIBE AGENCY" in result.stdout, "MOTD not displayed"
    print("   ✅ MOTD working")

    # COMPONENT B: Pre-Action Kernel
    print("\n2️⃣  Testing Pre-Action Kernel...")

    from core_orchestrator import CoreOrchestrator, KernelViolationError

    orchestrator = CoreOrchestrator(repo_root=Path.cwd())

    # Test kernel blocks critical operations
    try:
        orchestrator._kernel_check_save_artifact("project_manifest.json")
        assert False, "Kernel should have blocked"
    except KernelViolationError:
        pass  # Expected

    print("   ✅ Pre-Action Kernel working")

    print("\n✅ RUNTIME ENGINEERING INTEGRATION COMPLETE")


if __name__ == "__main__":
    try:
        test_complete_runtime_enforcement()
        print("\n✅ ALL INTEGRATION TESTS PASSED")
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
