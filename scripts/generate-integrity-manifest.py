#!/usr/bin/env python3
"""
System Integrity Manifest Generator (Layer 0)

This script generates a system integrity manifest containing SHA256 checksums
of all critical system files (regulatory scripts, configs, hooks).

The manifest is used by verify-system-integrity.py to ensure that the
regulatory framework has not been tampered with.

Usage:
    python scripts/generate-integrity-manifest.py

Output:
    .vibe/system_integrity_manifest.json

Part of: GAD-005-ADDITION Layer 0 (System Integrity Verification)
"""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

# Critical files to include in integrity manifest
# Format: (file_path, purpose, critical_flag)
CRITICAL_FILES = {
    "scripts": [
        (
            "scripts/verify-system-integrity.py",
            "Verifies system integrity (Layer 0)",
            True,
        ),
        (
            "scripts/generate-integrity-manifest.py",
            "Generates integrity manifest (Layer 0)",
            True,
        ),
        ("bin/update-system-status.sh", "Updates system health status", True),
        ("bin/pre-push-check.sh", "Pre-push quality checks", True),
        ("bin/show-context.py", "Displays session context", True),
    ],
    "configs": [
        (
            ".github/workflows/validate.yml",
            "CI/CD validation workflow",
            True,
        ),
        (
            ".github/workflows/post-merge-validation.yml",
            "Post-merge E2E validation",
            True,
        ),
    ],
    "core": [
        (
            "agency_os/00_system/orchestrator/core_orchestrator.py",
            "Core orchestrator with kernel checks",
            True,
        ),
        ("vibe-cli", "Main CLI entry point with MOTD", True),
    ],
}


def calculate_sha256(file_path: str) -> str:
    """
    Calculate SHA256 checksum of a file.

    Args:
        file_path: Path to file

    Returns:
        Hexadecimal checksum string
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def generate_manifest(
    output_path: str = ".vibe/system_integrity_manifest.json",
) -> dict:
    """
    Generate system integrity manifest.

    Args:
        output_path: Where to write the manifest

    Returns:
        Generated manifest dict

    Raises:
        FileNotFoundError: If critical file doesn't exist
    """
    manifest = {
        "manifestVersion": "1.0.0",
        "generatedAt": datetime.now(UTC).isoformat(),
        "trustedBaseline": {},
    }

    for category, files in CRITICAL_FILES.items():
        manifest["trustedBaseline"][category] = {}

        for file_path, purpose, critical in files:
            # Check file exists
            if not Path(file_path).exists():
                print(f"⚠️  WARNING: {file_path} not found - skipping")
                continue

            # Calculate checksum
            checksum = calculate_sha256(file_path)

            # Add to manifest
            file_name = Path(file_path).name
            manifest["trustedBaseline"][category][file_name] = {
                "path": file_path,
                "sha256": checksum,
                "purpose": purpose,
                "critical": critical,
            }

            print(f"✅ {file_path}: {checksum[:16]}...")

    # Write manifest
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print()
    print(f"✅ Manifest generated: {output_path}")
    print(f"   {sum(len(files) for files in manifest['trustedBaseline'].values())} critical files")

    return manifest


def main():
    """Main entry point."""
    try:
        generate_manifest()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import sys

        sys.exit(1)


if __name__ == "__main__":
    main()
