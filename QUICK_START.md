# Quick Start Guide - Vibe Agency System

> Get from "I have an idea" to validated specs in 30 minutes.

---

## 🎯 Goal

Plan a complete software project using Claude AI + Vibe Agency prompts.

---

## 📋 Prerequisites

1. **Claude AI access** (claude.ai or Anthropic API)
2. **This repository** cloned locally
3. **Basic understanding** of software projects

---

## 🚀 Step-by-Step Guide

### Step 1: Set Up Workspace (5 minutes)

```bash
# Navigate to repository
cd vibe-agency

# Create workspace for your project
# Format: workspaces/{client_name}/{project_name}/
mkdir -p workspaces/my_client/yoga_booking/artifacts/{planning,code,test,deployment}

# Copy manifest template
cp project_manifest.json workspaces/my_client/yoga_booking/

# Optional: Initialize git for this project
cd workspaces/my_client/yoga_booking
git init
```

**Result:** You now have a structured workspace for your project.

---

### Step 2: Compose Planning Prompt (2 minutes)

Open Claude (claude.ai) and load the following files:

**Base Prompt:**
```
Load file: agency_os/01_planning_framework/agents/VIBE_ALIGNER/_prompt_core.md
```

**Knowledge Bases:**
```
Load file: agency_os/01_planning_framework/knowledge/PROJECT_TEMPLATES.yaml
Load file: agency_os/01_planning_framework/knowledge/TECH_STACK_PATTERNS.yaml
Load file: agency_os/01_planning_framework/knowledge/FAE_constraints.yaml
```

**Validation Gates:**
```
Load file: agency_os/01_planning_framework/agents/VIBE_ALIGNER/gates/gate_sufficient_input_detail.md
Load file: agency_os/01_planning_framework/agents/VIBE_ALIGNER/gates/gate_realistic_timeline.md
Load file: agency_os/01_planning_framework/agents/VIBE_ALIGNER/gates/gate_budget_feasibility.md
Load file: agency_os/01_planning_framework/agents/VIBE_ALIGNER/gates/gate_tech_stack_coherence.md
Load file: agency_os/01_planning_framework/agents/VIBE_ALIGNER/gates/gate_security_baseline.md
```

**Tip:** Use Claude Projects feature to save this prompt composition for reuse!

---

### Step 3: Provide Project Idea (1 minute)

Now that Claude is "equipped" with Vibe Agency prompts, provide your project idea:

**Example Input:**
```
I want to build a booking website for my yoga studio.

Customers should be able to:
- See available classes in a calendar
- Book a class slot
- Pay online
- Get email confirmation

Budget: €25,000
Timeline: 6 weeks
Team: Just me (I know JavaScript/React basics)
```

**What Happens:**
Claude will now process this through VIBE_ALIGNER:
1. **Input Validation:** Checks if input is clear enough (gate_sufficient_input_detail)
2. **Template Matching:** Matches to `booking_system` template
3. **Feature Extraction:** Lists concrete features with complexity scores
4. **Tech Stack Recommendation:** Suggests Next.js + Prisma + PostgreSQL + Stripe + Vercel
5. **Budget Check:** €25k vs estimated €29k → YELLOW (tight but workable)
6. **Timeline Check:** 6 weeks vs estimated 9 weeks → YELLOW (aggressive but possible)
7. **Security Check:** Validates HTTPS, password hashing, payment security
8. **Output:** Generates `feature_spec.json`

---

### Step 4: Review & Iterate (10 minutes)

Claude will present:

**🟢 What's Good:**
- Clear project type detected
- Tech stack recommendation appropriate
- Features validated as feasible

**⚠️ Warnings:**
- Budget tight (85% of estimate) - recommend locking scope
- Timeline aggressive (66% of estimate) - recommend 8 weeks instead
- Missing: booking cancellation feature (should add)

**Ask Follow-ups:**
```
USER: "What if I skip the payment integration for v1.0 and add it later?"

VIBE_ALIGNER: "Good call! Removing payment reduces:
- Complexity: 90 → 65 points
- Timeline: 9 weeks → 6.5 weeks ✅ FITS your timeline!
- Budget: €29k → €20k ✅ UNDER your budget!
- Recommendation: Build v1.0 without payment, add in v1.1 after launch"
```

---

### Step 5: Save Artifacts (2 minutes)

Once satisfied, save the output:

```bash
# Claude will generate feature_spec.json
# Copy it to your workspace
cat > workspaces/my_client/yoga_booking/artifacts/planning/feature_spec.json << 'EOF'
{
  "project_name": "Yoga Studio Booking",
  "version": "1.0",
  "features": [
    {
      "id": "F001",
      "name": "Calendar View",
      "priority": "HIGH",
      "complexity": 20,
      "description": "Display available class times in calendar format"
    },
    ...
  ],
  "tech_stack": {
    "frontend": "Next.js 14 (App Router)",
    "backend": "Next.js API Routes",
    "database": "PostgreSQL (Supabase)",
    "hosting": "Vercel"
  },
  "budget": {
    "total": "€29,250",
    "breakdown": {
      "development": "€24,000",
      "infrastructure": "€360",
      "services": "€15",
      "buffer": "€4,875"
    }
  },
  "timeline": {
    "estimated_weeks": 9,
    "user_timeline": 6,
    "status": "YELLOW",
    "recommendation": "Extend to 8 weeks or reduce scope"
  }
}
EOF
```

---

### Step 6: Next Steps (Optional)

Now you have a validated spec! Next actions:

#### A. Generate Architecture (GENESIS_BLUEPRINT)

```
Load file: agency_os/01_planning_framework/agents/GENESIS_BLUEPRINT/_prompt_core.md

Input: feature_spec.json from Step 5

Output: architecture.json (detailed tech architecture)
```

#### B. Create Proposal Document

Use the outputs to create a client proposal:
- Feature list (from feature_spec.json)
- Tech stack recommendation (with rationale)
- Budget breakdown (with buffer explanation)
- Timeline with milestones
- Risks & assumptions

#### C. Start Development

Use the architecture as a blueprint for development.

---

## 📊 Complete Example Walkthrough

### Input (Vague)
```
USER: "I need a fitness app."
```

### VIBE_ALIGNER Response
```
GATE FAILED: Input Too Vague

Your input: "I need a fitness app."

What's missing:
- ❌ What KIND of fitness app? (workout tracking, nutrition, social, etc.)
- ❌ What will users DO with it? (log workouts, track progress, etc.)
- ❌ Mobile or web?

To proceed, please provide:
1. What problem does this solve? (e.g., "users can't track their workouts easily")
2. What's the MAIN thing users will do?
3. Mobile app (iOS/Android) or web application?
```

### Input (Sufficient)
```
USER: "Fitness tracking app for logging workouts.

Users can:
- Log exercises (name, sets, reps, weight)
- See workout history
- View weekly progress chart

Mobile app (iOS + Android, React Native)
Budget: €15,000
Timeline: 8 weeks
Team: Me (solo, know JavaScript)
```

### VIBE_ALIGNER Response
```
✅ Input Sufficient - Processing...

📋 PROJECT ANALYSIS

Template Match: rest_api_backend + mobile_app_basic
Project Type: Mobile App with Backend API

📦 FEATURES EXTRACTED (with complexity):
1. User Authentication (15) - HIGH
2. Exercise CRUD (20) - HIGH
3. Workout History (10) - MEDIUM
4. Progress Chart (15) - MEDIUM
Total Complexity: 60 points

🛠️ TECH STACK RECOMMENDED

Mobile: React Native + Expo
Backend: FastAPI + PostgreSQL
Hosting: Railway (backend) + Expo EAS (mobile)
Auth: Firebase Auth (simplest for mobile)

Why this stack:
- You know JavaScript ✅
- React Native = iOS + Android from one codebase
- Expo = simplifies mobile development
- FastAPI = fast, simple backend
- Budget-friendly hosting

💰 BUDGET CHECK

Estimated: €17,500
Your budget: €15,000

Status: 🔴 RED (Budget Insufficient by €2,500)

Options:
1. Increase budget to €18,000 (recommended)
2. Remove progress chart (saves €3k) → €14,500 ✅
3. Start with web version (simpler) → €12,000 ✅

⏱️ TIMELINE CHECK

Estimated: 9 weeks (base: 7 weeks + 30% buffer for solo + learning Expo)
Your timeline: 8 weeks

Status: ⚠️ YELLOW (Tight but doable)

Recommendations:
- Lock scope (no feature additions mid-project)
- Use Expo (saves time vs bare React Native)
- Skip animations for v1.0 (add later)

🔒 SECURITY CHECK

✅ Authentication (Firebase handles it)
✅ HTTPS (Railway enforces)
✅ Input validation (FastAPI + Pydantic auto-validates)
⚠️ Add rate limiting to API (prevent abuse)

Result: PASS with warning

📤 OUTPUT: feature_spec.json
→ Save to: workspaces/my_client/fitness_tracker/artifacts/planning/

Next: Load GENESIS_BLUEPRINT to generate detailed architecture
```

---

## 🎓 Tips & Tricks

### 1. Be Specific in Input
**Bad:** "I want a website"
**Good:** "Booking website for yoga studio with calendar, payment, email confirmations. Budget €25k, 6 weeks."

### 2. Iterate Freely
Ask "what if" questions:
- "What if I remove feature X?"
- "What if I extend timeline to 10 weeks?"
- "What if I switch from mobile to web?"

### 3. Use Templates as Starting Points
Browse `PROJECT_TEMPLATES.yaml` to see:
- 18 templates (booking, SaaS, API, mobile, etc.)
- Typical features + complexity
- Common pitfalls

### 4. Validate Budget Early
Don't skip budget/timeline - it catches unrealistic expectations EARLY.

### 5. Save Everything
Save ALL artifacts:
- feature_spec.json
- architecture.json
- budget_breakdown.json
- timeline_estimate.json

These become your **project documentation**.

---

## ⚡ Fast Track (10-Minute Version)

**For experienced users:**

1. Load prompts (2 min)
2. Paste project idea (30 sec)
3. Review + save feature_spec.json (7 min)
4. Done! Use spec for development or proposal.

---

## 🆘 Troubleshooting

### "Claude says input is too vague"
→ Add: project type, core user action, rough budget/timeline

Example: "Booking system for X. Users can Y. Budget Z, timeline W."

### "Budget/timeline checks fail"
→ Good! It's catching unrealistic expectations. Adjust scope or extend timeline.

### "Tech stack recommendation doesn't fit my team"
→ Tell Claude: "My team only knows Python" → Will switch from Next.js to Django

### "Too many features extracted"
→ Tell Claude: "Let's focus on MVP - which 3 features are must-have for v1.0?"

---

## ✅ Success Criteria

After this guide, you should have:

- ✅ Structured workspace (`workspaces/{client}/{project}/`)
- ✅ Validated feature list (feature_spec.json)
- ✅ Tech stack recommendation (with rationale)
- ✅ Budget estimate (with breakdown)
- ✅ Timeline estimate (with risk buffer)
- ✅ Security baseline validated
- ✅ Ready to build OR present to client

---

## 🚀 What's Next?

**For Developers:**
- Use architecture.json as blueprint
- Start with highest priority features
- Follow recommended tech stack

**For Consultants:**
- Use outputs to create client proposal
- Present budget/timeline with confidence
- Manage scope with feature priority list

**For Product Managers:**
- Use feature_spec.json as product backlog
- Prioritize features (HIGH/MEDIUM/LOW)
- Plan sprints based on complexity scores

---

**Ready to plan your project?** Start with Step 1! 🎯
