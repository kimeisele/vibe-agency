#!/usr/bin/env python3
"""
ARCH-004: Manifest Migration Tool
Imports existing project_manifest.json files into SQLiteStore.

This script populates the database with existing manifests that were
created before ARCH-003 Shadow Mode was implemented.

Usage:
  python3 bin/migrate-manifests-to-db.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from vibe_core.store.sqlite_store import (  # noqa: E402
    SQLiteStore,
)


def migrate_manifests():
    """Migrate all existing manifests to SQLiteStore"""
    print("📚 ARCH-004: MANIFEST MIGRATION TOOL")
    print(f"Started: {datetime.now().isoformat()}")
    print("-" * 70)

    root_dir = Path.cwd()
    db_path = root_dir / ".vibe" / "state" / "vibe_agency.db"

    # Find all manifest files
    manifest_files = list(root_dir.rglob("project_manifest.json"))
    print(f"\n🔍 Found {len(manifest_files)} manifests to migrate")

    if not manifest_files:
        print("✅ No manifests to migrate")
        return 0

    # Initialize database
    try:
        db_store = SQLiteStore(str(db_path))
        print(f"💾 Database: {db_path}")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return 1

    imported = 0
    skipped = 0
    errors = 0

    # Import each manifest
    for manifest_path in manifest_files:
        try:
            with open(manifest_path) as f:
                manifest_data = json.load(f)

            project_id = manifest_data.get("metadata", {}).get("projectId", "unknown")
            project_name = manifest_data.get("metadata", {}).get("name", "Unknown")

            # Import to database
            mission_id = db_store.import_project_manifest(manifest_data)

            if mission_id:
                print(f"  ✅ Imported: {project_id} ({project_name}) → mission_id={mission_id}")
                imported += 1
            else:
                print(f"  ⏭️  Skipped: {project_id} (already exists)")
                skipped += 1

        except json.JSONDecodeError:
            print(f"  ❌ ERROR: Invalid JSON in {manifest_path}")
            errors += 1
        except Exception as e:
            print(f"  ❌ ERROR: {project_id}: {e}")
            errors += 1

    db_store.close()

    # Summary
    print("\n" + "=" * 70)
    print("MIGRATION SUMMARY")
    print("=" * 70)
    print(f"✅ Imported: {imported}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"❌ Errors:   {errors}")

    if errors == 0:
        print("\n✨ Migration complete!")
        return 0
    else:
        print(f"\n⚠️  Migration complete with {errors} errors")
        return 1


if __name__ == "__main__":
    sys.exit(migrate_manifests())
