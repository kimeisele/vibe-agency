#!/usr/bin/env python3
"""
ARCH-006 Verification: Agent Sub-Task Persistence
"""

import os
import sys
import uuid

sys.path.append(os.getcwd())

from vibe_core.store.sqlite_store import SQLiteStore


def test_hierarchy():
    print("🧪 TESTING ARCH-006: Agent Sub-Tasks...")

    # 1. Setup - Use in-memory DB for testing
    print("   👉 Setting up in-memory database...")
    db = SQLiteStore(":memory:")

    # 2. Create Root Task (Simulation of Orchestrator)
    root_id = "root-mission-001"
    print("   👉 Creating root task...")
    try:
        db.add_task(root_id, "Root Mission", None, "in_progress")
        print(f"      Root Task ID: {root_id}")
    except Exception as e:
        print(f"❌ FAILURE: Could not create root task: {e}")
        sys.exit(1)

    # 3. Create subtask (simulating agent.create_subtask)
    print("   👉 Creating subtask...")

    sub_id = str(uuid.uuid4())
    try:
        db.add_task(sub_id, "Analyze requirements", root_id, "pending")
        print(f"      Subtask ID: {sub_id}")
    except Exception as e:
        print(f"❌ FAILURE: Could not create subtask: {e}")
        sys.exit(1)

    # 4. Update subtask (simulating agent.update_subtask)
    print("   👉 Updating subtask status to completed...")
    try:
        db.update_task_status(sub_id, "completed", result="Analysis Done")
    except Exception as e:
        print(f"❌ FAILURE: Could not update subtask: {e}")
        sys.exit(1)

    # 5. Verify in DB
    print("   🔍 Verifying DB state...")
    try:
        task = db.get_task(sub_id)
        if not task:
            print("❌ FAILURE: Task not found in database.")
            sys.exit(1)

        status = task["status"]
        parent = task["parent_id"]
        result = task.get("result")

        print(f"      DB Record: Status={status}, Parent={parent}, Result={result}")

        if status == "completed" and parent == root_id and result == "Analysis Done":
            print("✅ SUCCESS: Hierarchy persisted correctly.")
        else:
            print("❌ FAILURE: Data mismatch.")
            print(f"         Expected: status=completed, parent={root_id}, result='Analysis Done'")
            print(f"         Got: status={status}, parent={parent}, result={result}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ FAILURE: Error verifying DB state: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # 6. Test get_subtasks method
    print("   🔍 Testing get_subtasks method...")
    try:
        subtasks = db.get_subtasks(root_id)
        if len(subtasks) != 1:
            print(f"❌ FAILURE: Expected 1 subtask, got {len(subtasks)}")
            sys.exit(1)

        if subtasks[0]["id"] != sub_id:
            print("❌ FAILURE: Subtask ID mismatch")
            sys.exit(1)

        print(f"      Found {len(subtasks)} subtask(s) for root task")
        print("✅ SUCCESS: get_subtasks works correctly.")

    except Exception as e:
        print(f"❌ FAILURE: Error testing get_subtasks: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Close DB
    db.close()

    print("\n✅ ALL TESTS PASSED!")


if __name__ == "__main__":
    test_hierarchy()
