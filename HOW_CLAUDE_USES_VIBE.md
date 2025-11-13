# How Claude Uses Vibe Agency - The REAL Workflow

**Version:** 1.0
**Date:** 2025-11-13
**Critical Understanding:** This is NOT about automatic prompt generation!

---

## 🎯 What Vibe Agency REALLY Is

**IT IS:**
- ✅ A **guided workflow system** where Claude leads the user through structured phases
- ✅ A **knowledge-augmented conversation** with templates, rules, and validation
- ✅ An **interactive consultation process** with smart questions and scope negotiation
- ✅ A **variable-rich framework** that adapts based on user answers

**IT IS NOT:**
- ❌ An automatic prompt generator
- ❌ A fill-in-the-blanks template
- ❌ A batch processing system
- ❌ Something that works without Claude's intelligence

---

## 🧠 How The System Works

### **The Real Architecture:**

```
User: "I want to build a booking system"
  ↓
Claude loads: VIBE_ALIGNER personality + PROJECT_TEMPLATES + Validation Rules
  ↓
Claude (as VIBE_ALIGNER): "Let me calibrate expectations..."
  → Education Phase: Explains MVP vs v1.0
  → Asks: "Which scope matches your needs?"
User: "v1.0"
  ↓
Claude (with booking_system template): "I see this matches our booking template..."
  → Smart extraction: Uses inference rules to avoid unnecessary questions
  → Asks ONLY when genuinely ambiguous
  → Validates against FAE (Feasibility Analysis Engine)
User provides details...
  ↓
Claude: "Here are the extracted features. Let me validate..."
  → Checks FDG (Feature Dependency Graph)
  → Detects missing dependencies
  → Flags scope issues using APCE (Complexity Engine)
  → Negotiates scope if needed
  ↓
Claude outputs: feature_spec.json
  → User reviews
  → Iterates if needed
  ↓
NEXT PHASE: GENESIS_BLUEPRINT (architecture generation)
```

**This is an INTERACTIVE, GUIDED PROCESS with Claude as the conductor!**

---

## 📋 The 6-Phase VIBE_ALIGNER Workflow

### **Phase 1: Education & Calibration**

**What Claude Does:**
```
Load: task_01_education_calibration.md

Present options to user:
  📦 PROTOTYPE (days)
  🚀 MVP (4-8 weeks)
  ✅ v1.0 (8-16 weeks)

Educate based on choice:
  "A v1.0 means..."
  "Here are the tradeoffs..."

Store: user_scope_choice
```

**Variables Set:**
- `user_scope_choice` (prototype/mvp/v1.0)
- `core_problem_statement`
- `target_users`

---

### **Phase 2: Feature Extraction**

**What Claude Does:**
```
Load: task_02_feature_extraction.md + PROJECT_TEMPLATES.yaml

Match to template:
  User: "booking system"
  → Template: booking_system
  → Typical features: calendar_view, booking_creation, payments, etc.

Smart questioning:
  ✅ Infer: "booking" → Need database (don't ask!)
  ✅ Infer: "v1.0" → Production-ready (don't ask!)
  ❓ Ask ONLY: "Payment required upfront or optional?"

For EACH feature extract:
  - Input format + example
  - Processing logic + dependencies
  - Output format + success criteria
```

**Variables Collected:**
- Feature list with full specs
- Input/output formats
- External dependencies
- Side effects

---

### **Phase 3: Feasibility Validation**

**What Claude Does:**
```
Load: task_03_feasibility_validation.md + FAE_constraints.yaml

For EACH feature, check:
  ✅ Is it technically feasible for v1.0?
  ✅ Are there blocking constraints?

Example checks:
  ❌ Real-time video → Too complex for v1.0
  ❌ Custom ML model → Requires data + training
  ✅ Stripe payments → Well-supported, feasible

If infeasible:
  → Flag to user
  → Suggest alternatives
  → Get confirmation before proceeding
```

**Validation Against:**
- 717 FAE constraints
- Technical feasibility rules
- v1.0 scope guidelines

---

### **Phase 4: Gap Detection**

**What Claude Does:**
```
Load: task_04_gap_detection.md + FDG_dependencies.yaml

Check dependencies:
  Feature: "Send email confirmations"
  → Missing: Email service (SendGrid? Mailgun?)

  Feature: "Payment processing"
  → Missing: Payment gateway (Stripe? PayPal?)

Ask user:
  "I see you need email. Which service?"
  "I see you need payments. Which gateway?"

Check logical dependencies:
  Feature: "Cancel booking"
  → Requires: "View bookings" (add if missing)
```

**Uses:**
- 2,546 Feature Dependency rules
- Logical dependency chains
- Service integration requirements

---

### **Phase 5: Scope Negotiation**

**What Claude Does:**
```
Load: task_05_scope_negotiation.md + APCE_rules.yaml

Calculate complexity:
  Feature 1: 20 points
  Feature 2: 15 points
  ...
  Total: 85 points

Compare to timeline:
  User wants: 6 weeks
  Estimated need: 9 weeks
  → YELLOW flag (tight but doable)

Negotiate:
  "Your scope is ambitious for 6 weeks."
  "Options:"
  "  A) Extend to 9 weeks"
  "  B) Drop Feature X (save 15 points)"
  "  C) Simplify Feature Y"

Get user decision.
```

**Uses:**
- 1,303 APCE complexity rules
- Timeline estimation
- Scope vs resources tradeoffs

---

### **Phase 6: Output Generation**

**What Claude Does:**
```
Load: task_06_output_generation.md + ORCHESTRATION_data_contracts.yaml

Generate feature_spec.json:
  {
    "project_id": "...",
    "features": [...],
    "dependencies": [...],
    "estimated_complexity": 85,
    "timeline_estimate": "9 weeks",
    "scope_status": "YELLOW"
  }

Validate against schema.

Present to user:
  "Here's your validated specification."
  "Ready to proceed to architecture design?"

If approved → Pass to GENESIS_BLUEPRINT
If not → Iterate (back to Phase 2 or 4)
```

**Outputs:**
- `feature_spec.json` (validated)
- Ready for next agent (GENESIS_BLUEPRINT)

---

## 🔄 The Multi-Agent Workflow

### **Complete SDLC Flow:**

```
VIBE_ALIGNER (Planning)
  → Phases 1-6
  → Output: feature_spec.json
  ↓
GENESIS_BLUEPRINT (Architecture)
  → Select core modules
  → Design extensions
  → Generate config schema
  → Output: architecture.json
  ↓
CODE_GENERATOR (Development)
  → Analyze spec
  → Generate code
  → Generate tests
  → Output: source code + tests
  ↓
QA_VALIDATOR (Testing)
  → Run tests
  → Static analysis
  → Output: qa_report.json
  ↓
DEPLOY_MANAGER (Deployment)
  → Pre-deployment checks
  → Execute deployment
  → Post-deployment validation
  → Output: deploy_receipt.json
  ↓
BUG_TRIAGE (Maintenance)
  → Bug analysis
  → Remediation planning
  → Output: hotfix_plan.json
```

**Each agent has:**
- Core personality (who am I?)
- Multiple tasks (what do I do?)
- Knowledge bases (what do I know?)
- Validation gates (what must be checked?)

---

## 💡 How Claude ACTUALLY Uses This

### **The WRONG Way (What I Was Doing):**

```python
# Generate prompt automatically
vibe-cli.py generate VIBE_ALIGNER 02_feature_extraction

# Paste giant prompt
# Execute once
# Done
```

**Problems:**
- ❌ No interactivity
- ❌ No variable collection
- ❌ No scope negotiation
- ❌ Not using the framework's intelligence

---

### **The RIGHT Way (What I SHOULD Do):**

```python
# 1. Load the agent personality + knowledge
from vibe_helper import compose_prompt
vibe_aligner_context = compose_prompt("VIBE_ALIGNER", "01_education_calibration")

# 2. INTERNALIZE the personality
# I (Claude) become VIBE_ALIGNER
# I have access to:
#   - 18 project templates
#   - Smart questioning rules
#   - Inference rules
#   - Validation constraints

# 3. START THE CONVERSATION
"Welcome! I'm here to help you plan your software project.
Before we dive into features, let's align on scope.
Are we building: PROTOTYPE / MVP / v1.0?"

# 4. USER RESPONDS
User: "v1.0"

# 5. PROCEED THROUGH PHASES
# Phase 1: Education ✓
# Phase 2: Feature extraction (interactive!)
"Tell me about your project idea..."
User: "Booking system for yoga studio"

# I (Claude) check PROJECT_TEMPLATES:
# → Found: booking_system template
# → Typical features: calendar, booking, payments, emails

"I see this matches a booking system. Typical features include:
- Calendar view
- Create/cancel bookings
- Email notifications
- Optional: Payment processing

Does this match your vision?"

# 6. SMART QUESTIONS (not blind questions!)
# Check inference rules:
#   ✅ "booking" → Need database (inferred, don't ask)
#   ✅ "v1.0" → Production-ready (inferred, don't ask)
#   ❓ Payment processing → MUST ASK (business decision)

"For payments - required upfront or optional?"

# 7. VALIDATION
# Load FAE_constraints.yaml
# Check each feature against 717 rules

"I've validated your features. All are feasible for v1.0 ✓"

# 8. GAP DETECTION
# Load FDG_dependencies.yaml
# Check 2,546 dependency rules

"I notice you'll need:
- Email service (SendGrid/Mailgun)
- Database (PostgreSQL recommended)
- Optional: Payment gateway (Stripe recommended)

Which email service do you prefer?"

# 9. SCOPE NEGOTIATION
# Load APCE_rules.yaml
# Calculate complexity

"Total complexity: 85 points
Your timeline: 6 weeks
Estimated need: 9 weeks

This is tight but doable (YELLOW). Options:
A) Extend to 9 weeks (safer)
B) Simplify payment integration (save 2 weeks)

What would you prefer?"

# 10. OUTPUT
"Here's your validated specification:
- 5 core features
- All technically feasible
- Timeline: 8 weeks (negotiated)
- Ready for architecture design

Shall we proceed to architecture generation?"
```

**This is how the system SHOULD be used!**

---

## 🎯 Why vibe-cli.py Was Wrong

The CLI generates ONE STATIC PROMPT:

```bash
python3 vibe-cli.py generate VIBE_ALIGNER 02_feature_extraction
# → 48,000 character prompt
# → Static
# → No variables collected
# → No interactivity
```

But the system needs **INTERACTIVE EXECUTION**:

```
Phase 1 → Collect variables → Phase 2 → Validate → Phase 3 → Negotiate → Phase 4...
```

---

## 🛠️ What v1.0 Actually Needs

### **For Claude to USE the system:**

1. **Load Agent Context**
   ```python
   from vibe_helper import compose_prompt
   context = compose_prompt("VIBE_ALIGNER", "01_education_calibration")
   # Claude internalizes the personality + knowledge
   ```

2. **Execute Interactively**
   - Claude reads the task instructions
   - Claude has access to all templates/rules in context
   - Claude converses with user
   - Claude collects variables
   - Claude validates and negotiates
   - Claude outputs structured JSON

3. **Progress Through Workflow**
   ```python
   # Phase 1
   context1 = compose_prompt("VIBE_ALIGNER", "01_education_calibration")
   # ... interactive session ...

   # Phase 2
   context2 = compose_prompt("VIBE_ALIGNER", "02_feature_extraction")
   # ... interactive session ...

   # etc.
   ```

### **For Human Users to UNDERSTAND the system:**

1. **Workflow Documentation**
   - "Here's how Claude will guide you through planning"
   - "Expect these questions"
   - "Here's what each phase does"

2. **Examples**
   - Real session transcripts
   - "User asks for booking system → Here's how Claude responds"

3. **Knowledge Base Transparency**
   - "Claude has access to 18 project templates"
   - "Claude will validate against 717 feasibility rules"
   - "Claude knows 2,546 dependency relationships"

---

## 📊 What's MISSING for v1.0

### **Critical Gap: Meta-Documentation**

The system HAS:
- ✅ All the agents
- ✅ All the knowledge
- ✅ All the validation rules
- ✅ All the workflows

The system LACKS:
- ❌ Documentation of HOW CLAUDE USES IT
- ❌ User guide: "What to expect from the process"
- ❌ Session examples: "Here's a real planning session"
- ❌ Quick start: "Your first project in 15 minutes"

### **What Needs to be Created:**

1. **`CLAUDE_SESSION_GUIDE.md`**
   - How Claude loads and uses agent contexts
   - How to progress through phases
   - How to handle iterations

2. **`USER_EXPERIENCE_GUIDE.md`**
   - What happens in a planning session
   - Example questions Claude will ask
   - What outputs to expect

3. **`SESSION_EXAMPLES.md`**
   - Real transcript: "Planning a booking system"
   - Real transcript: "Planning a SaaS app"
   - Real transcript: "Planning a CLI tool"

4. **`QUICK_START_SESSION.md`**
   - "Your first project: Step-by-step"
   - Start with simplest template (todo app?)
   - Show complete workflow

---

## ✅ v1.0 Release Checklist

### **DONE:**
- ✅ All agents implemented (7 agents, 31 tasks)
- ✅ All knowledge bases (18 templates, 8 stacks, 6,400 lines)
- ✅ All validation gates (23 gates)
- ✅ All tests passing (23/23)
- ✅ Error handling + NFRs
- ✅ `vibe_helper.py` (for Claude to load contexts)

### **TODO for v1.0:**
- [ ] `CLAUDE_SESSION_GUIDE.md` (how Claude uses the system)
- [ ] `USER_EXPERIENCE_GUIDE.md` (what users should expect)
- [ ] `SESSION_EXAMPLES.md` (real transcript examples)
- [ ] `QUICK_START_SESSION.md` (first project walkthrough)
- [ ] Update README.md (point to new guides)

**Estimated time: 2-3 hours**

---

## 🚀 After v1.0

### **Potential Enhancements:**

1. **Session State Management**
   - Save/resume sessions
   - Track which phase user is in
   - Store collected variables

2. **Interactive CLI Mode**
   ```bash
   python3 vibe-session.py start --project yoga_booking
   # Claude interactively guides through phases
   # State is saved between sessions
   ```

3. **Web UI (Optional)**
   - Streamlit interface
   - Visual workflow progress
   - Save/export sessions

But for v1.0: **Documentation is enough!**

---

**Document Version:** 1.0
**Status:** ✅ Correct Understanding
**Next:** Create the 4 missing guides

---

## 🎓 Key Takeaways

1. **Vibe Agency is NOT a prompt generator**
   - It's a guided consultation framework

2. **Claude is the intelligent conductor**
   - Not a passive prompt executor
   - Active participant with knowledge and judgment

3. **The system is ALREADY complete**
   - Just needs meta-documentation
   - No code changes needed!

4. **v1.0 is about CLARITY**
   - Make it crystal clear how to use
   - Show real examples
   - Document expectations

**Ready to create the missing guides!** 🎯
