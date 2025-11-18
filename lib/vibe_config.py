"""
VibeConfig - Unified access to .vibe/ state

This is the GAD-100 Phase 3 "thin wrapper" that exposes:
- System integrity status (.vibe/system_integrity_manifest.json)
- Recent receipts (.vibe/receipts/)
- Session handoff (.session_handoff.json)

Architecture:
- Read-only by default (mutations are rare)
- Returns typed dicts (no custom classes yet)
- Fails fast with clear errors
- Zero dependencies beyond stdlib

Related: GAD-500 (defines .vibe/ structure), GAD-800 (integration matrix)
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class VibeConfig:
    """Unified access to .vibe/ state and session data."""

    def __init__(self, repo_root: Path | None = None):
        """
        Initialize VibeConfig.

        Args:
            repo_root: Repository root (defaults to cwd)
        """
        self.repo_root = Path(repo_root or Path.cwd())
        self.vibe_dir = self.repo_root / ".vibe"

        # Ensure .vibe/ exists
        if not self.vibe_dir.exists():
            raise FileNotFoundError(
                f".vibe/ directory not found at {self.vibe_dir}\n"
                "Has GAD-500 Layer 0 been initialized?"
            )

    # ========================================
    # SYSTEM INTEGRITY (GAD-500 Layer 0)
    # ========================================

    def get_system_integrity(self) -> dict[str, Any]:
        """
        Get system integrity status from .vibe/system_integrity_manifest.json

        Returns:
            {
                "status": "VERIFIED" | "COMPROMISED" | "UNKNOWN",
                "checksums": {"file": "sha256", ...},
                "last_verified": "ISO timestamp",
                "violations": [{"file": "...", "expected": "...", "actual": "..."}]
            }

        Related: scripts/verify-system-integrity.py (writes this file)
        """
        manifest_file = self.vibe_dir / "system_integrity_manifest.json"

        if not manifest_file.exists():
            return {
                "status": "UNKNOWN",
                "error": f"Manifest not found: {manifest_file}",
                "hint": "Run: python scripts/generate-integrity-manifest.py",
            }

        try:
            with open(manifest_file) as f:
                data = json.load(f)

            # Validate required fields
            if "checksums" not in data:
                return {"status": "UNKNOWN", "error": "Invalid manifest: missing 'checksums' field"}

            # Check if manifest has status field (newer format)
            status = data.get("status", "UNKNOWN")

            return {
                "status": status,
                "checksums": data.get("checksums", {}),
                "last_verified": data.get("last_verified", "never"),
                "violations": data.get("violations", []),
            }

        except json.JSONDecodeError as e:
            return {"status": "UNKNOWN", "error": f"Invalid JSON in manifest: {e}"}

    def is_system_healthy(self) -> bool:
        """
        Quick boolean check: is system in good state?

        Returns:
            True if integrity verified and no critical issues
        """
        integrity = self.get_system_integrity()
        return integrity["status"] == "VERIFIED"

    # ========================================
    # RECEIPTS (GAD-500 Layer 2)
    # ========================================

    def get_recent_receipts(self, limit: int = 5) -> list[dict[str, Any]]:
        """
        Get recent receipts from .vibe/receipts/

        Args:
            limit: Max number of receipts to return

        Returns:
            List of receipt dicts, sorted by timestamp (newest first)
        """
        receipts_dir = self.vibe_dir / "receipts"

        if not receipts_dir.exists():
            return []

        # Find all receipt files
        receipt_files = list(receipts_dir.glob("*.json"))

        # Sort by modification time (newest first)
        receipt_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        # Load and return
        receipts = []
        for receipt_file in receipt_files[:limit]:
            try:
                with open(receipt_file) as f:
                    receipt = json.load(f)
                    receipts.append(receipt)
            except Exception as e:
                # Skip corrupted receipts
                print(f"Warning: Skipping corrupted receipt {receipt_file}: {e}")
                continue

        return receipts

    def get_last_receipt(self) -> dict[str, Any] | None:
        """Get most recent receipt (convenience method)."""
        receipts = self.get_recent_receipts(limit=1)
        return receipts[0] if receipts else None

    # ========================================
    # SESSION HANDOFF
    # ========================================

    def get_session_handoff(self) -> dict[str, Any] | None:
        """
        Get current session handoff from .session_handoff.json

        Returns:
            Session handoff dict or None if file doesn't exist

        Note: Uses NEW 4-layer format (schema v2.0_4layer)
        """
        handoff_file = self.repo_root / ".session_handoff.json"

        if not handoff_file.exists():
            return None

        try:
            with open(handoff_file) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid handoff JSON: {e}")
            return None

    def get_handoff_summary(self) -> dict[str, Any]:
        """
        Get human-friendly summary of session handoff.

        Returns:
            {
                "state": "complete" | "blocked" | "in-progress",
                "from": "Agent name",
                "date": "YYYY-MM-DD",
                "summary": "Completed summary text",
                "todos": ["Task 1", "Task 2", ...],
                "blocker": "Blocker description" or None
            }
        """
        handoff = self.get_session_handoff()

        if not handoff:
            return {"state": "unknown", "error": "No session handoff found"}

        # Extract from 4-layer format
        layer0 = handoff.get("layer0_bedrock", {})
        layer1 = handoff.get("layer1_runtime", {})

        return {
            "state": layer0.get("state", "unknown"),
            "from": layer0.get("from", "Unknown"),
            "date": layer0.get("date", "Unknown"),
            "summary": layer1.get("completed_summary", ""),
            "todos": layer1.get("todos", []),
            "blocker": layer0.get("blocker"),
        }

    # ========================================
    # COMBINED STATUS (The "One Command" Query)
    # ========================================

    def get_full_status(self) -> dict[str, Any]:
        """
        Get complete system status (integrity + receipts + handoff).

        This is the "one command" that gives you everything.

        Returns:
            {
                "integrity": {...},
                "receipts": [...],
                "handoff": {...},
                "healthy": bool,
                "timestamp": "ISO timestamp"
            }
        """
        return {
            "integrity": self.get_system_integrity(),
            "receipts": self.get_recent_receipts(limit=3),
            "handoff": self.get_handoff_summary(),
            "healthy": self.is_system_healthy(),
            "timestamp": datetime.now(UTC).isoformat(),
        }
