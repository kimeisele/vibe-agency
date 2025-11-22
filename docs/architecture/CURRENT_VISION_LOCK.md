# CURRENT_VISION_LOCK.md

**Version:** 1.0 | **Last Updated:** 2025-11-22 | **Status:** 🔐 LOCKED

---

## 🎯 EXECUTIVE SUMMARY

This document freezes the **current architectural vision** for Vibe Studio v1.0 and defines the **corrected strategy** for the next phase (ARCH-044: Git Operations & Synchronization).

**Key Principle:** The system is **self-aware, signal-driven, and autonomously intelligent**. It doesn't need the operator to understand Git. It manages itself.

---

## 1. THE CORE IDENTITY

### Vibe Studio v1.0: An Intelligent Operating System

Vibe is not a simple CLI tool or script runner. It's an **autonomous software operating system** with:

- **Phoenix Config** (vibe_core/config/phoenix.py:218-324): Single source of truth for all system state
- **VibeKernel** (vibe_core/kernel.py:34-587): Central orchestration engine (Game Loop pattern)
- **Scheduler** (VibeScheduler): FIFO task queue with pluggable agents
- **Ledger** (VibeLedger): Persistent execution record (audit trail, observability)
- **Agent Registry**: Dynamic capability-based agent discovery
- **Inbox System** (GAD-006): Asynchronous intent channel for human-originated tasks

**Design Principle:** Single-threaded, explicit tick() calls, clear state machine, pluggable agents.

---

## 2. THE MECHANISMS

### 2.1 Phoenix: The Configuration System (vibe_core/config/phoenix.py:57-324)

**Purpose:** Unified, type-safe configuration management replacing scattered `os.getenv()` calls.

**Architecture:**
```
PhoenixConfig (Master)
├── SystemConfig (env, debug, log_level)
├── PathsConfig (home, project_root, data_dir, cache_dir, logs_dir)
├── QuotaConfig (RPM, TPM, concurrent_requests, cost_limits)
├── SafetyConfig (live_fire, quota_enforcement, cost_tracking, audit_logging)
└── ModelConfig (provider, model_name, api_key, max_tokens, temperature)
```

**Key Properties:**
- **Single Source of Truth:** One global `PhoenixConfig` instance (lazy singleton pattern)
- **Environment Override:** All fields respect env vars (prefix-based: `VIBE_SYSTEM_*`, `VIBE_PATH_*`, etc.)
- **Safe Defaults:** Conservative quotas, `live_fire_enabled=False` by default
- **Validation:** `validate_configuration()` checks sanity on load
- **Zero-Config Boot:** `.env` auto-loads on import

**Implementation Detail:**
```python
# vibe_core/config/phoenix.py:303-324
def get_config() -> PhoenixConfig:
    global _config
    if _config is None:
        _config = PhoenixConfig()
        is_valid, issues = _config.validate_configuration()
    return _config
```

**Usage Pattern:**
```python
from vibe_core.config import get_config
config = get_config()
live_fire = config.safety.live_fire_enabled
rpm_limit = config.quotas.requests_per_minute
```

---

### 2.2 VibeKernel: The Execution Engine (vibe_core/kernel.py:34-587)

**Purpose:** Central orchestrator that coordinates task execution, agent lifecycle, and system observability.

**Architecture:**
```
VibeKernel
├── VibeScheduler (FIFO task queue)
├── AgentRegistry (dict[agent_id, VibeAgent])
├── ManifestRegistry (STEWARD identity for each agent, ARCH-026)
├── VibeLedger (execution record, audit trail)
├── InboxMessages (asynchronous intent, GAD-006)
└── Status (STOPPED -> RUNNING -> STOPPED state machine)
```

**Core Lifecycle:**

1. **Initialization** (`__init__:59-77`)
   - Creates scheduler, registries, ledger
   - Status = STOPPED

2. **Boot** (`boot:120-164`)
   - Transitions to RUNNING
   - **Scans inbox** (`_scan_inbox:79-118`) - loads HIGH PRIORITY messages from `workspace/inbox/*.md`
   - Generates STEWARD manifests for all registered agents
   - Injects inbox messages as context for the operator

3. **Task Submission** (`submit:269-300`)
   - Validates agent using STEWARD manifest (ARCH-026 Phase 4)
   - Queues task to scheduler
   - Returns task_id for tracking

4. **Task Execution** (`tick:302-339` → `_execute_task:341-413`)
   - On each tick, retrieves next task from scheduler
   - Dispatches to registered agent
   - Records execution to ledger (start, completion, or failure)
   - Returns busy/idle status

5. **Shutdown** (`shutdown:166-181`)
   - Transitions to STOPPED
   - Pending tasks remain queued

**The Inbox Mechanism (GAD-006)** (`_scan_inbox:79-118`):
```python
def _scan_inbox(self) -> None:
    """Scan workspace/inbox/ for pending messages (HIGH PRIORITY context)"""
    inbox_path = Path("workspace/inbox")
    md_files = sorted(inbox_path.glob("*.md"))

    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        self.inbox_messages.append({
            "filename": md_file.name,
            "content": content,
        })
        logger.info(f"KERNEL: Loaded inbox message: {md_file.name}")

def boot(self) -> None:
    self._scan_inbox()
    if self.inbox_messages:
        logger.info(f"KERNEL: Inbox has {len(self.inbox_messages)} message(s) [HIGH PRIORITY]")
        for msg in self.inbox_messages:
            logger.info(f"KERNEL: >> INBOX: {msg['filename']}")
```

**The Manifest System (ARCH-026)** (`register_agent:183-216`, `_validate_delegation:218-265`):
- Each agent has a STEWARD manifest defining identity, class, capabilities, status
- Smart delegation: kernel validates agent exists, has active manifest, is registered
- Capability-based discovery: `find_agents_by_capability(capability: str)`

---

### 2.3 The Signal Flow: Boot → Inbox → Context

The kernel's boot sequence demonstrates the **signal-driven architecture**:

```
1. Kernel.boot()
   └─> _scan_inbox()
       └─> Reads workspace/inbox/*.md
           └─> Loads into self.inbox_messages
2. Agent loads (or operator boots)
   └─> Kernel.get_inbox_messages()
       └─> Returns list of {filename, content}
           └─> Inbox messages become HIGH PRIORITY context
3. Operator/Agent processes with full context
   └─> Decisions informed by inbox
       └─> Submit new tasks to kernel
```

**Key Principle:** The inbox is **not** a system notification channel. It's a **human intent channel**. System internals never write to the inbox. Only the operator/user does.

---

## 3. THE MISSING LINK: CORRECTED VISION FOR GIT-OPS (ARCH-044)

### Problem Statement

Local users pulling old code branches, bootstrapping stale systems, encountering database schema mismatches, missing dependencies. The repo has drifted 5+ commits ahead on `main`, but the local instance doesn't know this until runtime errors occur.

### Previous (Incorrect) Approach

**"System writes to Inbox"** → Pollute the human intent channel with technical noise.

Example: `workspace/inbox/SYSTEM_UPDATE_AVAILABLE.md` would train users to ignore the inbox.

### Corrected Approach: Context Injection + User Preferences

**The System NEVER writes to the inbox.**

Instead:

#### **Phase 1: Bootloader Detection (Bash)**
```bash
# bin/system-boot.sh
git fetch origin main
HEAD_COMMIT=$(git rev-parse HEAD)
MAIN_COMMIT=$(git rev-parse origin/main)

if [ "$HEAD_COMMIT" != "$MAIN_COMMIT" ]; then
    echo "SYSTEM_STATE.git_status=BEHIND" > /tmp/system_context.txt
    echo "SYSTEM_STATE.commits_behind=$(git rev-list --count HEAD..origin/main)" >> /tmp/system_context.txt
fi
```

#### **Phase 2: Context Injection (Boot Runtime)**
The kernel's boot sequence reads this context and **injects it into the prompt/manifest registry**.

```python
# In kernel.boot() or boot_sequence.py
def _scan_system_state(self) -> dict:
    """Load system context (Git status, DB schema, etc.) from /tmp/system_context.txt"""
    if Path("/tmp/system_context.txt").exists():
        # Parse and return as dict
        return {...}
    return {}
```

#### **Phase 3: User Preferences (STEWARD.md)**
The **STEWARD.md** file contains operator preferences for how to react:

```yaml
# STEWARD.md (user configuration)

[Git Operations]
auto_sync_enabled: true
sync_threshold_commits: 3  # Only ask if >3 commits behind
require_clean_working_tree: true
post_sync_action: "restart_system"  # or "manual_review"

[Safety]
allow_force_pull: false
backup_before_sync: true
```

#### **Phase 4: Autonomous Decision (Steward Agent)**
The Steward scans the injected system state AND preferences, then decides:

```python
# Pseudocode for future Steward logic
def check_system_health(self):
    state = kernel.get_system_state()  # {git_status, commits_behind, ...}
    prefs = load_preferences("STEWARD.md")

    if state["git_status"] == "BEHIND" and state["commits_behind"] >= prefs["sync_threshold"]:
        if prefs["auto_sync_enabled"]:
            self.log("System is {commits_behind} commits behind. Syncing per preferences...")
            self.perform_git_sync()
        else:
            self.log("System is behind. Manual sync required per preferences.")
```

### Why This Is The Right Design

1. **Channel Purity:** Inbox remains sacred for human intent only
2. **Signal-Driven:** System state flows through context, not messages
3. **Preference-Driven:** Operator behavior is configured, not reactive
4. **Autonomous:** Steward acts based on configuration, not interactive prompts
5. **Noob-Friendly:** User never needs to understand Git—system handles it
6. **Professional:** Mirrors SRE / Kubernetes operator patterns (desired state → actual state)

---

## 4. ARCHITECTURE TIMELINE

| Version | Component | Status | Vision |
|---------|-----------|--------|--------|
| v1.0 | Phoenix Config | ✅ LIVE | LOCKED |
| v1.0 | VibeKernel | ✅ LIVE | LOCKED |
| v1.0 | Inbox (GAD-006) | ✅ LIVE | LOCKED |
| v1.0 | STEWARD Manifests (ARCH-026) | ✅ LIVE | LOCKED |
| v1.1 | System Context Injection | 🎯 PLANNED | Phase 1-2 of ARCH-044 |
| v1.1 | Git-Ops Maintenance Specialist | 🎯 PLANNED | Phase 4 of ARCH-044 |
| v1.2 | Auto-Sync with Preferences | 🎯 PLANNED | Full ARCH-044 |

---

## 5. TESTING & VALIDATION CHECKPOINTS

To ensure this vision is achieved:

### Checkpoint 1: Inbox Purity ✅
- [ ] No system code writes to `workspace/inbox/`
- [ ] Only operator/user-initiated tasks write to inbox
- [ ] Kernel logs inbox load events at INFO level

### Checkpoint 2: Context Injection (ARCH-044 Phase 1-2)
- [ ] Bootloader detects Git state (branch, commits behind, working tree)
- [ ] System context stored in ephemeral storage or kernel state
- [ ] Kernel injects state into manifests/context on boot

### Checkpoint 3: Preferences (ARCH-044 Phase 3)
- [ ] `STEWARD.md` has `[Git Operations]` section
- [ ] Preferences include: `auto_sync_enabled`, `sync_threshold_commits`, `backup_before_sync`
- [ ] Steward loads and respects preferences

### Checkpoint 4: Autonomous Action (ARCH-044 Phase 4)
- [ ] Steward agent has `check_system_health()` method
- [ ] Detects Git drift and acts per preferences
- [ ] Logs decisions for audit trail

---

## 6. REFERENCE IMPLEMENTATION DETAILS

### Key Files (Current - v1.0)
- **vibe_core/config/phoenix.py:57-324** - Configuration master
- **vibe_core/kernel.py:34-587** - Execution engine
- **vibe_core/kernel.py:79-118** - Inbox scanning (GAD-006)
- **vibe_core/kernel.py:218-265** - Manifest validation (ARCH-026)

### Key Files (Future - v1.1+)
- **vibe_core/kernel.py** - Add `_scan_system_state()` method
- **vibe_core/runtime/boot_sequence.py** - Inject system state before agent boot
- **STEWARD.md** - Add `[Git Operations]` configuration section
- **vibe_core/agents/maintenance_specialist.py** - New agent for system health checks

---

## 7. PRINCIPLE: OPERATOR INVERSION (GAD-000)

This vision applies **Operator Inversion** throughout:

**Traditional:** Operator must understand system internals (Git, DB schemas, dependency management)

**Vibe Way:** System understands itself. Operator confirms preferences. System acts.

```
Operator's Mental Model:
┌─────────────────────────────────────┐
│ "System, are we up to date? Fix it. │
│ (I'll confirm via STEWARD.md)"      │
└──────────────────────────────────────

System's Model:
┌──────────────────────────────────────────────────────┐
│ 1. Check Git status (detect drift)                   │
│ 2. Load user preferences from STEWARD.md             │
│ 3. Make decision (sync? ask? warn?)                  │
│ 4. Execute autonomously or prompt for confirmation   │
│ 5. Record decision in ledger                         │
└──────────────────────────────────────────────────────
```

---

## 8. SIGN-OFF

**This vision is locked and will guide all subsequent development on ARCH-044.**

- **Architect Sign:** 🔐 LOCKED (2025-11-22)
- **Next Phase:** Implement Git-Ops Cartridge (ARCH-044 Phase 1-2)
- **Success Criteria:** System auto-detects and optionally auto-syncs Git state per user preferences, without operator needing to understand Git mechanics.

---

**END OF VISION LOCK**
