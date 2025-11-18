#!/usr/bin/env python3
"""
Validation script for .knowledge_index.yaml
Verifies that all referenced files exist and paths are correct.
"""

import sys
from pathlib import Path

import yaml


def validate_knowledge_index(index_path: str = ".knowledge_index.yaml") -> bool:
    """
    Validates the knowledge index file.

    Returns:
        bool: True if all validations pass, False otherwise
    """
    repo_root = Path(__file__).parent.parent
    index_file = repo_root / index_path

    print(f"📋 Validating: {index_file}")
    print("=" * 60)

    # Check if index file exists
    if not index_file.exists():
        print(f"❌ ERROR: Index file not found: {index_file}")
        return False

    # Load YAML
    try:
        with open(index_file) as f:
            index_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"❌ ERROR: Invalid YAML syntax: {e}")
        return False

    print("✅ YAML syntax valid")

    # Validate structure
    required_keys = ["version", "kind", "categories"]
    for key in required_keys:
        if key not in index_data:
            print(f"❌ ERROR: Missing required key: {key}")
            return False

    print(f"✅ Required keys present: {', '.join(required_keys)}")

    # Validate version format
    version = index_data.get("version", "")
    if not version or not version.count(".") >= 2:
        print(f"⚠️  WARNING: Invalid version format: {version}")
    else:
        print(f"✅ Version: {version}")

    # Check kind
    expected_kind = "KnowledgeIndex"
    if index_data.get("kind") != expected_kind:
        print(f"⚠️  WARNING: Expected kind '{expected_kind}', got '{index_data.get('kind')}'")

    # Validate all file paths
    categories = index_data.get("categories", [])
    total_files = 0
    missing_files = []
    valid_files = []

    print("\n🔍 Validating file paths...")
    print("-" * 60)

    for category in categories:
        cat_id = category.get("id", "unknown")
        files = category.get("files", [])

        for file_entry in files:
            file_path = file_entry.get("path")
            if not file_path:
                print(f"⚠️  Category '{cat_id}': No path specified")
                continue

            total_files += 1
            full_path = repo_root / file_path

            if full_path.exists():
                valid_files.append(file_path)
                print(f"  ✅ {file_path}")
            else:
                missing_files.append(file_path)
                print(f"  ❌ MISSING: {file_path}")

    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total categories:     {len(categories)}")
    print(f"Total file references: {total_files}")
    print(f"Valid files:          {len(valid_files)} ✅")
    print(f"Missing files:        {len(missing_files)} ❌")

    if missing_files:
        print("\n❌ MISSING FILES:")
        for path in missing_files:
            print(f"  - {path}")
        return False

    # Validate query examples (if present)
    query_examples = index_data.get("queryExamples", [])
    if query_examples:
        print(f"\n✅ Query examples defined: {len(query_examples)}")
        for i, example in enumerate(query_examples, 1):
            query = example.get("query", "N/A")
            category = example.get("matchesCategory", "N/A")
            print(f'  {i}. "{query}" → {category}')

    print("\n" + "=" * 60)
    print("✅ ALL VALIDATIONS PASSED")
    print("=" * 60)
    return True


def validate_hardcoded_paths() -> bool:
    """
    Validates that all hardcoded 'agency_os/' paths still resolve.
    """
    repo_root = Path(__file__).parent.parent
    ssf_dir = repo_root / "system_steward_framework"

    print("\n🔍 Checking hardcoded paths in system_steward_framework...")
    print("=" * 60)

    if not ssf_dir.exists():
        print("⚠️  system_steward_framework directory not found")
        return True  # Not fatal

    import subprocess

    # Find all hardcoded agency_os/ references
    try:
        result = subprocess.run(
            ["grep", "-rh", "agency_os/", str(ssf_dir)], capture_output=True, text=True
        )

        if result.returncode != 0:
            print("✅ No hardcoded paths found (or grep failed)")
            return True

        # Extract unique paths
        lines = result.stdout.strip().split("\n")
        paths = set()

        for line in lines:
            # Extract agency_os/... patterns
            import re

            matches = re.findall(r'agency_os/[^\s\'"`,;)]+', line)
            paths.update(matches)

        # Validate each path (skip wildcards - they're documentation examples)
        missing_paths = []
        valid_paths = []
        skipped_wildcards = []

        for path in sorted(paths):
            # Skip wildcard paths (e.g., "agency_os/*/knowledge/") - these are documentation examples
            if "*" in path or "..." in path:
                skipped_wildcards.append(path)
                continue

            full_path = repo_root / path
            if full_path.exists():
                valid_paths.append(path)
                print(f"  ✅ {path}")
            else:
                missing_paths.append(path)
                print(f"  ❌ MISSING: {path}")

        print(f"\n📊 Hardcoded paths: {len(paths)} found")
        print(f"   Valid: {len(valid_paths)} ✅")
        print(f"   Missing: {len(missing_paths)} ❌")
        if skipped_wildcards:
            print(f"   Skipped (wildcards): {len(skipped_wildcards)} ⏭️")

        if missing_paths:
            print("\n❌ BROKEN HARDCODED PATHS:")
            for path in missing_paths:
                print(f"  - {path}")
            return False

        return True

    except Exception as e:
        print(f"⚠️  Could not check hardcoded paths: {e}")
        return True  # Non-fatal


if __name__ == "__main__":
    print("\n" + "🚀 AGENCY OS KNOWLEDGE INDEX VALIDATOR" + "\n")

    success = True

    # Validate knowledge index
    if not validate_knowledge_index():
        success = False

    # Validate hardcoded paths
    if not validate_hardcoded_paths():
        success = False

    # Exit with appropriate code
    if success:
        print("\n✅ All validations passed!")
        sys.exit(0)
    else:
        print("\n❌ Validation failed!")
        sys.exit(1)
