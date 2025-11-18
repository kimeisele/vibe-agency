# Playbook System

**Version:** 1.0  
**Last Updated:** 2025-11-18

---

## Overview

The playbook system provides domain-specific context enrichment for STEWARD workflows. When a user expresses intent (e.g., "restaurant app"), the system automatically loads relevant domain knowledge, pre-questions, and quality gates.

## Key Components

### 1. Playbook Registry
- **File:** `_registry.yaml`
- **Purpose:** Maps user intent to playbook workflows
- **Routes:** 6+ registered (bootstrap, session_resume, restaurant_app, etc.)
- **Matching:** Tier 1 keyword-based (fast, no dependencies)

### 2. Domain Playbooks
- **Location:** `domains/**/*.yaml`
- **Structure:** YAML files with metadata, pre-questions, quality gates
- **Example:** `domains/hospitality/restaurant.yaml`

### 3. Core Playbooks
- **Location:** `core/*.md`
- **Purpose:** System-level workflows (bootstrap, session_resume, status_check)

## Boot Integration

The playbook system is integrated into the boot sequence:

```bash
./bin/system-boot.sh
  ├─ Pre-flight checks
  └─ python3 ./vibe-cli boot
      ├─ Display MOTD (system health)
      ├─ Load playbook registry
      ├─ Show available routes
      └─ Ready for user intent
```

## Usage

### For Users

**Manual prompt (single entry point):**
```
⚡ You are STEWARD, senior orchestration agent at vibe-agency.

Execute: ./bin/system-boot.sh

⁉️ Fallback: python3 ./vibe-cli boot
```

**Available intents:**
- "restaurant app" → Loads restaurant domain context
- "continue work" → Resumes from session handoff
- "status" → Shows current project status
- "healthcare app" → Loads healthcare domain context
- "online store" → Loads e-commerce domain context

### For Developers

**Test playbook matching:**
```bash
python3 ./vibe-cli match "restaurant app"
python3 ./vibe-cli match "continue work"
```

**Add a new playbook:**
1. Create playbook YAML in `domains/<domain>/<name>.yaml`
2. Add route to `_registry.yaml`
3. Test with `python3 ./vibe-cli match "<intent>"`
4. Run tests: `python3 -m pytest tests/test_boot_mode.py -v`

## Related Documentation

- **Boot Prompt:** `STEWARD_BOOT_PROMPT.md` - Complete boot system guide
- **User Guide:** `USER_PLAYBOOK.md` - User-facing documentation
- **Architecture:** `../../ARCHITECTURE_V2.md` - System architecture
- **SSOT:** `../../SSOT.md` - Implementation decisions

## Version History

- **v1.0** (2025-11-18): Initial implementation with boot integration
