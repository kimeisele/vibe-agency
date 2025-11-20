# Unknown / Unclear GADs

**Status:** Quarantined pending investigation
**Created:** 2025-11-20

## Purpose

This directory is reserved for GAD documents that are:
- Referenced but don't exist as files
- Incomplete or unclear in purpose
- Cannot be verified as implemented
- Need investigation before classification

## Expected GADs (from cleanup audit)

The following GAD IDs were referenced in the system but don't exist as files:

- **GAD-105**: Status unknown
- **GAD-201-204**: Not found (may have been planned but never created)
- **GAD-301-304**: Not found
- **GAD-503-504**: Referenced but missing
- **GAD-601-602**: Mentioned but not found
- **GAD-701-702**: Status unclear
- **GAD-901-909**: Not found

## What to Do with These

When investigating legacy references to these GADs:

1. **If the GAD was never implemented:** Remove references, close related issues
2. **If the GAD exists elsewhere:** Move it here and investigate
3. **If the GAD is actually architecture:** Verify implementation, add tests, move to `/docs/architecture/`
4. **If the GAD is a feature:** Move to `quarantine/features/`

## Investigation Checklist

Before moving any GAD out of quarantine:
- [ ] Verify the decision is actually implemented in code
- [ ] Add tests that prove the architecture works
- [ ] Ensure it describes a pattern/principle, not a feature
- [ ] Check it doesn't contradict existing ADRs (especially ADR-003)

## Next Steps

This is part of the cleanup roadmap (PHASE_0: Quarantine & Triage). These unclear GADs will be investigated in later phases:
- **PHASE_1**: Stop the bleeding (Q002-Q004, B001-B004)
- **PHASE_2**: Clean foundation (F001-F004)
- **PHASE_3**: Verify completion (V001-V004)

## References

- Parent: `docs/architecture/quarantine/README.md`
- Cleanup Roadmap: `.vibe/config/cleanup_roadmap.json`
