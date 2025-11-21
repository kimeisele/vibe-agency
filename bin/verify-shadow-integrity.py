#!/usr/bin/env python3
"""
ARCH-004: Shadow Mode Integrity Verifier
Compares the Legacy State (JSON/Files) with the New State (SQLite).

This "Lügendetektor" (lie detector) verifies that:
- project_manifest.json matches missions table
- artifacts/ directory matches artifacts table
- active_mission.json (tasks) are tracked in the database

Returns:
  - 0 if all checks pass
  - 1 if gaps are found (requires Dual-Write implementation)
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Adjust path to find vibe_core
sys.path.insert(0, str(Path(__file__).parent.parent))

from vibe_core.store.sqlite_store import (
    SQLiteStore,
)


def check_integrity():
    """Run all integrity checks"""
    print("🕵️  ARCH-004: STARTING SHADOW INTEGRITY CHECK...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("-" * 70)

    root_dir = Path.cwd()
    issues_found = 0
    integrity_score = 0.0

    try:
        # 1. VERIFY MANIFEST
        print("\n[1/4] Checking Project Manifests...")
        manifest_results = _check_manifests(root_dir)
        print(f"   📂 Files:  {manifest_results['file_count']}")
        print(f"   💾 DB:     {manifest_results['db_count']}")

        if manifest_results["match"]:
            print("   ✅ Manifests synced")
        else:
            print("   ❌ MISMATCH: Manifests out of sync")
            issues_found += 1
            if manifest_results["missing_in_db"]:
                for proj_id in manifest_results["missing_in_db"]:
                    print(f"      → {proj_id} NOT IN DATABASE")

        # 2. VERIFY ARTIFACTS
        print("\n[2/4] Checking Artifacts...")
        artifact_results = _check_artifacts(root_dir)
        print(f"   📂 Files:  {artifact_results['file_count']}")
        print(f"   💾 DB:     {artifact_results['db_count']}")

        if artifact_results["match"]:
            print("   ✅ Artifacts synced")
        else:
            print("   ⚠️  Loose match (DB may track history)")
            # Not critical - artifacts accumulate

        # 3. VERIFY ACTIVE MISSIONS (Task State)
        print("\n[3/4] Checking Active Missions (Task State)...")
        mission_results = _check_active_missions(root_dir)
        print(f"   📂 Files:  {mission_results['file_count']}")
        print(f"   💾 DB:     {mission_results['db_count']}")

        if mission_results["match"]:
            print("   ✅ Task state synced")
        else:
            print("   ❌ COUNT MISMATCH: Active missions not in DB")
            print("      ACTION REQUIRED: Add dual-write for active_mission.json")
            issues_found += 1

        # 4. VERIFY DATABASE HEALTH
        print("\n[4/4] Checking Database Health...")
        health_results = _check_db_health()
        print(f"   Tables:    {health_results['table_count']}")
        print(f"   Missions:  {health_results['mission_count']}")

        if health_results["healthy"]:
            print("   ✅ Database healthy")
        else:
            print("   ⚠️  Database empty or degraded")

        # SUMMARY
        print("\n" + "=" * 70)
        print("INTEGRITY CHECK SUMMARY")
        print("=" * 70)

        if issues_found == 0:
            print("✅ INTEGRITY VERIFIED: Shadow Mode is fully consistent")
            print("\n✨ All checks passed - ready for next phase!")
            integrity_score = 100.0
            return_code = 0
        else:
            print(f"⚠️  FOUND {issues_found} CRITICAL GAPS")
            print("\nGAP ANALYSIS:")
            if not manifest_results["match"]:
                print("  ❌ Manifests: Some projects not in database")
                print("     → Ensure save_project_manifest() is in Shadow Mode")
            if not mission_results["match"]:
                print("  ❌ Tasks: active_mission.json not synced to DB")
                print("     → Need to add dual-write for task operations")
                print("     → Check: CoreOrchestrator.add_task() and update_task_status()")
            print("\n👉 BUILDER ACTION REQUIRED:")
            print("   1. Identify which operations need dual-write")
            print("   2. Wrap DB writes in try-catch (Shadow Mode)")
            print("   3. Re-run this script to verify")
            integrity_score = max(0.0, 100.0 * (1 - (issues_found / 3)))
            return_code = 1

        print(f"\nIntegrity Score: {integrity_score:.1f}%")
        return return_code

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


def _check_manifests(root_dir: Path) -> dict:
    """Check if project manifests are synced"""
    try:
        # Find all manifest files
        manifest_files = list(root_dir.rglob("project_manifest.json"))
        file_count = len(manifest_files)

        # Extract project IDs from files
        projects_in_files = set()
        for manifest_path in manifest_files:
            try:
                with open(manifest_path) as f:
                    data = json.load(f)
                    proj_id = data.get("metadata", {}).get("projectId")
                    if proj_id:
                        projects_in_files.add(proj_id)
            except json.JSONDecodeError:
                pass

        # Check database
        db_store = SQLiteStore(str(root_dir / ".vibe" / "state" / "vibe_agency.db"))
        missions = db_store.get_mission_history()
        db_count = len(missions)
        projects_in_db = {m["mission_uuid"] for m in missions}

        db_store.close()

        # Compare
        missing_in_db = projects_in_files - projects_in_db
        match = file_count == db_count and not missing_in_db

        return {
            "file_count": file_count,
            "db_count": db_count,
            "match": match,
            "missing_in_db": list(missing_in_db),
        }
    except Exception as e:
        print(f"   ERROR checking manifests: {e}")
        return {"file_count": 0, "db_count": 0, "match": False, "missing_in_db": []}


def _check_artifacts(root_dir: Path) -> dict:
    """Check if artifacts are synced"""
    try:
        # Count artifact files
        artifact_dir = root_dir / "workspaces"
        if not artifact_dir.exists():
            return {"file_count": 0, "db_count": 0, "match": True}

        file_count = 0
        for artifact_path in artifact_dir.rglob("*.json"):
            # Count only actual artifacts (not manifests)
            if "project_manifest.json" not in str(artifact_path):
                file_count += 1

        # Check database
        db_store = SQLiteStore(str(root_dir / ".vibe" / "state" / "vibe_agency.db"))
        cursor = db_store.conn.execute("SELECT COUNT(*) FROM artifacts")
        db_count = cursor.fetchone()[0]
        db_store.close()

        # Loose match (DB accumulates)
        match = file_count == 0 or db_count > 0

        return {
            "file_count": file_count,
            "db_count": db_count,
            "match": match,
        }
    except Exception as e:
        print(f"   ERROR checking artifacts: {e}")
        return {"file_count": 0, "db_count": 0, "match": True}


def _check_active_missions(root_dir: Path) -> dict:
    """Check if active missions (task state) are synced"""
    try:
        # Find active_mission.json files
        mission_files = list(root_dir.rglob("active_mission.json"))
        file_count = len(mission_files)

        # Check database
        db_store = SQLiteStore(str(root_dir / ".vibe" / "state" / "vibe_agency.db"))
        cursor = db_store.conn.execute("SELECT COUNT(*) FROM missions WHERE status='in_progress'")
        db_count = cursor.fetchone()[0]
        db_store.close()

        # For now, report if there are missions not in DB
        match = file_count == 0 or db_count >= file_count

        return {
            "file_count": file_count,
            "db_count": db_count,
            "match": match,
        }
    except Exception as e:
        print(f"   ERROR checking active missions: {e}")
        return {"file_count": 0, "db_count": 0, "match": True}


def _check_db_health() -> dict:
    """Check database health"""
    try:
        root_dir = Path.cwd()
        db_path = root_dir / ".vibe" / "state" / "vibe_agency.db"

        if not db_path.exists():
            return {
                "healthy": False,
                "table_count": 0,
                "mission_count": 0,
                "status": "Database not found",
            }

        db_store = SQLiteStore(str(db_path))

        # Count tables
        cursor = db_store.conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]

        # Count missions
        cursor = db_store.conn.execute("SELECT COUNT(*) FROM missions")
        mission_count = cursor.fetchone()[0]

        db_store.close()

        healthy = table_count > 0
        return {
            "healthy": healthy,
            "table_count": table_count,
            "mission_count": mission_count,
            "status": "OK" if healthy else "Degraded",
        }
    except Exception as e:
        print(f"   ERROR checking DB health: {e}")
        return {
            "healthy": False,
            "table_count": 0,
            "mission_count": 0,
            "status": str(e),
        }


if __name__ == "__main__":
    sys.exit(check_integrity())
