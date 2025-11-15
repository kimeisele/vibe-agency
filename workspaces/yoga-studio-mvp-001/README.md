# Yoga Studio Booking Platform MVP - Portfolio Test

## Overview

This is a comprehensive end-to-end (E2E) portfolio test project designed to validate the entire SDLC workflow of the vibe-agency system. The test uses realistic business requirements for a yoga studio booking SaaS platform to exercise all major system components.

## What This Test Validates

### PLANNING Phase
- ✅ Business validation with LEAN_CANVAS_VALIDATOR
- ✅ Feature specification with GENESIS_BLUEPRINT
- ✅ VIBE alignment
- ✅ Architecture design decisions

### RESEARCH Phase (NEW!)
- ✅ Market research with Google Custom Search API
- ✅ Technical research for tech stack decisions
- ✅ User research for UX insights
- ✅ Fact validation and cross-checking
- ✅ Fallback to Claude Code WebSearch if Google API unavailable

### CODING Phase
- ✅ 5-phase code generation workflow
- ✅ Quality gates (9 governance rules)
- ✅ Artifact bundling
- ✅ Production-ready code output

## Project Scope

**Business Context:**
- Full-featured yoga studio booking platform
- Competitors: Mindbody, Momoyoga, Pike13
- Target market: 35,000+ yoga studios in US
- Pricing: $50-150/month per studio

**Core Features:**
- Class schedule management
- Online booking with capacity limits
- Stripe payment integration
- Student profiles and memberships
- Email notifications
- Admin dashboard with analytics
- Mobile-responsive UI

**Budget:** $100 USD for comprehensive testing

## Quick Start

### Prerequisites
1. UV environment setup: `make install`
2. Research tools validation: `python scripts/validate_research_tools.py`
3. (Optional) Google API keys configured for enhanced research

### Run Test
```bash
./vibe-cli run yoga-studio-mvp-001
```

### Expected Duration
- **PLANNING:** 30-45 minutes
- **RESEARCH:** 15-20 minutes (with Google API)
- **CODING:** 60-90 minutes
- **Total:** 3-4 hours

## Detailed Guides

- **[TEST_EXECUTION_GUIDE.md](./TEST_EXECUTION_GUIDE.md)** - Step-by-step execution instructions
- **[RESEARCH_VALIDATION.md](./RESEARCH_VALIDATION.md)** - Research integration validation
- **[EXPECTED_ARTIFACTS.md](./EXPECTED_ARTIFACTS.md)** - Expected outputs and validation criteria

## Monitoring Progress

```bash
# Check current phase
cat workspaces/yoga-studio-mvp-001/project_manifest.json | grep projectPhase

# View real-time logs
tail -f workspaces/yoga-studio-mvp-001/logs/execution_trace.json

# List generated artifacts
ls -la workspaces/yoga-studio-mvp-001/artifacts/
```

## Success Criteria

### Artifacts Generated
- ✅ `lean_canvas.json` (business validation)
- ✅ `feature_spec.json` (detailed requirements)
- ✅ `research_summary.json` (market/tech/user insights)
- ✅ `code_gen_spec.json` (technical architecture)
- ✅ `artifact_bundle.json` (production code)

### Quality Checks
- ✅ All artifacts pass JSON schema validation
- ✅ Research insights integrated into specifications
- ✅ Quality gates pass (9 governance rules)
- ✅ Code is production-ready and deployable

## Troubleshooting

**If test hangs:**
- Check delegation requests in STDOUT
- Verify Claude Code operator is responsive
- Review logs in `workspaces/yoga-studio-mvp-001/logs/`

**If Google API fails:**
- System should automatically fallback to Claude Code WebSearch
- Check logs for "using Claude Code WebSearch" message
- Test continues without failure

**If artifacts are missing:**
- Verify quality gates passed
- Check for error messages in logs
- Ensure phase transitions completed

## Related Documentation

- [ARCHITECTURE_V2.md](../../ARCHITECTURE_V2.md) - System architecture
- [CLAUDE.md](../../CLAUDE.md) - Operational status
- [docs/testing/](../../docs/testing/) - Testing guides

## Tags

`#portfolio-test` `#e2e-validation` `#research-integration` `#saas` `#mvp`
