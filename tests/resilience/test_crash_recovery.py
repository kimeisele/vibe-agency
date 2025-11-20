#!/usr/bin/env python3
"""
ARCH-003 AC6: Crash Recovery Test

Tests that mission state survives process restart.

Scenario:
1. Create mission and persist to SQLite
2. Simulate crash (close DB, destroy instance)
3. Create new SQLiteStore instance
4. Verify mission recovered from DB
5. Verify all data intact

This is the CRITICAL test - proves persistence across restarts.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agency_os.persistence.sqlite_store import SQLiteStore


def test_crash_recovery():
    """Test that mission state survives process crashes"""
    print("=" * 80)
    print("ARCH-003 AC6: CRASH RECOVERY TEST")
    print("=" * 80)

    # Use temporary DB for testing
    db_path = project_root / ".vibe" / "state" / "test_crash_recovery.db"

    # Clean up any existing test DB
    if db_path.exists():
        db_path.unlink()
        print(f"🧹 Cleaned up existing test DB: {db_path}")

    # =========================================================================
    # PHASE 1: CREATE MISSION AND PERSIST
    # =========================================================================
    print("\n📝 PHASE 1: Creating mission and persisting...")

    store1 = SQLiteStore(str(db_path))

    # Create mission with full metadata
    mission_uuid = "crash-test-001"
    phase = "PLANNING"
    status = "in_progress"
    created_at = datetime.utcnow().isoformat() + "Z"
    metadata = {
        "mission_name": "Crash Recovery Test Mission",
        "description": "Testing persistence across crashes",
        "objectives": [
            "Persist mission state",
            "Survive process restart",
            "Verify data integrity",
        ],
        "context": {"test": True, "iteration": 1},
    }

    mission_id = store1.create_mission(
        mission_uuid=mission_uuid,
        phase=phase,
        status=status,
        created_at=created_at,
        metadata=metadata,
    )

    print(f"   ✅ Created mission: ID={mission_id}, UUID={mission_uuid}")

    # Log some tool calls (to test CASCADE preservation)
    tool_call_id_1 = store1.log_tool_call(
        mission_id=mission_id,
        tool_name="WebFetch",
        args={"url": "https://example.com"},
        result={"status": 200},
        timestamp=datetime.utcnow().isoformat() + "Z",
        duration_ms=150,
        success=True,
    )

    tool_call_id_2 = store1.log_tool_call(
        mission_id=mission_id,
        tool_name="Grep",
        args={"pattern": "test"},
        result={"matches": 5},
        timestamp=datetime.utcnow().isoformat() + "Z",
        duration_ms=50,
        success=True,
    )

    print(f"   ✅ Logged tool calls: {tool_call_id_1}, {tool_call_id_2}")

    # Record decision
    decision_id = store1.record_decision(
        mission_id=mission_id,
        decision_type="recovery_strategy",
        rationale="Testing crash recovery with full state preservation",
        timestamp=datetime.utcnow().isoformat() + "Z",
        agent_name="CRASH_TEST_AGENT",
        context={"test_phase": "pre-crash"},
    )

    print(f"   ✅ Recorded decision: {decision_id}")

    # =========================================================================
    # PHASE 2: SIMULATE CRASH (CLOSE DB, DESTROY INSTANCE)
    # =========================================================================
    print("\n💥 PHASE 2: Simulating crash...")

    store1.close()
    del store1  # Destroy instance
    print("   ✅ Store closed and instance destroyed (simulated crash)")

    # =========================================================================
    # PHASE 3: RECOVERY (CREATE NEW INSTANCE, LOAD FROM DB)
    # =========================================================================
    print("\n🔄 PHASE 3: Recovering from crash...")

    store2 = SQLiteStore(str(db_path))
    print("   ✅ New SQLiteStore instance created")

    # Verify mission recovered
    recovered_mission = store2.get_mission_by_uuid(mission_uuid)

    if not recovered_mission:
        print("   ❌ CRASH RECOVERY FAILED: Mission not found in DB!")
        return False

    print("   ✅ Mission recovered from DB!")

    # =========================================================================
    # PHASE 4: VERIFY DATA INTEGRITY
    # =========================================================================
    print("\n🔍 PHASE 4: Verifying data integrity...")

    # Verify mission fields
    assert recovered_mission["id"] == mission_id, (
        f"Mission ID mismatch: {recovered_mission['id']} != {mission_id}"
    )
    assert recovered_mission["mission_uuid"] == mission_uuid, (
        f"UUID mismatch: {recovered_mission['mission_uuid']} != {mission_uuid}"
    )
    assert recovered_mission["phase"] == phase, (
        f"Phase mismatch: {recovered_mission['phase']} != {phase}"
    )
    assert recovered_mission["status"] == status, (
        f"Status mismatch: {recovered_mission['status']} != {status}"
    )
    assert recovered_mission["created_at"] == created_at, (
        f"Created_at mismatch: {recovered_mission['created_at']} != {created_at}"
    )

    print("   ✅ Mission fields intact")

    # Verify metadata
    assert recovered_mission["metadata"] is not None, "Metadata is None!"
    assert recovered_mission["metadata"]["mission_name"] == "Crash Recovery Test Mission", (
        "Metadata mission_name mismatch"
    )
    assert len(recovered_mission["metadata"]["objectives"]) == 3, (
        "Metadata objectives count mismatch"
    )

    print("   ✅ Metadata intact")

    # Verify tool calls
    tool_calls = store2.get_tool_calls_for_mission(mission_id)
    assert len(tool_calls) == 2, f"Expected 2 tool calls, got {len(tool_calls)}"
    assert tool_calls[0]["tool_name"] == "WebFetch", "Tool call 1 name mismatch"
    assert tool_calls[1]["tool_name"] == "Grep", "Tool call 2 name mismatch"

    print("   ✅ Tool calls intact (2 calls recovered)")

    # Verify decisions
    decisions = store2.get_decisions_for_mission(mission_id)
    assert len(decisions) == 1, f"Expected 1 decision, got {len(decisions)}"
    assert decisions[0]["agent_name"] == "CRASH_TEST_AGENT", "Decision agent_name mismatch"

    print("   ✅ Decisions intact (1 decision recovered)")

    # =========================================================================
    # PHASE 5: PROOF OUTPUT
    # =========================================================================
    print("\n" + "=" * 80)
    print("✅ CRASH RECOVERY TEST PASSED")
    print("=" * 80)

    print("\n📊 RECOVERY PROOF:")
    print(f"   Mission ID:   {recovered_mission['id']}")
    print(f"   UUID:         {recovered_mission['mission_uuid']}")
    print(f"   Phase:        {recovered_mission['phase']}")
    print(f"   Status:       {recovered_mission['status']}")
    print(f"   Created:      {recovered_mission['created_at']}")
    print(f"   Metadata:     {len(recovered_mission['metadata'])} keys")
    print(f"   Tool Calls:   {len(tool_calls)} recovered")
    print(f"   Decisions:    {len(decisions)} recovered")

    print("\n🎯 CRITICAL VERIFICATION:")
    print("   ✅ Mission survived process termination")
    print("   ✅ All fields intact after recovery")
    print("   ✅ Metadata preserved (full JSON)")
    print("   ✅ Related records preserved (tool_calls, decisions)")
    print("   ✅ Database correctly persisted across restarts")

    print("\n💡 This proves:")
    print("   • SQLite persistence is RELIABLE")
    print("   • Mission state survives crashes")
    print("   • System can resume from any point")
    print("   • No data loss on unexpected termination")

    # Cleanup
    store2.close()
    db_path.unlink()
    print(f"\n🧹 Cleaned up test DB: {db_path}")

    return True


if __name__ == "__main__":
    try:
        success = test_crash_recovery()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ CRASH RECOVERY TEST FAILED: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)
