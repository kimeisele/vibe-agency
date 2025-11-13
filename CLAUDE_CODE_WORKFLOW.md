# Vibe Agency - Claude Code Workflow Guide

**Version:** 1.0
**Date:** 2025-11-13
**For:** Using Vibe Agency with Claude Code (this instance!)

---

## 🎯 Overview

Vibe Agency is a **prompt composition system** designed to work WITH Claude Code (or any Claude instance). It:

- ✅ **Generates specialized prompts** for different tasks
- ✅ **Loads relevant knowledge bases** automatically
- ✅ **Includes validation gates** to ensure quality
- ✅ **Guides you through multi-step workflows**

**You DON'T need:**
- ❌ External APIs
- ❌ Complex automation
- ❌ Multiple LLM instances

**You DO use:**
- ✅ Claude Code (this instance)
- ✅ The `vibe-cli.py` tool to generate prompts
- ✅ Copy/paste the prompts into Claude Code

---

## 🚀 Quick Start

### 1. List Available Agents

```bash
python3 vibe-cli.py list
```

**Output:**
```
VIBE_ALIGNER      → Feature extraction & feasibility validation
GENESIS_BLUEPRINT → Architecture generation
CODE_GENERATOR    → Code generation from specs
QA_VALIDATOR      → Quality assurance & testing
DEPLOY_MANAGER    → Deployment orchestration
BUG_TRIAGE        → Bug analysis & remediation
```

### 2. List Tasks for an Agent

```bash
python3 vibe-cli.py tasks VIBE_ALIGNER
```

**Output:**
```
01_education_calibration    → Phase 1
02_feature_extraction       → Phase 2
03_feasibility_validation   → Phase 3
04_gap_detection            → Phase 4
05_scope_negotiation        → Phase 5
06_output_generation        → Phase 6
```

### 3. Generate a Prompt

```bash
python3 vibe-cli.py generate VIBE_ALIGNER 02_feature_extraction
```

**Output:**
```
✅ SUCCESS
Prompt saved to: COMPOSED_PROMPT.md
Prompt size: 48,344 characters
```

### 4. Use the Prompt in Claude Code

```bash
# Option A: Ask Claude to read it
"Hey Claude, please read COMPOSED_PROMPT.md and execute the task"

# Option B: Copy/paste the content
cat COMPOSED_PROMPT.md
# Then paste into Claude Code
```

---

## 📋 Complete Workflow Example

### Scenario: Planning a New Project

**Step 1: Feature Extraction**

```bash
# Generate the prompt
python3 vibe-cli.py generate VIBE_ALIGNER 02_feature_extraction

# Ask Claude Code
"Read COMPOSED_PROMPT.md and extract features from this project description:
I want a booking system for my yoga studio..."
```

**What happens:**
- Claude reads the composed prompt (with personality + knowledge + gates)
- Claude extracts features from your description
- Claude validates against feasibility rules
- Claude outputs `feature_spec.json`

**Step 2: Architecture Generation**

```bash
# Generate next prompt
python3 vibe-cli.py generate GENESIS_BLUEPRINT 01_select_core_modules

# Ask Claude Code
"Read COMPOSED_PROMPT.md and generate architecture from
workspaces/yoga_studio/artifacts/planning/feature_spec.json"
```

**What happens:**
- Claude reads the architecture generation prompt
- Claude selects core modules based on features
- Claude validates against architecture rules
- Claude outputs `architecture.json`

**Step 3: Code Generation**

```bash
# Generate code gen prompt
python3 vibe-cli.py generate CODE_GENERATOR 02_code_generation

# Ask Claude Code
"Read COMPOSED_PROMPT.md and generate code from architecture.json"
```

**What happens:**
- Claude reads the code generation prompt
- Claude generates code following patterns
- Claude validates against quality gates
- Claude outputs source code + tests

---

## 🔄 Multi-Step Workflows

### Planning Workflow (VIBE_ALIGNER → GENESIS_BLUEPRINT)

```bash
# Step 1: Feature Extraction
python3 vibe-cli.py generate VIBE_ALIGNER 02_feature_extraction
# → Talk to Claude → feature_spec.json

# Step 2: Feasibility Check
python3 vibe-cli.py generate VIBE_ALIGNER 03_feasibility_validation
# → Talk to Claude → validated_features.json

# Step 3: Architecture Selection
python3 vibe-cli.py generate GENESIS_BLUEPRINT 01_select_core_modules
# → Talk to Claude → core_modules.json

# Step 4: Extension Design
python3 vibe-cli.py generate GENESIS_BLUEPRINT 02_design_extensions
# → Talk to Claude → architecture.json
```

### Development Workflow (CODE_GENERATOR → QA_VALIDATOR)

```bash
# Step 1: Generate Code
python3 vibe-cli.py generate CODE_GENERATOR 02_code_generation
# → Talk to Claude → source code

# Step 2: Generate Tests
python3 vibe-cli.py generate CODE_GENERATOR 03_test_generation
# → Talk to Claude → test files

# Step 3: Run QA
python3 vibe-cli.py generate QA_VALIDATOR 02_automated_test_execution
# → Talk to Claude → test_report.json
```

---

## 💡 Best Practices

### 1. **Use Sequential Tasks**

Don't skip steps! Each task builds on previous outputs:

```
✅ GOOD:
  01_feature_extraction → 02_feasibility_validation → 03_gap_detection

❌ BAD:
  Skip 02_feasibility_validation → Missing validation rules
```

### 2. **Save Outputs to Workspace**

Claude should save outputs to the correct location:

```
workspaces/{client_name}/{project_name}/artifacts/
├── planning/
│   ├── feature_spec.json
│   └── architecture.json
├── code/
│   └── src/
├── test/
│   └── test_report.json
└── deployment/
    └── deploy_receipt.json
```

### 3. **Check Validation Gates**

Each prompt includes validation gates. Claude will check them automatically:

```
✓ Validation gates loaded: gate_concrete_specifications.md

Claude will validate:
- Are features concrete enough?
- Are dependencies available?
- Is the timeline realistic?
```

### 4. **Iterate When Needed**

If validation fails, regenerate with fixes:

```bash
# First attempt failed
python3 vibe-cli.py generate VIBE_ALIGNER 02_feature_extraction
# → Claude: "Feature X too vague"

# Fix input and retry
# → Give more specific requirements
```

---

## 🧩 Understanding the Composition

### What's in a Composed Prompt?

```markdown
# === CORE PERSONALITY ===
- Agent identity (e.g., "You are VIBE_ALIGNER")
- Responsibilities
- Success criteria

# === KNOWLEDGE BASE ===
- PROJECT_TEMPLATES.yaml (18 templates)
- TECH_STACK_PATTERNS.yaml (8 stacks)
- FAE_constraints.yaml (feasibility rules)
- FDG_dependencies.yaml (feature dependencies)

# === TASK INSTRUCTIONS ===
- Step-by-step what to do
- Expected inputs
- Expected outputs

# === VALIDATION GATES ===
- gate_concrete_specifications.md
- gate_realistic_timeline.md
- gate_budget_feasibility.md

# === RUNTIME CONTEXT ===
- project_id: "yoga_studio"
- workspace: "workspaces/yoga_studio"
- phase: "PLANNING"
```

**Total: 16,000 - 48,000 characters depending on task**

### Why So Large?

The prompts are large because they include:
- Complete agent personality (ensures consistency)
- Relevant knowledge bases (18 project templates, 8 tech stacks, etc.)
- Validation rules (prevent common mistakes)
- Task-specific instructions

This ensures Claude has ALL the context needed to execute the task correctly.

---

## 🎛️ Advanced Usage

### Custom Context

```bash
# Generate with custom output location
python3 vibe-cli.py generate VIBE_ALIGNER 02_feature_extraction -o custom-prompt.md

# Then tell Claude:
"Read custom-prompt.md and use this context:
- project_id: my_saas_app
- workspace: workspaces/acme_corp/my_saas_app
- budget: €50k
- timeline: 12 weeks"
```

### Workspace Setup

```bash
# Create workspace for new project
mkdir -p workspaces/{client}/{project}/artifacts/{planning,code,test,deployment}

# Copy manifest
cp project_manifest.json workspaces/{client}/{project}/

# Generate first prompt
python3 vibe-cli.py generate VIBE_ALIGNER 01_education_calibration
```

### Batch Generation

```bash
# Generate all planning prompts at once
for task in 02_feature_extraction 03_feasibility_validation 04_gap_detection; do
    python3 vibe-cli.py generate VIBE_ALIGNER $task -o "prompts/VIBE_ALIGNER_${task}.md"
done

# Then work through them with Claude sequentially
```

---

## 🐛 Troubleshooting

### "Agent not found"

```bash
# Check available agents
python3 vibe-cli.py list

# Make sure you use exact agent ID (case-sensitive)
python3 vibe-cli.py generate VIBE_ALIGNER ...  # ✅ Correct
python3 vibe-cli.py generate vibe_aligner ...  # ❌ Wrong case
```

### "Task not found"

```bash
# List tasks for agent
python3 vibe-cli.py tasks VIBE_ALIGNER

# Use exact task ID (with numbers)
python3 vibe-cli.py generate VIBE_ALIGNER 02_feature_extraction  # ✅ Correct
python3 vibe-cli.py generate VIBE_ALIGNER feature_extraction     # ❌ Missing number
```

### "Prompt too large"

Some prompts are 40k+ characters. This is normal! Claude can handle up to 200k characters.

If you get context window errors:
1. Use a smaller task (e.g., `05_handoff` instead of `02_feature_extraction`)
2. Or: Ask Claude to read the file instead of pasting

### "Missing knowledge files"

```bash
# Validate knowledge index
python3 validate_knowledge_index.py

# This checks all knowledge files are present and valid
```

---

## 📊 What's Different from Manual Prompting?

### Manual Prompting (Old Way)

```
User: "Hey Claude, extract features from this project"
Claude: "Sure! What kind of project?"
User: "A booking system"
Claude: "Ok, here are generic features..."
```

**Problems:**
- ❌ Claude doesn't know your templates
- ❌ No validation rules
- ❌ Inconsistent output format
- ❌ No quality gates

### Vibe Agency (New Way)

```bash
python3 vibe-cli.py generate VIBE_ALIGNER 02_feature_extraction
# → Loads 18 project templates, tech stacks, validation rules

User: "Read COMPOSED_PROMPT.md - I need a booking system"
Claude: "I see this matches the 'booking_system' template.
         Extracting features... validating against FAE rules...
         Output: feature_spec.json ✅"
```

**Benefits:**
- ✅ Claude has ALL domain knowledge
- ✅ Follows proven patterns
- ✅ Validates automatically
- ✅ Consistent, structured outputs

---

## 🎓 Learning Path

### Beginner: Single Tasks

```bash
# Start simple - just generate one prompt
python3 vibe-cli.py generate VIBE_ALIGNER 02_feature_extraction

# Use it with Claude
"Read COMPOSED_PROMPT.md and help me with my project idea"
```

### Intermediate: Multi-Step Workflows

```bash
# Plan a complete project
# Step 1-6 of VIBE_ALIGNER
# Then Step 1-5 of GENESIS_BLUEPRINT
# Each step builds on previous
```

### Advanced: Custom Agents

```bash
# Understand the composition system
# Read: agency_os/00_system/runtime/prompt_runtime.py
# Create your own agents with:
#   - _prompt_core.md (personality)
#   - _composition.yaml (assembly rules)
#   - tasks/ (task prompts)
#   - gates/ (validation rules)
```

---

## 🔗 Key Files

```
vibe-agency/
├── vibe-cli.py                              # CLI tool (start here!)
├── agency_os/00_system/runtime/prompt_runtime.py  # Composition engine
├── agency_os/01_planning_framework/         # Planning agents
│   ├── agents/VIBE_ALIGNER/                # Feature extraction
│   └── agents/GENESIS_BLUEPRINT/           # Architecture
├── agency_os/02_code_gen_framework/         # Code generation
├── agency_os/03_qa_framework/               # QA & testing
├── agency_os/04_deploy_framework/           # Deployment
├── agency_os/05_maintenance_framework/      # Bug triage
└── workspaces/                             # Your projects go here
```

---

## ✅ Checklist: Is Vibe Agency Working?

**Test 1: CLI Works**
```bash
python3 vibe-cli.py list
# Should show 7 agents
```

**Test 2: Prompt Generation Works**
```bash
python3 vibe-cli.py generate VIBE_ALIGNER 02_feature_extraction
# Should create COMPOSED_PROMPT.md
```

**Test 3: All Agents Work**
```bash
python3 tests/test_prompt_composition.py
# Should show: Passed: 23/23
```

**Test 4: Claude Can Use It**
```bash
# Generate prompt
python3 vibe-cli.py generate VIBE_ALIGNER 02_feature_extraction

# Ask Claude:
"Read COMPOSED_PROMPT.md and execute the task with this input:
I want to build a simple todo app"

# Claude should:
# ✅ Extract features
# ✅ Validate feasibility
# ✅ Output feature_spec.json
```

---

## 🚀 Ready for v1.0?

**What works NOW:**
- ✅ Prompt composition system (23/23 tests passing)
- ✅ All 7 agents with all tasks
- ✅ Knowledge bases (18 templates, 8 stacks)
- ✅ Validation gates
- ✅ CLI tool
- ✅ Works with Claude Code (this instance!)

**What's NOT needed:**
- ❌ External LLM APIs
- ❌ Complex automation
- ❌ Multi-agent orchestration
- ❌ Database or backend

**You can release v1.0 NOW as a "Prompt Composition System"**

Users work with:
1. The CLI tool (`vibe-cli.py`)
2. Claude Code (or Claude.ai, or any Claude instance)
3. Manual copy/paste workflow

This is intentionally simple and works with the existing Claude Code workflow.

---

## 📞 Support

- **Documentation:** See README.md
- **Tests:** Run `python3 tests/test_prompt_composition.py`
- **Issues:** File at GitHub Issues
- **Examples:** See `PHASE_2_TEST_RESULTS.md` for real scenarios

---

**Remember:** Vibe Agency is a TOOL for Claude Code, not a replacement. You (the user) + Claude + Vibe Agency = Powerful Planning System! 🚀
