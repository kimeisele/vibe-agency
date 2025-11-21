#!/usr/bin/env python3
"""
ARCH-004: Artifact Migration Tool
Imports existing artifact files into SQLiteStore.

This script scans the workspaces/ directory and records all artifacts
in the database for queryability.

Usage:
  python3 bin/migrate-artifacts-to-db.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from vibe_core.store.sqlite_store import (
    SQLiteStore,
)


def migrate_artifacts():
    """Migrate all existing artifacts to SQLiteStore"""
    print("📦 ARCH-004: ARTIFACT MIGRATION TOOL")
    print(f"Started: {datetime.now().isoformat()}")
    print("-" * 70)

    root_dir = Path.cwd()
    db_path = root_dir / ".vibe" / "state" / "vibe_agency.db"

    # Initialize database and get missions
    try:
        db_store = SQLiteStore(str(db_path))
        missions = {m["mission_uuid"]: m["id"] for m in db_store.get_mission_history()}
        print(f"💾 Database: {db_path}")
        print(f"📚 Found {len(missions)} missions in database")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return 1

    # Define artifact patterns by type and location
    artifact_patterns = {
        "planning": ["artifacts/planning"],
        "coding": ["artifacts/coding"],
        "testing": ["artifacts/testing"],
        "deployment": ["artifacts/deployment"],
    }

    imported = 0
    skipped = 0
    errors = 0

    # Find all workspaces
    workspaces_dir = root_dir / "workspaces"
    if not workspaces_dir.exists():
        print("⚠️  No workspaces/ directory found")
        db_store.close()
        return 0

    for workspace in workspaces_dir.iterdir():
        if not workspace.is_dir():
            continue

        # Get project ID from manifest
        manifest_path = workspace / "project_manifest.json"
        if not manifest_path.exists():
            continue

        try:
            with open(manifest_path) as f:
                manifest = json.load(f)

            project_id = manifest.get("metadata", {}).get("projectId")
            if not project_id:
                continue

            mission_id = missions.get(project_id)
            if not mission_id:
                print(f"  ⏭️  Skipping {workspace.name} (project not in DB)")
                continue

            print(f"\n📂 Workspace: {workspace.name} (project_id={project_id})")

            # Find all artifacts in this workspace
            for artifact_type, dirs in artifact_patterns.items():
                for dir_path in dirs:
                    artifact_dir = workspace / dir_path
                    if not artifact_dir.exists():
                        continue
                    for artifact_path in artifact_dir.glob("**/*"):
                        if not artifact_path.is_file():
                            continue

                        try:
                            artifact_name = artifact_path.stem
                            created_at = (
                                datetime.fromtimestamp(artifact_path.stat().st_ctime).isoformat()
                                + "Z"
                            )

                            # Read metadata if it's a JSON file
                            metadata = None
                            if artifact_path.suffix == ".json":
                                try:
                                    with open(artifact_path) as f:
                                        metadata = json.load(f)
                                except json.JSONDecodeError:
                                    pass

                            # Add to database
                            artifact_id = db_store.add_artifact(
                                mission_id=mission_id,
                                artifact_type=artifact_type,
                                artifact_name=artifact_name,
                                created_at=created_at,
                                path=str(artifact_path),
                                metadata=metadata,
                            )

                            print(
                                f"  ✅ Added: {artifact_type}/{artifact_name} "
                                f"→ artifact_id={artifact_id}"
                            )
                            imported += 1

                        except Exception as e:
                            print(f"  ❌ ERROR: {artifact_path.name}: {e}")
                            errors += 1

        except json.JSONDecodeError:
            print(f"  ❌ ERROR: Invalid manifest in {workspace.name}")
            errors += 1
        except Exception as e:
            print(f"  ❌ ERROR: {workspace.name}: {e}")
            errors += 1

    db_store.close()

    # Summary
    print("\n" + "=" * 70)
    print("ARTIFACT MIGRATION SUMMARY")
    print("=" * 70)
    print(f"✅ Imported: {imported}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"❌ Errors:   {errors}")

    if errors == 0:
        print("\n✨ Artifact migration complete!")
        return 0
    else:
        print(f"\n⚠️  Artifact migration complete with {errors} errors")
        return 1


if __name__ == "__main__":
    sys.exit(migrate_artifacts())
