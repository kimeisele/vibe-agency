#!/usr/bin/env python3
"""
STEWARD Mission Management CLI
Manage GAD roadmap tasks and track progress toward zero technical debt

This is a wrapper around agency_os/01_interface/cli/cmd_mission.py
that adds STEWARD-specific functionality for managing the GAD roadmap.

Usage:
    ./bin/steward-mission.py status              - Show current mission status
    ./bin/steward-mission.py switch <roadmap>    - Switch roadmap (demo|gad)
"""

import shutil
import sys
from pathlib import Path

def main():
    vibe_root = Path(__file__).parent.parent
    
    if len(sys.argv) < 2:
        print("STEWARD Mission Control")
        print("=" * 60)
        print()
        print("Usage:")
        print("  ./bin/steward-mission.py status           - Show mission status")
        print("  ./bin/steward-mission.py switch <roadmap> - Switch roadmap (demo|gad)")
        print()
        print("For full mission control, use:")
        print("  python3 agency_os/01_interface/cli/cmd_mission.py")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "status":
        # Call the existing cmd_mission.py
        import subprocess
        result = subprocess.run(
            [sys.executable, "agency_os/01_interface/cli/cmd_mission.py", "status"],
            cwd=vibe_root,
        )
        sys.exit(result.returncode)
    
    elif command == "switch":
        if len(sys.argv) < 3:
            print("Usage: ./bin/steward-mission.py switch <demo|gad>")
            sys.exit(1)
        
        roadmap_name = sys.argv[2]
        roadmap_files = {
            "demo": vibe_root / ".vibe" / "config" / "roadmap.yaml",
            "gad": vibe_root / ".vibe" / "config" / "steward_roadmap.yaml",
        }
        
        if roadmap_name not in roadmap_files:
            print(f"❌ Invalid roadmap: {roadmap_name}")
            print(f"Available: {', '.join(roadmap_files.keys())}")
            sys.exit(1)
        
        source_file = roadmap_files[roadmap_name]
        target_file = vibe_root / ".vibe" / "config" / "roadmap.yaml"
        
        if not source_file.exists():
            print(f"❌ Roadmap file not found: {source_file}")
            sys.exit(1)
        
        # Backup current roadmap
        if target_file.exists():
            backup_file = vibe_root / ".vibe" / "config" / "roadmap.yaml.backup"
            shutil.copy(target_file, backup_file)
            print(f"📋 Backed up current roadmap to: {backup_file}")
        
        # Copy new roadmap
        shutil.copy(source_file, target_file)
        print(f"✅ Switched to '{roadmap_name}' roadmap")
        print(f"Location: {target_file}")
        
        # Reset mission state to start fresh with new roadmap
        state_file = vibe_root / ".vibe" / "state" / "active_mission.json"
        if state_file.exists():
            state_backup = vibe_root / ".vibe" / "state" / "active_mission.json.backup"
            shutil.copy(state_file, state_backup)
            state_file.unlink()
            print(f"📋 Reset mission state (backed up to {state_backup})")
        
        print()
        print("Next steps:")
        print("  1. Run: ./bin/steward-mission.py status")
        print("  2. Or: python3 agency_os/01_interface/cli/cmd_mission.py status")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
