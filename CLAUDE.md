# CLAUDE.md - Operational Snapshot

> ⚠️ **REDIRECTED TO STEWARD.md**
> This file is now a minimal stub. For complete documentation, see [STEWARD.md](./STEWARD.md).

**Status:** Minimal stub - full details in STEWARD.md

---

## 📌 Quick Reference

**For full documentation, see:**
- **[STEWARD.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/STEWARD.md)** - Single Source of Truth
- **[INDEX.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/INDEX.md)** - Documentation Hub

---

## ⚡ Essential Commands

```bash
# System boot & health
./bin/system-boot.sh                              # Bootstrap with full context
./bin/vibe status                                 # System health check

# Execute missions
uv run apps/agency/cli.py --mission "Your task"  # Autonomous mode
./bin/vibe run                                    # Interactive picker

# Development
./bin/pre-push-check.sh                           # Quality gates
./bin/show-context.py                             # Full system context
```

---

## 📚 Full Documentation

**→ See [STEWARD.md](./STEWARD.md) for:**
- Complete command reference
- System architecture
- Agent capabilities
- Quality guarantees
- Verification procedures
- All project documentation links

---

**This file is intentionally minimal. All operational details are maintained in STEWARD.md to prevent documentation drift.**
