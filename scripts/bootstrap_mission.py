#!/usr/bin/env python3
"""
Bootstrap Mission State
Creates minimal .vibe/state/active_mission.json for system boot.
Called automatically by bin/system-boot.sh if mission state missing.
"""

import json
import sys
from pathlib import Path


def bootstrap_mission():
    """Create minimal active_mission.json for first boot."""

    # Ensure .vibe/state directory exists
    state_dir = Path(".vibe/state")
    state_dir.mkdir(parents=True, exist_ok=True)

    # Create minimal mission state
    mission_state = {
        "mission_id": "default",
        "mission_name": "Default Mission",
        "status": "active",
        "created_at": "auto-generated",
        "description": "Auto-generated mission state for system boot",
        "objectives": [
            "Complete cleanup roadmap tasks",
            "Maintain system health",
            "Execute strategic priorities",
        ],
        "context": {"mode": "steward", "auto_provisioned": True},
    }

    # Write mission state
    mission_file = state_dir / "active_mission.json"
    with open(mission_file, "w") as f:
        json.dump(mission_state, f, indent=2)

    print(f"✅ Mission state bootstrapped: {mission_file}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(bootstrap_mission())
    except Exception as e:
        print(f"❌ Failed to bootstrap mission: {e}", file=sys.stderr)
        sys.exit(1)
