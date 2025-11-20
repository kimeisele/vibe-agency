# 🤖 VIBE AGENCY OS - Self-Constructing Software Factory

> **Status:** 🟢 **OPERATIONAL** | **Version:** 2.5
>
> A self-managing AI agency system that builds itself. The system is now live with agents, runtime, knowledge retrieval, mission control, and quality assurance fully integrated.

## 🎉 v2.5 Architecture - NOW OPERATIONAL

**Date:** 2025-11-20 | **Status:** ✅ **VERIFIED IN PRODUCTION**

The v2.5 architecture upgrade is complete and operational:

- **✅ HAP (Hierarchical Agent Pattern)** - Specialist-based execution model
- **✅ SQLite Shadow Mode** - Persistent decision logging and audit trails
- **✅ Registry Pattern** - Dynamic agent selection and routing
- **✅ Tool Safety Guard** - Strict file operation security layer
- **✅ 5 Specialized Agents** - Planning, Coding, Testing, Deployment, Maintenance

**Verification:** Maiden voyage test successfully validated all components. See [`MAIDEN_VOYAGE_REPORT.md`](MAIDEN_VOYAGE_REPORT.md) for details.

**What This Means:** The system now scales with dedicated specialists for each SDLC phase, persistent state management, and production-grade security controls.

---

## 🏛️ Architecture: The Anatomy of VIBE

VIBE Agency is built like a living organism with specialized subsystems:

```
                    ┌─────────────────────────┐
                    │   BRAIN (GAD-7)         │
                    │  Mission Control        │
                    │  Task Management        │
                    │  Orchestration          │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
   ┌─────────┐            ┌──────────┐            ┌──────────┐
   │BODY     │            │ARMS      │            │LEGS      │
   │(GAD-5)  │            │(GAD-6)   │            │(GAD-3)   │
   │Runtime  │            │Knowledge │            │Agents    │
   │Kernel   │            │Retrieval │            │Personas  │
   └────┬────┘            └────┬─────┘            └────┬─────┘
        │                      │                      │
        ▼                      ▼                      ▼
   ┌─────────────────────────────────────────────────────┐
   │           FEET (GAD-4) - Quality Assurance          │
   │        Code Linting + Testing + Verification       │
   └─────────────────────────────────────────────────────┘
```

### What Each Subsystem Does

**🧠 Brain (GAD-7): Mission Control**
- Self-managing task framework
- Tracks all work via roadmap.yaml
- Validates completion with automated checks
- Coordinates between agents

**🦴 Body (GAD-5): Runtime Environment**
- `bin/vibe-shell` — Secure command execution with context injection
- Enforces MOTD (Message of the Day) at startup
- Logs all command execution with timestamps
- Manages environment variables and context

**💪 Arms (GAD-6): Knowledge System**
- `bin/vibe-knowledge` — Semantic search and retrieval
- File-based knowledge artifact storage
- Research framework integration
- Pattern library for agents

**🚀 Legs (GAD-3): Active Agents**
- **BaseAgent** — Integration hub connecting all systems
- **CoderAgent** — Development specialist (patterns domain)
- **ResearcherAgent** — Investigation specialist (research domain)
- **ReviewerAgent** — Quality specialist (patterns/decisions)
- **ArchitectAgent** — System design specialist (decisions domain)

**🦶 Feet (GAD-4): Quality Assurance**
- `bin/vibe-check` — Code linting and formatting
- `bin/vibe-test` — Test execution and reporting
- `verify_work()` — Integrated QA validation in BaseAgent

---

## 🛠️ Available Tools (Toolbelt)

### System Management

#### `bin/system-boot.sh`
Initialize the entire system with pre-flight checks and context setup.
```bash
./bin/system-boot.sh
# Outputs:
# ✅ Pre-flight checks passed
# 🟢 System health: OPERATIONAL
# 📋 Session context loaded
```

#### `bin/mission`
Task management and mission control interface.
```bash
./bin/mission status          # Show current task status
./bin/mission start <task>    # Start a task
./bin/mission validate <task> # Validate task completion
./bin/mission complete <task> # Mark task as complete
```

### Runtime & Execution

#### `bin/vibe-shell`
Secure shell wrapper with context injection, MOTD enforcement, and execution logging.
```bash
bin/vibe-shell "python script.py"
# - Enforces MOTD on startup
# - Injects VIBE_CONTEXT environment variable
# - Logs execution to .vibe/logs/commands.log
# - Returns exit code and captures output
```

### Knowledge & Research

#### `bin/vibe-knowledge`
Semantic search and artifact retrieval.
```bash
bin/vibe-knowledge search "authentication patterns"
# Lists matching artifacts with relevance scores

bin/vibe-knowledge read "workspaces/vibe_research_framework/research/auth-patterns.md"
# Outputs full artifact content
```

### Quality Assurance

#### `bin/vibe-check`
Code quality checks using Ruff.
```bash
bin/vibe-check              # Run all checks
bin/vibe-check --fix        # Auto-fix issues
# Output: ✅ PASS or ❌ FAIL with details
```

#### `bin/vibe-test`
Test execution with domain filtering.
```bash
bin/vibe-test               # Run all tests
bin/vibe-test --fast        # Skip slow tests
bin/vibe-test --domain agents  # Only agent tests
bin/vibe-test --coverage    # With coverage report
```

### System Information

#### `bin/vibe-sysinfo`
Beautiful system information display (first client application).
```bash
bin/vibe-sysinfo            # Formatted table with CPU, Memory, Disk, Uptime
bin/vibe-sysinfo --json     # JSON output for programmatic access
bin/vibe-sysinfo --help     # Show help
bin/vibe-sysinfo --version  # Show version
```

#### `bin/vibe-dashboard`
Unified health and mission status dashboard integrating all GAD layers.
```bash
bin/vibe-dashboard          # Show full dashboard (Mission Control, Health, Git, PRs)
bin/vibe-dashboard --json   # JSON output for programmatic access
bin/vibe-dashboard --help   # Show help
```

---

## ⚙️ Configuration

### Environment Variables (GAD-510.1: Dynamic Quotas)

VIBE Agency loads quota limits from environment variables for flexible cost and rate control:

```bash
# Budget Control (Safe defaults prevent surprise costs)
export VIBE_QUOTA_RPM=10                    # Requests per minute (default: 10)
export VIBE_QUOTA_TPM=10000                 # Tokens per minute (default: 10000)
export VIBE_QUOTA_HOURLY_USD=2.0            # Cost per hour limit (default: $2.0)
export VIBE_QUOTA_DAILY_USD=5.0             # Cost per day limit (default: $5.0)
```

**Common Scenarios:**

```bash
# Conservative budget for testing
export VIBE_QUOTA_DAILY_USD=1.0
export VIBE_QUOTA_HOURLY_USD=0.50

# Production with more headroom
export VIBE_QUOTA_DAILY_USD=100.0
export VIBE_QUOTA_HOURLY_USD=20.0

# Rate limiting (useful for free tier APIs)
export VIBE_QUOTA_RPM=3
export VIBE_QUOTA_TPM=5000
```

**How It Works:**
- System loads these variables on startup
- Falls back to safe defaults if undefined
- Circuit breaker protects against cascading failures
- Pre-flight quota checks prevent wasted API calls

---

## 🚀 How to Use

### Quick Start (One Command)

```bash
# Initialize the system
./bin/system-boot.sh

# The system will:
# 1. Run pre-flight checks
# 2. Display health status
# 3. Load session context
# 4. Show available routes
```

### Working with Tasks

```bash
# Check what's in the roadmap
./bin/mission status

# Start a task
./bin/mission start GAD-401_QA_SUITE

# Run validation checks for a task
./bin/mission validate GAD-401_QA_SUITE

# Mark task as complete
./bin/mission complete GAD-401_QA_SUITE
```

### Running Code

```bash
# Execute a Python script with context injection
./bin/vibe-shell "python scripts/genesis.py"

# Run a bash command
./bin/vibe-shell "ls -la"

# Run with environment variables
./bin/vibe-shell "echo $VIBE_CONTEXT"
```

### Quality Assurance

```bash
# Check code quality
./bin/vibe-check

# Run tests
./bin/vibe-test

# Run specific domain tests (faster)
./bin/vibe-test --domain agents

# With coverage
./bin/vibe-test --coverage
```

### Working with Agents

```python
from agency_os.03_agents.base_agent import BaseAgent
from agency_os.03_agents.personas import CoderAgent, ArchitectAgent

# Initialize an agent
coder = CoderAgent(name="junior-dev", vibe_root="/path/to/vibe-agency")

# Execute a command via runtime
result = coder.execute_command("python script.py")
print(result.output)

# Consult the knowledge base
knowledge = coder.consult_knowledge("authentication patterns")
print(knowledge.artifacts)

# Verify work before committing
verification = coder.verify_work(check_code=True, run_tests=True)
print(verification["success"])

# Report status
status = coder.report_status()
print(f"Agent {status['agent_name']} executed {status['execution_count']} commands")
```

### Knowledge Search

```bash
# Search for patterns
bin/vibe-knowledge search "REST API patterns"

# Search in specific domain
bin/vibe-knowledge search "authentication" --domain patterns

# Read full artifact
bin/vibe-knowledge read "workspaces/vibe_research_framework/patterns/rest-api.md"
```

### System Info

```bash
# Display system info in beautiful table format
bin/vibe-sysinfo

# Get JSON for scripting
bin/vibe-sysinfo --json > system_info.json

# Integration with other tools
SYSTEM_MEMORY=$(bin/vibe-sysinfo --json | jq '.memory.total_gb')
echo "System has $SYSTEM_MEMORY GB RAM"
```

---

## 📊 Current Status

### Version: 2.0 - OPERATIONAL

| Component | Status | Details |
|-----------|--------|---------|
| **Brain (GAD-7)** | ✅ DONE | Mission Control system self-managing |
| **Body (GAD-5)** | ✅ DONE | Runtime kernel with context injection & logging |
| **Arms (GAD-6)** | ✅ DONE | Knowledge system with semantic search |
| **Legs (GAD-3)** | ✅ DONE | 5 agent personas with integration hub |
| **Feet (GAD-4)** | ✅ DONE | QA suite (linting + testing) |
| **Orchestration (GAD-2)** | ✅ DONE | Secure atomic Git delivery with draft PR safety gate |
| **First Contact** | ✅ DONE | vibe-sysinfo & vibe-dashboard system monitoring |

### Test Coverage

- **Total Tests:** 519/532 passing (13 skipped) ✅
- **Coverage:** 52%

### Available Commands

```
bin/system-boot.sh    ✅ System initialization
bin/mission           ✅ Task management
bin/vibe-shell        ✅ Runtime execution
bin/vibe-knowledge    ✅ Knowledge retrieval
bin/vibe-check        ✅ Code quality
bin/vibe-test         ✅ Test execution
bin/vibe-sysinfo      ✅ System information
```

---

## 🏗️ What's Been Built

### GAD-5: Runtime Foundation
- **bin/vibe-shell** — Secure execution kernel with MOTD and context injection
- **Context Injection** — Loads .vibe/runtime/context.json into every execution
- **Audit Logging** — All commands logged to .vibe/logs/commands.log
- **Status:** DONE ✅

### GAD-6: Knowledge Foundation
- **Directory Structure** — workspaces/vibe_research_framework organized
- **Knowledge Config** — agency_os/02_knowledge/config/knowledge_graph.yaml
- **bin/vibe-knowledge** — CLI tool for searching and reading artifacts
- **Status:** DONE ✅

### GAD-3: Agent Framework
- **BaseAgent** — Integration hub (execute_command, consult_knowledge, verify_work)
- **4 Specialized Personas** — CoderAgent, ResearcherAgent, ReviewerAgent, ArchitectAgent
- **Execution Results** — ExecutionResult and KnowledgeResult dataclasses
- **Status:** DONE ✅

### GAD-4: Quality Assurance
- **bin/vibe-check** — Ruff-based code quality and formatting
- **bin/vibe-test** — Pytest wrapper with domain filtering
- **verify_work()** — Integrated QA method in BaseAgent
- **Status:** DONE ✅

### OPERATION_FIRST_CONTACT: First Client App
- **bin/vibe-sysinfo** — Beautiful system information tool
- **psutil Integration** — CPU, Memory, Disk, Uptime collection
- **rich Output** — Formatted tables and JSON export
- **8 Unit Tests** — Comprehensive validation
- **Status:** DONE ✅

### GAD-8: Health Dashboard
- **bin/vibe-dashboard** — Unified health and mission status dashboard
- **GAD Integration** — Displays data from all GAD layers (Mission Control, Health, Git, PRs)
- **JSON Export** — Provides machine-readable output for system integration
- **Status:** DONE ✅

---

## 📂 Repository Structure

```
vibe-agency/
├── agency_os/                          # Core infrastructure
│   ├── 00_system/task_management/      # Mission Control (GAD-7)
│   ├── 01_interface/cli/cmd_mission.py # CLI interface
│   ├── 02_knowledge/                   # Knowledge System (GAD-6)
│   │   ├── retriever.py
│   │   └── config/knowledge_graph.yaml
│   ├── 03_agents/                      # Agent Framework (GAD-3)
│   │   ├── base_agent.py               # Integration hub
│   │   └── personas/                   # Specialized agents
│   │       ├── coder.py
│   │       ├── researcher.py
│   │       ├── reviewer.py
│   │       └── architect.py
│
├── bin/                                # Toolbelt
│   ├── system-boot.sh                  # System initialization
│   ├── mission                         # Task management
│   ├── vibe-shell                      # Runtime kernel (GAD-5)
│   ├── vibe-knowledge                  # Knowledge retrieval (GAD-6)
│   ├── vibe-check                      # Code linting (GAD-4)
│   ├── vibe-test                       # Test runner (GAD-4)
│   └── vibe-sysinfo                    # System info (First app)
│
├── .vibe/                              # System state
│   ├── config/roadmap.yaml             # Task definitions
│   ├── runtime/context.json            # Execution context
│   └── logs/commands.log               # Audit trail
│
├── workspaces/                         # Knowledge artifacts
│   └── vibe_research_framework/        # Research & patterns
│
├── tests/                              # Test suite
│   ├── test_base_agent.py              # Agent tests
│   ├── test_personas.py                # Persona tests
│   └── test_sysinfo.py                 # System info tests
│
└── README.md                           # This file
```

---

## 🔄 Development Workflow

### 1. Check System Health
```bash
./bin/system-boot.sh
```

### 2. Run Quality Assurance
```bash
./bin/vibe-check    # Code quality
./bin/vibe-test     # Tests
```

### 3. Execute Work
```bash
./bin/vibe-shell "command here"
```

### 4. Track Progress
```bash
./bin/mission status
./bin/mission validate TASK_ID
```

### 5. Before Committing
```bash
./bin/pre-push-check.sh
git add .
git commit -m "feat: description"
git push
```

---

## 🎯 Next Steps

1. **Use the system** — Try the tools on real tasks
2. **Build client apps** — Extend vibe-sysinfo pattern
3. **Expand agents** — Add specialized personas for your domain
4. **Automate workflows** — Chain agents together with mission control

---

## 📚 Documentation

- **CLAUDE.md** — Operational status and quick reference
- **ARCHITECTURE_V2.md** — System design and principles
- **SSOT.md** — Implementation decisions
- **.vibe/config/roadmap.yaml** — All tasks and validation checks

---

## ✨ Key Features

- **Self-Managing** — Tasks defined in YAML, validated automatically
- **Integrated** — All subsystems connected via BaseAgent
- **Audited** — Every command logged to audit trail
- **Testable** — 35 core tests prove system works
- **Extensible** — Add new agents, tools, and domains easily
- **Zero External Dependencies** — File-based, no databases or APIs

---

## 🚀 Status Summary

**VIBE Agency is now OPERATIONAL.** The self-constructing software factory has successfully:

✅ Built its runtime kernel (GAD-5)
✅ Built its knowledge system (GAD-6)
✅ Built its agent framework (GAD-3)
✅ Built its quality assurance suite (GAD-4)
✅ Built its mission control (GAD-7)
✅ Built its first client application (vibe-sysinfo)
✅ Proven all systems work with tests

The system is ready for production use. Deploy, extend, and automate.

---

## 📞 Support

For issues, check:
- **System not booting?** → Run `./bin/system-boot.sh` for diagnostics
- **Tests failing?** → Run `./bin/vibe-test --coverage` to see what's broken
- **Code quality issues?** → Run `./bin/vibe-check --fix` to auto-correct

---

**Last Updated:** 2025-11-19
**Version:** 2.0 (OPERATIONAL)
**Status:** 🟢 LIVE
