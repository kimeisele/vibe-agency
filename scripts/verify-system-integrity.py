#!/usr/bin/env python3
"""
System Integrity Verification (Layer 0)

This script verifies that all critical system files (regulatory scripts,
configuration files, and hooks) match their trusted checksums defined in
the system integrity manifest.

Purpose: Ensures "Who watches the watchmen?" - validates that the
         regulatory system itself has not been tampered with.

Usage:
    python scripts/verify-system-integrity.py

Returns:
    Exit 0: All checks passed (integrity verified)
    Exit 1: Integrity check failed or critical error

Part of: GAD-005-ADDITION Layer 0 (System Integrity Verification)
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, Tuple


class SystemIntegrityError(Exception):
    """Raised when system integrity check fails."""

    pass


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


def verify_system_integrity(
    manifest_path: str = ".vibe/system_integrity_manifest.json",
) -> Tuple[bool, Dict]:
    """
    Verify that all critical system files match their trusted checksums.

    Args:
        manifest_path: Path to system integrity manifest

    Returns:
        Tuple of (success: bool, report: dict)
        - success: True if all files verified, False otherwise
        - report: Dict with keys 'verified', 'failed', 'missing'

    Raises:
        SystemIntegrityError: If manifest file not found
    """
    # Load manifest
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except FileNotFoundError:
        raise SystemIntegrityError(
            f"❌ CRITICAL: System integrity manifest not found at {manifest_path}\n"
            f"   This file defines the trusted baseline for regulatory scripts.\n"
            f"   Run: python scripts/generate-integrity-manifest.py"
        )

    baseline = manifest["trustedBaseline"]
    report = {"verified": [], "failed": [], "missing": []}

    # Verify each category
    for category in ["scripts", "configs", "hooks"]:
        for name, spec in baseline.get(category, {}).items():
            file_path = spec["path"]
            expected_checksum = spec["sha256"]

            # Check if file exists
            if not Path(file_path).exists():
                report["missing"].append({"file": file_path, "purpose": spec["purpose"]})
                continue

            # Calculate current checksum
            current_checksum = calculate_sha256(file_path)

            # Compare
            if current_checksum == expected_checksum:
                report["verified"].append(file_path)
            else:
                report["failed"].append(
                    {
                        "file": file_path,
                        "purpose": spec["purpose"],
                        "expected": expected_checksum,
                        "actual": current_checksum,
                        "critical": spec.get("critical", False),
                    }
                )

    # Determine success
    success = len(report["failed"]) == 0 and len(report["missing"]) == 0

    return success, report


def print_integrity_report(success: bool, report: Dict) -> None:
    """
    Print human-readable integrity report.

    Args:
        success: Whether integrity check passed
        report: Report dict from verify_system_integrity()
    """
    if success:
        print("✅ SYSTEM INTEGRITY: VERIFIED")
        print(f"   {len(report['verified'])} critical files verified")
        return

    print("❌ SYSTEM INTEGRITY: COMPROMISED")
    print()

    if report["failed"]:
        print("🚨 FAILED CHECKSUMS:")
        for failure in report["failed"]:
            print(f"   • {failure['file']}")
            print(f"     Purpose: {failure['purpose']}")
            print(f"     Expected: {failure['expected'][:16]}...")
            print(f"     Actual:   {failure['actual'][:16]}...")
            if failure["critical"]:
                print("     ⚠️  CRITICAL: This file is essential for system regulation")
            print()

    if report["missing"]:
        print("🚨 MISSING FILES:")
        for missing in report["missing"]:
            print(f"   • {missing['file']}")
            print(f"     Purpose: {missing['purpose']}")
            print()

    print("⛔ SYSTEM HALTED: Integrity verification failed")
    print("   The system's self-regulation is compromised.")
    print("   DO NOT PROCEED until integrity is restored.")
    print()
    print("Remediation:")
    print("  1. Check git history: git log <file>")
    print("  2. Restore from baseline: git checkout HEAD -- <file>")
    print("  3. If changes are intentional:")
    print("     a. Verify changes are correct")
    print("     b. Regenerate manifest: python scripts/generate-integrity-manifest.py")


def main():
    """Main entry point."""
    try:
        success, report = verify_system_integrity()
        print_integrity_report(success, report)

        if not success:
            sys.exit(1)

        sys.exit(0)

    except SystemIntegrityError as e:
        print(str(e))
        sys.exit(1)
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
