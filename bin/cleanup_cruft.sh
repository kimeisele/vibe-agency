#!/bin/bash
# Cleanup Script - Run ONLY after Golden Path test PASSES
# Purpose: Archive old session artifacts and organize repo

set -e

echo "🧹 Starting cleanup..."

# Create archive directory
mkdir -p docs/archive/pre-v1.3-cruft

# Archive test files from root
echo "📦 Archiving test files..."
mv test_deep_analysis.py docs/archive/pre-v1.3-cruft/ 2>/dev/null || true
mv test_real_world.sh docs/archive/pre-v1.3-cruft/ 2>/dev/null || true
mv test_vibe_aligner.py docs/archive/pre-v1.3-cruft/ 2>/dev/null || true
mv test_workspace_fix.py docs/archive/pre-v1.3-cruft/ 2>/dev/null || true

# Archive old reports
echo "📦 Archiving old reports..."
mv ARCHITECTURE_AUDIT_REPORT.md docs/archive/pre-v1.3-cruft/ 2>/dev/null || true
mv FOUNDATION_HARDENING_PLAN.md docs/archive/pre-v1.3-cruft/ 2>/dev/null || true
mv TOKEN_CHECK.md docs/archive/pre-v1.3-cruft/ 2>/dev/null || true
mv SYNC_TO_RESEARCH.md docs/archive/pre-v1.3-cruft/ 2>/dev/null || true
mv TEST_REPORT_001_delegated_execution.md docs/archive/pre-v1.3-cruft/ 2>/dev/null || true

# Archive old release notes (consolidate to docs/releases/)
echo "📦 Organizing release notes..."
mkdir -p docs/releases
mv RELEASE_NOTES_v1.1.md docs/releases/ 2>/dev/null || true
mv RELEASE_NOTES_v1.2.md docs/releases/ 2>/dev/null || true

# Create archive README
cat > docs/archive/pre-v1.3-cruft/README.md << 'EOF'
# Pre-v1.3 Archived Files

**Date Archived:** $(date +%Y-%m-%d)
**Reason:** Cleanup for v1.3 release (Prompt Registry)

These files were from earlier development sessions and are no longer needed in root directory.

## Contents
- Test scripts (moved to /tests/ or obsolete)
- Old architecture reports (superseded by ARCHITECTURE_V2.md)
- Session-specific analysis files (historical only)

## If You Need These
- They're preserved here for reference
- Check git history for full context: \`git log --all -- [filename]\`
EOF

echo "✅ Cleanup complete!"
echo ""
echo "📋 Summary:"
echo "   - Archived test files: docs/archive/pre-v1.3-cruft/"
echo "   - Organized releases: docs/releases/"
echo ""
echo "🔍 Verify with: ls -la docs/archive/pre-v1.3-cruft/"
