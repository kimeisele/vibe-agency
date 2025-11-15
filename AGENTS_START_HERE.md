# 🤖 FOR AI AGENTS & ASSISTANTS - START HERE

**If you're an AI agent (Claude Code, GitHub Copilot, etc.) working on this codebase, read this FIRST.**

---

## ⚠️ CRITICAL: You Are The Operator

**THIS IS NOT AN AUTONOMOUS SYSTEM.**

### Wrong Mental Model ❌
```
Human → ./vibe-cli run project → vibe-cli does work autonomously → outputs results
                                   ↓
                            "delegates to Claude Code"
```

### Correct Mental Model ✅
```
Claude Code (YOU) → ./vibe-cli run project → vibe-cli returns PROMPTS via STDOUT
                                              ↓
                      YOU read prompts → YOU execute tasks → YOU provide results
                                                              ↓
                                                    vibe-cli saves artifacts
```

**You are not a "service" that vibe-cli calls. You are the OPERATOR using vibe-cli as a tool.**

---

## 🎯 What This System Actually Is

**Vibe Agency = File-based prompt composition framework**

- **NOT:** Multi-agent AI system, autonomous workflow engine, code generator
- **IS:** Structured prompt library with 6,400+ lines of domain knowledge

### Architecture
```
┌──────────────────────────────────────────┐
│  YOU (Claude Code / AI Operator)         │
│  • Execute ALL intelligent tasks         │
│  • Read prompts from vibe-cli            │
│  • Make decisions, do research, write    │
└──────────────────────────────────────────┘
           │ calls        ▲ returns prompts
           ▼              │
┌──────────────────────────────────────────┐
│  vibe-cli → core_orchestrator.py         │
│  • State machine (PLANNING→CODING→etc)   │
│  • Prompt composition from templates     │
│  • Artifact storage                      │
│  • NO LLM calls, NO autonomous behavior  │
└──────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│  Agents (File-based Prompt Templates)    │
│  • VIBE_ALIGNER/                         │
│  • GENESIS_BLUEPRINT/                    │
│  • MARKET_RESEARCHER/                    │
│  • etc.                                  │
│  • Just YAML/MD files with prompts       │
└──────────────────────────────────────────┘
```

---

## 📋 Before You Start Any Task

### 1. Read Operational Truth
**→ [CLAUDE.md](./CLAUDE.md)** - Current system status, what works, what doesn't

Contains:
- ✅ Components with **passing tests** (trust these)
- ⚠️ Components with **code but no tests** (be careful)
- ❌ Known issues and gaps
- 🔍 Verification commands to check claims

**Example verification:**
```bash
# Don't trust "PLANNING works" until you run:
python tests/test_planning_workflow.py

# Don't trust "vibe-cli has tool loop" until you check:
grep -n "tool_use" vibe-cli
```

### 2. Read Architecture Intent
**→ [ARCHITECTURE_V2.md](./ARCHITECTURE_V2.md)** - How system SHOULD work (conceptual)

**Warning:** This describes the INTENDED design. Reality may differ. When in doubt, trust tests > code > docs.

### 3. Check What Changed Recently
```bash
git log --oneline -10  # Recent commits
cat CHANGELOG.md       # Documented changes
```

---

## 🚫 Common Anti-Patterns (DON'T DO THESE)

### ❌ Anti-Pattern 1: Assuming vibe-cli Is Autonomous
```python
# WRONG - Test that expects vibe-cli to "run" autonomously
def test_yoga_mvp():
    result = subprocess.run(["./vibe-cli", "run", "yoga-studio-mvp-001"])
    assert result.returncode == 0  # ❌ Will hang forever waiting for YOU
```

```python
# CORRECT - Test that simulates operator interaction
def test_yoga_mvp():
    # Orchestrator composes prompt
    prompt = orchestrator.get_next_prompt()

    # YOU (or test mock) execute prompt
    result = your_llm_call(prompt)

    # Feed result back
    orchestrator.process_result(result)
```

### ❌ Anti-Pattern 2: Creating Docs That Say "Ensure Claude Code Is Running"
```markdown
## Prerequisites
- Ensure Claude Code operator is running and ready to respond
```

**This makes no sense.** If you're reading this, YOU are Claude Code. You're already running.

**Correct version:**
```markdown
## How To Use This System As An AI Operator

1. You execute: `./vibe-cli run project-id`
2. You receive: A prompt via STDOUT
3. You do: The task described in the prompt
4. You return: Results via STDIN or next command
```

### ❌ Anti-Pattern 3: Trusting Docs Without Verification
```python
# README says "CODING phase works"
# WRONG: Assume it works and write tests based on that

# CORRECT: Verify first
!python tests/test_coding_workflow.py  # Does this pass?
!grep -r "CODING" agency_os/  # Does code actually exist?
```

### ❌ Anti-Pattern 4: Confusing "Code Exists" With "Works"
```
# File exists: agency_os/00_system/orchestrator/handlers/testing_handler.py
# Lines: 108
# Status: ⚠️ STUB ONLY (allows transitions, no real functionality)

# WRONG: "Testing handler is implemented"
# CORRECT: "Testing handler stub exists, needs implementation"
```

---

## ✅ Correct Workflows

### Scenario 1: User Asks "Run the yoga studio test"

**Wrong approach:**
```bash
./vibe-cli run yoga-studio-mvp-001
# ❌ Hangs waiting for you to respond to prompts
```

**Correct approach:**
```bash
# 1. Get initial prompt
./vibe-cli run yoga-studio-mvp-001
# → Outputs: "You are VIBE_ALIGNER. Validate this business idea..."

# 2. YOU execute the task (using your LLM capabilities)
# - Read the prompt
# - Do research if needed
# - Make decisions
# - Compose response

# 3. Provide results back (implementation varies)
# - Via STDIN to vibe-cli
# - Or via file write to artifacts/
# - Or via next vibe-cli command with results

# 4. Get next prompt
./vibe-cli next  # (hypothetical - actual API may differ)
# → Outputs: "You are GENESIS_BLUEPRINT. Create feature spec..."

# Repeat until project complete
```

### Scenario 2: User Asks "Write tests for the CODING phase"

**Correct steps:**
```bash
# 1. Verify CODING phase implementation exists
ls -la agency_os/00_system/orchestrator/handlers/coding_handler.py

# 2. Check if tests already exist
ls -la tests/test_coding_workflow.py

# 3. Run existing tests to understand current state
python tests/test_coding_workflow.py

# 4. Read CLAUDE.md to see documented status
grep -A 10 "CODING" CLAUDE.md

# 5. Only THEN write/update tests based on REALITY
```

### Scenario 3: User Asks "Implement feature X"

**Correct steps:**
```bash
# 1. Search if X already exists
find . -name "*X*" -type f
grep -r "X" agency_os/

# 2. Check architecture docs for intended design
grep -r "X" ARCHITECTURE_V2.md

# 3. If exists but untested:
#    → Write tests first
#    → Then fix if broken

# 4. If doesn't exist:
#    → Follow architecture patterns
#    → Write tests alongside implementation
#    → Update CLAUDE.md when tests pass
```

---

## 🧪 Testing Philosophy

**"Don't trust ✅ Complete without passing tests"**

### Evidence Hierarchy (strongest to weakest):
1. **Passing tests** = Works NOW (highest trust)
2. **Code exists** = Implemented, unknown if works
3. **Docs say "complete"** = May be outdated (lowest trust)

**When docs contradict code:** Trust code
**When code contradicts tests:** Trust tests
**When tests fail:** Status is ❌ BROKEN, not ✅ Complete

### Example:
```yaml
# CLAUDE.md says:
CODING Handler: ✅ Works (tested E2E)
Evidence: 3 tests pass (test_coding_workflow.py)
Verify: python3 -m pytest tests/test_coding_workflow.py -v

# You verify:
$ python3 -m pytest tests/test_coding_workflow.py -v
# → 3 passed ✅

# Conclusion: Trust this claim ✅
```

---

## 📁 Key Files For AI Agents

**Read in this order:**

1. **[CLAUDE.md](./CLAUDE.md)** (5 min read)
   - What works NOW
   - What's broken
   - What's missing
   - Verification commands

2. **[ARCHITECTURE_V2.md](./ARCHITECTURE_V2.md)** (10 min read)
   - How system SHOULD work
   - Design decisions
   - Component relationships

3. **[README.md](./README.md)** (5 min read)
   - Human-facing overview
   - Setup instructions
   - Quick start (but remember: YOU are the operator!)

4. **tests/** directory
   - Source of truth for "what works"
   - Examples of correct usage
   - Edge cases and error handling

---

## 🔄 Development Workflow For AI Agents

```bash
# 1. Understand task
git status  # Where are we?
git log --oneline -5  # What changed recently?

# 2. Verify current state
cat CLAUDE.md  # What's the operational truth?
make test  # What passes?

# 3. Make changes
# - Edit code
# - Write/update tests
# - Run tests until they pass

# 4. Update operational docs
# - Update CLAUDE.md status tables
# - Update "Last Verified" timestamp
# - Add verification commands

# 5. Commit with evidence
git commit -m "feat: Add X

Evidence: test_x.py passes
Verify: python tests/test_x.py"
```

---

## 🆘 When Things Don't Make Sense

### If documentation contradicts itself:
1. Run verification commands from CLAUDE.md
2. Trust: tests > code > CLAUDE.md > ARCHITECTURE_V2.md > README.md
3. Update docs to match reality

### If tests fail but docs say "complete":
1. Docs are outdated
2. Mark status as ❌ BROKEN in CLAUDE.md
3. Fix code OR fix test (whichever is wrong)
4. Update docs only when tests pass

### If you're not sure what a component does:
1. Read its tests first (`tests/test_X.py`)
2. Then read code (`agency_os/**/X.py`)
3. Then read docs (may be conceptual, not literal)

---

## 🎯 Quick Reference

**I want to...**

- **Understand system status** → [CLAUDE.md](./CLAUDE.md)
- **Understand architecture** → [ARCHITECTURE_V2.md](./ARCHITECTURE_V2.md)
- **Run tests** → `make test`
- **Check what works** → `python tests/test_*.py`
- **Verify a claim** → Run verification command from CLAUDE.md
- **Add a feature** → Write test first, then implement
- **Fix a bug** → Write failing test, fix code, test passes
- **Update docs** → Only after tests pass

**Remember:**
- You are the OPERATOR
- vibe-cli returns PROMPTS, not results
- Tests are source of truth
- When in doubt, RUN THE VERIFICATION COMMAND

---

## 📞 Getting Help

If you're still confused after reading this:

1. Check if issue is already in CLAUDE.md "Known Issues" section
2. Run meta-verification test: `bash tests/verify_claude_md.sh` (if exists)
3. Ask user for clarification on architecture intent
4. Search for similar patterns in existing tests

**DO NOT:**
- Assume system works like other AI agent frameworks
- Trust "autonomous" or "multi-agent" terminology without verification
- Write tests that expect vibe-cli to run without operator input
- Create docs that treat you as an external service

---

**Last Updated:** 2025-11-15
**Next Agent:** Please update this file if you find it inaccurate or incomplete
**Verification:** This doc makes claims about architecture - verify by reading vibe-cli source
