# DOCUMENTATION REALITY CHECK
**Date:** 2025-11-21
**Status:** 🔥 CRITICAL - BROKEN REFERENCES EVERYWHERE

---

## THE PROBLEM

**CLAUDE.md references non-existent files:**
- `ARCHITECTURE_V2.md` → **DOES NOT EXIST** ❌
- `SSOT.md` → **DOES NOT EXIST** ❌

**These files are referenced in 30+ documents across the codebase!**

---

## WHAT ACTUALLY EXISTS

### Root Documentation (✅ Verified)
```
./AGENTS_START_HERE.md          ✅
./CLAUDE.md                      ✅ (but contains broken refs!)
./INDEX.md                       ✅
./README.md                      ✅
./HOW_TO_SELF_HEAL.md           ✅
```

### Architecture Documentation (✅ Verified)
```
docs/architecture/
├── ARCHITECTURE_V3_OS.md              ✅ (CURRENT - replaces V2!)
├── ARCHITECTURE_MAP.md                ✅
├── ARCHITECTURE_REGISTRY.md           ✅
├── ARCHITECTURE_GAP_ANALYSIS.md       ✅
├── KERNEL_AGENCY_SPLIT_PLAN.md        ✅
├── GAD-000_OPERATOR_INVERSION.md      ✅
├── GAD-000_COMPLIANCE_AUDIT.md        ✅
├── GAD-008_HAP_IMPLEMENTATION.md      ✅
├── GAD_IMPLEMENTATION_STATUS.md       ✅
├── STRATEGY_SHIFT.md                  ✅ (IN ROOT, not docs/)
└── (many more...)
```

### What's MISSING (❌ Not Found)
```
ARCHITECTURE_V2.md    ❌ (archived? deleted?)
SSOT.md               ❌ (never existed or deleted?)
```

---

## THE ROLE CONFUSION PROBLEM

**From user:**
> "claude code ist weder llm provider noch agent. er ist beides und gleichzeitig nicht...?"

**The Reality:**
- ✅ `vibe_core/llm/provider.py` - LLM Provider (abstract interface)
- ✅ `vibe_core/agents/llm_agent.py` - SimpleLLMAgent (uses provider)
- ✅ `vibe_core/specialists/base_specialist.py` - BaseSpecialist (HAP pattern)
- ✅ `vibe_core/kernel.py` - VibeKernel (orchestrator)
- ❓ **STEWARD** - Where is it? What is it?

---

## THE STEWARD MYSTERY

**References found:**
- `docs/playbook/STEWARD_BOOT_PROMPT.md` ✅ exists
- `bin/system-boot.sh` calls STEWARD ✅
- Boot output shows "STEWARD (Mission Control)" ✅

**But WHERE is the code?**
```bash
# Search results:
vibe_core/
├── llm/           ✅ LLM Provider abstraction
├── agents/        ✅ SimpleLLMAgent
├── specialists/   ✅ BaseSpecialist, registry
├── kernel.py      ✅ VibeKernel
└── ??? STEWARD ???  ❓ NOT FOUND IN vibe_core/
```

**Hypothesis:**
- STEWARD may be in `apps/agency/orchestrator/` (domain-specific)
- STEWARD may be a ROLE, not a class
- STEWARD may be the **boot sequence** itself (bin/system-boot.sh)

---

## BROKEN REFERENCES AUDIT

**Files referencing non-existent docs:** 30+

### Critical Files:
1. `CLAUDE.md` - Main operations manual
2. `AGENTS_START_HERE.md`
3. `INDEX.md`
4. `docs/playbook/STEWARD_BOOT_PROMPT.md`
5. `docs/architecture/*.md` (many)

---

## IMMEDIATE ACTIONS REQUIRED

### P0 - Fix CLAUDE.md
```diff
- **ARCHITECTURE_V2.md** — Conceptual model (the "should be")
- **SSOT.md** — Implementation decisions (the "is")
+ **ARCHITECTURE_V3_OS.md** — Current OS architecture (the "is")
+ **ARCHITECTURE_MAP.md** — GAD-based architecture
+ **STRATEGY_SHIFT.md** — Theater → Engineering Era pivot
```

### P1 - Define STEWARD
**Questions to answer:**
1. Is STEWARD a class, module, or role?
2. Where does STEWARD live in the codebase?
3. What is the relationship between:
   - Claude Code (the operator - external)
   - STEWARD (the orchestrator? - internal)
   - VibeKernel (the executor)
   - LLMAgent (the cognitive unit)
   - BaseSpecialist (the workflow agent)

### P2 - Fix ALL broken references
- Grep entire codebase for `ARCHITECTURE_V2.md`
- Grep entire codebase for `SSOT.md`
- Replace with correct references

---

## THE CORE QUESTION

**User's insight:**
> "claude code ist weder llm provider noch agent. er ist beides und gleichzeitig nicht...?"

**Translation:**
Claude Code (the AI operating this system) is:
- NOT an LLM Provider (it USES providers like Anthropic API)
- NOT an Agent (it OPERATES agents like SimpleLLMAgent)
- NOT a Specialist (it DELEGATES to specialists)

**So what IS Claude Code in this architecture?**

**Hypothesis:** Claude Code is the **OPERATOR** (GAD-000: Operator Inversion)
- Layer 8: Human provides intent
- **Layer 7: Claude Code (THE OPERATOR)** ← THIS IS THE MISSING LAYER!
- Layer 6: Tools/APIs (vibe_core, specialists)
- Layer 5: State (SQLite, ledger)

**The Gap:** We have infrastructure for agents, but no clear definition of WHO/WHAT operates them!

---

## NEXT STEPS

1. ✅ Document the reality (this file)
2. ⬜ Fix CLAUDE.md broken references
3. ⬜ Define STEWARD role/location clearly
4. ⬜ Map Claude Code → STEWARD → Kernel → Agents → LLM
5. ⬜ Fix all 30+ broken references
6. ⬜ Create SSOT.md (or equivalent) with CURRENT reality

---

**END OF REALITY CHECK**

*This is the truth as of 2025-11-21. No speculation. No should-be. Just IS.*
