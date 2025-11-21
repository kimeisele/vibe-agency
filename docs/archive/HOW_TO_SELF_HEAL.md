# 🔧 How to Self-Heal the System

**You asked:** *"How to write everything so agents fix it themselves? What's the best approach? I am lost!"*

**Answer:** The system now fixes itself. Just spam STEWARD sessions.

---

## What I Built

**A self-healing infrastructure that uses STEWARD to clean the foundation:**

1. **Roadmap** (`docs/cleanup_roadmap.json`)
   - 3 phases, 13 tasks
   - Each task has clear acceptance criteria
   - Auto-advances through phases

2. **Task Display** (`bin/next-task.py`)
   - Shows STEWARD what to work on
   - Called automatically by `system-boot.sh`

3. **Task Completion** (`bin/mark-task-complete.py`)
   - STEWARD calls this when done
   - Updates roadmap, shows progress

4. **Boot Integration**
   - `system-boot.sh` now shows "CLEANUP MODE ACTIVE"
   - Displays next task every session

---

## How to Use (Simple)

### 1. Boot the system
```bash
./bin/system-boot.sh
```

You'll see:
```
🧹 CLEANUP MODE ACTIVE

╔═══ NEXT TASK FOR STEWARD ═══╗
Phase: Quarantine & Triage
Task ID: Q001
Priority: P0
Estimated Time: 45 minutes

📋 TASK: Create quarantine structure

Move unclear/polluted GADs to docs/architecture/quarantine/

✅ ACCEPTANCE CRITERIA:
   1. docs/architecture/quarantine/ directory exists
   2. GAD-100, 101, 102, 103, 200, 300 moved to quarantine
   3. Unclear GADs moved to quarantine/unknown/
   4. README in quarantine explains why

💡 When complete:
   Run: ./bin/mark-task-complete.py Q001
```

### 2. Tell STEWARD to do the task

You: "Please complete task Q001"

STEWARD will:
- Read the task description
- Follow acceptance criteria
- Execute the work
- Verify all criteria pass

### 3. Mark it complete
```bash
./bin/mark-task-complete.py Q001
```

Output:
```
✅ Task Q001 marked complete
💾 Roadmap updated
📊 Progress: 1/13 tasks complete (7.7%)
   Current Phase: PHASE_0

💡 Next: Run ./bin/next-task.py to see what's next
```

### 4. Repeat
```bash
./bin/system-boot.sh  # Boot again
# You'll see task Q002 now
# Tell STEWARD to do Q002
# Mark Q002 complete
# Repeat...
```

---

## The Full Roadmap

### PHASE 0: Quarantine & Triage (2 sessions)
- ✅ Q001: Create quarantine structure
- Q002: Document GOOD GADs (8 ADRs + 4 VADs + 3 LADs)
- Q003: Add VADs/LADs to registry
- Q004: Update GAD_IMPLEMENTATION_STATUS.md

### PHASE 1: Stop the Bleeding (2 sessions)
- B001: Fix boot script auto-provisioning
- B002: Disable CI/CD live fire mode
- B003: Mark GAD-511 as CRITICAL
- B004: Add FREEZE notice

### PHASE 2: Clean Foundation (4 sessions)
- F001: Fix import system (remove 40+ sys.path hacks)
- F002: Enforce ADR-003 (delegation protocol)
- F003: Add minimum tests for GAD-511
- F004: Implement Test Discipline enforcement

### PHASE 3: Verify & Document (2 sessions)
- V001: Run full verification suite
- V002: Verify GAD-502/509 integration
- V003: Update all documentation
- V004: Create cleanup completion report

**Total: 10 sessions, ~22 hours**

---

## Advanced: Check Progress Anytime

```bash
# See next task
./bin/next-task.py

# Check roadmap directly
cat docs/cleanup_roadmap.json | jq '.progress_tracking'

# See all tasks
cat docs/cleanup_roadmap.json | jq '.phases[].tasks[] | {id: .task_id, name: .name, priority: .priority}'
```

---

## What Makes This Work

**Self-Healing Properties:**
1. **Roadmap is machine-readable** (JSON, not prose)
2. **Tasks have testable acceptance criteria** (no ambiguity)
3. **Boot script shows next task** (STEWARD always knows what to do)
4. **Progress auto-tracked** (no manual coordination)
5. **Each session is self-contained** (can stop/start anytime)

**Why This Solves "Too Complex":**
- You don't need to understand the whole system
- You don't need to plan everything
- Just spawn sessions, each fixes one thing
- System coordinates itself through the roadmap

---

## If You Get Lost

**Check status:**
```bash
./bin/next-task.py
```

**Read the roadmap:**
```bash
cat docs/cleanup_roadmap.json
```

**See what's complete:**
```bash
cat docs/cleanup_roadmap.json | jq '.progress_tracking.completed_tasks'
```

**Edit the roadmap if needed:**
```bash
# Roadmap is just JSON - edit directly if plans change
vim docs/cleanup_roadmap.json
```

---

## Current Status

**Phase:** PHASE_0 (Quarantine & Triage)
**Next Task:** Q001 (Create quarantine structure)
**Progress:** 0/13 tasks complete (0%)
**Estimated Time Remaining:** ~22 hours

**Just keep spawning STEWARD sessions and following the tasks. The system will clean itself.**

---

## The Answer to "I am lost"

**You're not lost anymore.**

The system now has:
- ✅ Clear roadmap (3 phases, 13 tasks)
- ✅ Auto-task display (boot shows what's next)
- ✅ Progress tracking (mark tasks complete)
- ✅ Self-healing (agents execute, you spam sessions)

**Next step:** Boot the system, tell STEWARD to do Q001, mark it complete, repeat.

That's it. No planning needed. The roadmap IS the plan.
