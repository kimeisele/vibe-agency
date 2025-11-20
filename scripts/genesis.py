#!/usr/bin/env python3
"""
Genesis Protocol: Bootstrap System State
=========================================

Creates minimal valid .vibe/state/active_mission.json for system genesis (first boot).
Called automatically by bin/system-boot.sh if mission state is missing.

Philosophy:
- Minimal, valid state only (no assumptions)
- Explicit error handling (no silent failures)
- Idempotent (safe to run multiple times)
- Single responsibility (state creation only)
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def create_genesis_state() -> dict:
    """Create minimal, valid mission state for genesis."""
    return {
        "mission_id": "genesis",
        "mission_name": "Genesis Bootstrap",
        "status": "active",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "genesis_time": datetime.utcnow().isoformat() + "Z",
        "description": "Auto-generated mission state on system genesis",
        "objectives": [
            "Initialize system foundation",
            "Execute cleanup roadmap",
            "Maintain system health",
        ],
        "context": {
            "mode": "steward",
            "genesis": True,
            "version": "1.0",
        },
    }


def validate_state(state: dict) -> bool:
    """Validate that state has required fields."""
    required_fields = [
        "mission_id",
        "mission_name",
        "status",
        "created_at",
        "description",
        "objectives",
        "context",
    ]

    for field in required_fields:
        if field not in state:
            print(f"❌ GENESIS FAILED: Missing required field '{field}'", file=sys.stderr)
            return False

    return True


def genesis() -> int:
    """
    Execute Genesis Protocol: Create minimal system state.

    Returns:
        0 on success
        1 on failure
    """
    try:
        # 1. Ensure .vibe/state directory exists
        state_dir = Path(".vibe/state")
        state_dir.mkdir(parents=True, exist_ok=True)

        # 2. Check if state already exists (idempotent)
        mission_file = state_dir / "active_mission.json"
        if mission_file.exists():
            print(f"ℹ️  Mission state already exists: {mission_file}")
            return 0

        # 3. Create genesis state
        genesis_state = create_genesis_state()

        # 4. Validate state
        if not validate_state(genesis_state):
            return 1

        # 5. Write state to file
        with open(mission_file, "w") as f:
            json.dump(genesis_state, f, indent=2)

        # 6. Verify file was created
        if not mission_file.exists():
            print(f"❌ GENESIS FAILED: Could not create {mission_file}", file=sys.stderr)
            return 1

        print(f"✅ Genesis complete: {mission_file}")
        return 0

    except PermissionError as e:
        print(f"❌ GENESIS FAILED: Permission denied: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"❌ GENESIS FAILED: Invalid JSON: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ GENESIS FAILED: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(genesis())
