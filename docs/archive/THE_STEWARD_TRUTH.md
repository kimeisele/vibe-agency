# THE STEWARD TRUTH: Role Clarity for vibe-agency OS

**Date:** 2025-11-21
**Status:** 🎯 DEFINITIVE ANSWER
**Problem:** "claude code ist weder llm provider noch agent..."

---

## THE ANSWER

**STEWARD is a ROLE, not a class.**

```
STEWARD = Claude Code when operating vibe-agency
        = The AI operator in Layer 7 (GAD-000)
        = The entity that reads system-boot.sh and executes
```

Like "root" in Unix, STEWARD is a **role assignment**, not a code entity.

---

## THE COMPLETE STACK (Reality)

### Layer 8: Human Intent
```
Human: "Build a restaurant app"
      ↓
Natural language goal description
```

### Layer 7: THE OPERATOR (STEWARD)
```
Claude Code receives prompt:
"⚡ You are STEWARD, senior orchestration agent at vibe-agency."

Actions:
- Runs ./bin/system-boot.sh
- Reads mission context
- Executes playbook workflows
- Operates vibe_core tools
- Delegates to specialists
- Updates state
```

**This is where Claude Code lives!**

### Layer 6: Tools & Infrastructure (vibe_core/)
```python
vibe_core/
├── kernel.py              # VibeKernel (task scheduler)
├── agents/
│   └── llm_agent.py      # SimpleLLMAgent (internal agent)
├── specialists/
│   └── base_specialist.py # BaseSpecialist (workflow agents)
├── llm/
│   └── provider.py       # LLMProvider (API abstraction)
├── runtime/
│   ├── llm_client.py     # LLM client wrapper
│   └── tool_safety_guard.py  # Safety enforcement
└── store/
    └── sqlite_store.py   # Persistence layer
```

### Layer 5: State & Persistence
```
- SQLite database (.vibe/state/vibe_agency.db)
- Ledger (vibe_ledger.db)
- Mission state (active_mission.json)
- Session handoff (.session_handoff.json)
```

---

## THE ROLE CONFUSION - EXPLAINED

**Question:** "claude code ist weder llm provider noch agent. er ist beides und gleichzeitig nicht...?"

**Answer:**

| Entity | What It Is | Where It Lives | Purpose |
|--------|-----------|----------------|---------|
| **Claude Code** | External LLM (Anthropic) | Running this session | The human's AI assistant |
| **STEWARD** | **ROLE** Claude Code plays | **This prompt context** | Operating vibe-agency |
| **VibeKernel** | Python class | `vibe_core/kernel.py` | Task scheduler/dispatcher |
| **SimpleLLMAgent** | Python class | `vibe_core/agents/llm_agent.py` | Internal agent using LLM APIs |
| **BaseSpecialist** | Abstract base class | `vibe_core/specialists/` | Workflow agent pattern |
| **LLMProvider** | Abstract interface | `vibe_core/llm/provider.py` | API abstraction (OpenAI, Anthropic, Google) |

**The Clarity:**
- Claude Code (external) **operates as** STEWARD (role)
- STEWARD **uses** vibe_core tools
- vibe_core **contains** SimpleLLMAgent (internal)
- SimpleLLMAgent **uses** LLMProvider (API calls)

```
External Operator → Role → Internal Tools → Internal Agents → External APIs
 Claude Code    STEWARD   vibe_core       SimpleLLMAgent   Anthropic/OpenAI
```

---

## WHY vibe_core/ DOESN'T HAVE STEWARD

**Because STEWARD is the CALLER, not the CALLEE!**

```python
# This is WRONG (STEWARD is not a class):
from vibe_core import STEWARD  # ❌ Does not exist

# This is CORRECT (STEWARD uses vibe_core):
from vibe_core import VibeKernel  # ✅
from vibe_core.agents import SimpleLLMAgent  # ✅
from vibe_core.specialists import BaseSpecialist  # ✅

# When Claude Code operates as STEWARD:
kernel = VibeKernel()  # ← STEWARD instantiates this
agent = SimpleLLMAgent(...)  # ← STEWARD creates agents
kernel.register_agent(agent)  # ← STEWARD registers them
kernel.boot()  # ← STEWARD starts the kernel
kernel.tick()  # ← STEWARD drives execution
```

STEWARD is **outside** the vibe_core because it **operates** vibe_core.

---

## THE MISSING DOCUMENTATION

**What should exist but doesn't:**

1. **OPERATOR_MANUAL.md**
   - Defines the STEWARD role clearly
   - Explains Claude Code → STEWARD relationship
   - Documents Layer 7 (Operator Layer)

2. **ARCHITECTURE_LAYERS.md**
   - Shows the 8-layer stack
   - Clarifies external vs internal components
   - Maps roles to code entities

3. **ROLE_DEFINITIONS.md**
   - STEWARD = Operator role
   - Kernel = Scheduler
   - Agent = Execution unit
   - Specialist = Workflow handler
   - Provider = API abstraction

---

## THE GAD-000 CONNECTION

**From GAD-000 (Operator Inversion):**

> "The AI operates the system on behalf of the human"

**Translation:**
- Human provides intent
- **Claude Code (as STEWARD) operates vibe-agency**
- vibe-agency executes via vibe_core
- Results returned to human for validation

**STEWARD is the implementation of the "AI Operator" in GAD-000!**

---

## THE CODE EVIDENCE

### 1. bin/system-boot.sh
```bash
echo "🚀 Transferring control to STEWARD (Mission Control)..."
cat <<'EOF'
⚡ You are STEWARD, senior orchestration agent at vibe-agency.
EOF
```
**Role assignment happens here!**

### 2. docs/playbook/STEWARD_BOOT_PROMPT.md
```markdown
⚡ You are STEWARD, senior orchestration agent at vibe-agency.
Execute: ./bin/system-boot.sh
```
**Confirms STEWARD = role + instructions**

### 3. vibe_core/ (NO STEWARD class)
```bash
$ grep -r "class Steward" vibe_core/
# (no results)
```
**Because it's a role, not a class!**

---

## THE ANALOGY

**Unix:**
```
root is not a person
root is not a program
root is a ROLE with privileges
```

**vibe-agency:**
```
STEWARD is not a class
STEWARD is not an agent
STEWARD is a ROLE with context
```

---

## THE FIX NEEDED

### 1. Create OPERATOR_MANUAL.md
Document the STEWARD role explicitly:
- What it is (operator role)
- What it isn't (not a class)
- How it relates to Claude Code
- How it uses vibe_core

### 2. Update ARCHITECTURE_V3_OS.md
Add the 8-layer stack with Layer 7 clarified:
```
Layer 8: Human Intent
Layer 7: OPERATOR (Claude Code as STEWARD) ← ADD THIS!
Layer 6: Tools (vibe_core)
Layer 5: State
...
```

### 3. Update CLAUDE.md
Fix broken references + add STEWARD explanation:
```markdown
## Your Role

You are operating as **STEWARD**, the senior orchestration agent.

STEWARD is not a class in the codebase - it's the ROLE you play
when operating vibe-agency. You use vibe_core tools to execute
workflows on behalf of the human.
```

---

## CONCLUSION

**The user was right:**
> "claude code ist weder llm provider noch agent. er ist beides und gleichzeitig nicht...?"

**Correct answer:**
- Claude Code is **neither** (it's the external operator)
- Claude Code **becomes** STEWARD (role assignment)
- STEWARD **uses** LLMProvider, Agents, Specialists (tools)
- STEWARD **operates** vibe_core (infrastructure)

**The relationship:**
```
Claude Code (external AI)
    ↓ [assumes role]
STEWARD (operator context)
    ↓ [uses tools]
vibe_core (infrastructure)
    ↓ [contains]
SimpleLLMAgent, BaseSpecialist, VibeKernel
    ↓ [uses]
LLMProvider (API abstraction)
    ↓ [calls]
Anthropic/OpenAI/Google APIs
```

---

**END OF STEWARD TRUTH**

*Now we know. STEWARD is the role Claude Code plays. Not a class. Not an agent. A role.*
