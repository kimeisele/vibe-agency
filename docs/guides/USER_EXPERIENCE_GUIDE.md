# User Experience Guide - What to Expect

**Version:** 1.0
**Audience:** End Users (Consultants, Agencies, Solo Developers)
**Purpose:** Understand how Vibe Agency sessions work

---

## 🎯 What is Vibe Agency?

Vibe Agency is an **AI-powered planning assistant** that helps you transform vague project ideas into concrete, validated software specifications.

**Think of it as:**
- ✅ A senior product manager + software architect in your corner
- ✅ A structured consultation process (not just chatting)
- ✅ A knowledge-augmented conversation (18 templates, 6,000+ rules)
- ✅ A scope negotiation tool (keeps you realistic)

**NOT:**
- ❌ A code generator (we plan, not code - yet!)
- ❌ An automatic tool (you work WITH Claude, not submit a form)
- ❌ A generic chatbot (we have specific domain knowledge)

---

## 🚀 How a Planning Session Works

### The Complete Flow

```
You: "I want to build X"
  ↓
Phase 1: Education (5-10 min)
  Claude: "Let's define scope - MVP or v1.0?"
  Claude: "Here's what each means..."
  You: Choose scope
  ↓
Phase 2: Feature Extraction (15-30 min)
  Claude: "Tell me about your project..."
  Claude: Asks smart questions (only when needed)
  You: Provide details
  ↓
Phase 3: Validation (5 min)
  Claude: "Checking feasibility..."
  Claude: Flags any impossible features
  ↓
Phase 4: Gap Detection (10 min)
  Claude: "Missing dependencies detected..."
  Claude: "You need email service - which one?"
  You: Make choices
  ↓
Phase 5: Scope Negotiation (10-20 min)
  Claude: "Complexity: 85 points, 9 weeks needed"
  Claude: "Your timeline: 6 weeks - here are options..."
  You: Negotiate scope vs timeline
  ↓
Phase 6: Output (5 min)
  Claude: "Here's your validated spec..."
  Claude: Generates feature_spec.json
  You: Review and approve
  ↓
Next: Architecture Design (if you want)
  Claude: Switches to GENESIS_BLUEPRINT
  ...continues workflow...
```

**Total Time:** 50-90 minutes for complete planning phase

---

## 📋 The 6 Phases Explained

### Phase 1: Education & Calibration

**What Happens:**
Claude doesn't immediately ask "What do you want to build?" - that leads to scope creep.

Instead, Claude first calibrates your expectations by explaining three options:
- 📦 **PROTOTYPE** - Visual mockup (days to 2 weeks)
- 🚀 **MVP** - Minimal product to test ONE hypothesis (4-8 weeks)
- ✅ **v1.0** - Complete, production-ready solution to ONE problem (8-16 weeks)

**Why This Matters:**
Most project failures come from misaligned expectations. By starting with education, we ensure you understand the tradeoffs between features, time, and complexity.

**Your Role:**
- Choose your scope goal
- Think about core problem (not all features)
- Be honest about timeline/budget constraints

**Example Exchange:**
```
Claude: "Welcome! Before we dive in, let's align on scope.
         Are we building a PROTOTYPE, MVP, or v1.0?"

You: "v1.0 - I want something production-ready"

Claude: "Excellent. v1.0 means complete, stable, lovable, and focused.
         It's NOT 'all features imaginable' - that's v5.0.
         My job is to keep you focused on solving ONE problem perfectly.

         What problem are you solving? Who is it for?"
```

---

### Phase 2: Feature Extraction

**What Happens:**
Claude extracts concrete features from your description using:
- **18 project templates** (booking systems, SaaS apps, marketplaces, etc.)
- **Smart questioning rules** (only ask what can't be inferred)
- **Inference rules** (don't ask obvious things)

**Why This Matters:**
Generic AI asks 100 questions. Vibe Agency asks ~5-10 targeted questions because it has domain knowledge.

**Your Role:**
- Describe your project idea
- Answer Claude's questions
- Clarify ambiguous requirements

**Example Exchange:**
```
You: "I want a booking system for my yoga studio"

Claude: "Got it! This matches our 'booking_system' template.
         Typical features:
         - Calendar view (available time slots)
         - Booking creation/cancellation
         - Email confirmations
         - Payment processing

         Does this match your vision?"

You: "Yes, exactly!"

Claude: "Great. A few quick clarifications:
         - Payment required upfront or optional?
         - Email service preference? [SendGrid/Mailgun/SES]
         - Cancellation deadline? (e.g., '24h before class')"
```

**What Claude WON'T Ask:**
- ❌ "Should it be configurable?" (Always yes for production)
- ❌ "Should it handle errors?" (Always yes)
- ❌ "Do you need a database?" (Inferred from "booking system")
- ❌ "Should users log in?" (Inferred from "bookings")

**What Claude WILL Ask:**
- ✅ "Payment upfront or optional?" (Business logic decision)
- ✅ "Which email service?" (Multiple valid options)
- ✅ "Support class packages or single classes only?" (Scope decision)

---

### Phase 3: Feasibility Validation

**What Happens:**
Claude validates every feature against **717 feasibility rules** (FAE - Feasibility Analysis Engine).

**Why This Matters:**
Catches impossible features early before you invest time/money.

**Your Role:**
- Review any warnings
- Accept suggestions for alternatives
- Confirm scope changes if needed

**Example Exchange:**
```
Claude: "Checking feasibility for all features...

         ✅ Calendar view - FEASIBLE
         ✅ Booking creation - FEASIBLE
         ✅ Payment processing (Stripe) - FEASIBLE
         ⚠️  Custom ML recommendation engine - TOO COMPLEX

         For v1.0, I recommend: Simple featured classes instead.
         Add ML recommendations in v2.0.

         Agree?"

You: "Makes sense. Let's do simple for v1.0"
```

**Common Warnings:**
- Real-time video/chat → Too complex, suggest async alternatives
- Custom ML models → Need data + training, suggest rule-based for v1.0
- Blockchain integration → High complexity, suggest traditional DB

---

### Phase 4: Gap Detection

**What Happens:**
Claude checks for missing dependencies using **2,546 dependency rules** (FDG - Feature Dependency Graph).

**Why This Matters:**
You might say "I want bookings" but forget you need user authentication, email service, payment gateway, etc.

**Your Role:**
- Review detected gaps
- Choose between options (e.g., Stripe vs PayPal)
- Approve adding required features

**Example Exchange:**
```
Claude: "I've detected some missing dependencies:

         Your Feature: 'Send booking confirmations'
         ❌ Missing: Email service

         Your Feature: 'Process payments'
         ❌ Missing: Payment gateway

         Your Feature: 'User bookings'
         ❌ Missing: User authentication system

         Recommendations:
         - Email: SendGrid (easy setup, reliable)
         - Payments: Stripe (best for small business)
         - Auth: NextAuth (built-in with Next.js)

         Should I add these to the spec?"

You: "Yes, add all three"

Claude: "Done! Updated feature list:
         + User Registration & Login
         + Password Reset
         + Email Integration (SendGrid)
         + Payment Integration (Stripe)

         This adds ~3 weeks to timeline. Recalculating..."
```

---

### Phase 5: Scope Negotiation

**What Happens:**
Claude calculates total complexity using **1,303 complexity rules** (APCE - Architectural Planning & Complexity Engine) and compares to your timeline/budget.

**Why This Matters:**
Most projects fail because scope > reality. This phase aligns them.

**Your Role:**
- Review complexity estimate
- Choose: Extend timeline, simplify features, or accept risk
- Make informed tradeoff decisions

**Example Exchange:**
```
Claude: "Scope Analysis Complete:

         **Total Complexity:** 118 points
         **Estimated Timeline:** 9 weeks (1 developer)
         **Your Target:** 6 weeks

         ⚠️ **STATUS: YELLOW** (Tight but possible)

         Options:
         A) Extend to 9 weeks (Recommended - safer)
         B) Simplify payments - add in v1.1 (saves 3 weeks)
         C) Aggressive sprint - HIGH RISK of bugs

         My recommendation: Option A
         Quality launch beats rushed launch.

         What do you prefer?"

You: "Let's do 9 weeks. I want it done right"

Claude: "Smart choice! Updated timeline: 9 weeks
         Status now: ✅ GREEN (Realistic scope)"
```

**Complexity Scoring:**
- Simple CRUD: 5-10 points/feature
- API integration: 15-20 points
- Payment processing: 25 points
- Real-time features: 30-40 points
- Auth system: 25 points

**Rule of Thumb:** 1 developer = 15 points/week

---

### Phase 6: Output Generation

**What Happens:**
Claude generates a validated, machine-readable specification (feature_spec.json) following a strict schema.

**Why This Matters:**
This isn't just a document - it's the input for the next phase (architecture design) or can be handed to your development team.

**Your Role:**
- Review the final spec
- Request changes if needed
- Approve to proceed or save for later

**Example Output:**
```json
{
  "project_id": "yoga_booking_system",
  "scope": "v1.0",
  "timeline_weeks": 9,
  "status": "GREEN",
  "features": [
    {
      "id": "user_authentication",
      "name": "User Registration & Login",
      "complexity": 25,
      "priority": "HIGH",
      "dependencies": ["database", "email_service"]
    },
    {
      "id": "booking_calendar",
      "name": "Calendar View",
      "complexity": 20,
      "priority": "HIGH",
      "input": "User selects date",
      "output": "Available time slots displayed"
    }
    ...
  ],
  "tech_stack": {
    "frontend": "Next.js",
    "backend": "Next.js API Routes",
    "database": "PostgreSQL",
    "email": "SendGrid",
    "payments": "Stripe"
  },
  "estimated_cost": {
    "development": "€27,000 (9 weeks @ €3k/week)",
    "infrastructure": "€150/month",
    "services": "€100/month (SendGrid + Stripe)"
  }
}
```

---

## 🔄 Continuing to Architecture Design

### If You Want to Continue

After Phase 6, Claude can switch to **GENESIS_BLUEPRINT** to design the technical architecture:

```
Claude: "Your specification is complete!

         Would you like me to proceed to architecture design?
         This will:
         - Select core modules
         - Design feature extensions
         - Generate config schema
         - Create directory structure

         Continue? [Yes / Save and exit]"

You: "Yes, let's design the architecture"

Claude: *switches to GENESIS_BLUEPRINT*
        "Great! Loading architecture design context...

         I've analyzed your 8 features. Based on the 'booking_system'
         pattern, I recommend:

         Core Modules (stdlib only):
         - booking_engine (core business logic)
         - calendar_manager (slot management)
         - config_loader (YAML config)

         Extensions (external deps):
         - auth_extension (NextAuth)
         - payment_extension (Stripe)
         - email_extension (SendGrid)

         Let me walk you through the architecture..."
```

---

## ⏱️ Time Estimates

### Planning Phase (VIBE_ALIGNER)
- **Minimum:** 50 minutes (simple project, clear requirements)
- **Typical:** 75 minutes (medium complexity, some negotiation)
- **Maximum:** 120 minutes (complex project, lots of scope negotiation)

### Architecture Phase (GENESIS_BLUEPRINT)
- **Minimum:** 30 minutes (simple architecture)
- **Typical:** 60 minutes (medium complexity)
- **Maximum:** 90 minutes (complex architecture with many integrations)

### Total for Complete Planning + Architecture
- **Fast:** 80 minutes
- **Typical:** 135 minutes (~2.5 hours)
- **Thorough:** 210 minutes (~3.5 hours)

---

## 💡 Tips for Best Results

### Before You Start

**✅ DO:**
- Have a clear problem statement ("Yoga studio needs bookings")
- Know your timeline/budget constraints
- Understand your target users
- Be open to scope negotiation

**❌ DON'T:**
- List 50 features upfront (let Claude guide extraction)
- Say "I want everything" (focus is key)
- Demand unrealistic timelines
- Skip the education phase

---

### During the Session

**✅ DO:**
- Answer Claude's questions honestly
- Clarify when requirements are unclear
- Accept expert guidance on feasibility
- Negotiate scope pragmatically

**❌ DON'T:**
- Rush through phases
- Insist on impossible features
- Ignore warnings about complexity
- Add features without considering impact

---

### After Planning

**✅ DO:**
- Save the feature_spec.json
- Share with your development team
- Use it as contract/scope document
- Refer back when scope creep happens

**❌ DON'T:**
- Change scope without recalculating
- Add features without consultation
- Ignore the validated tech stack
- Skip dependencies that were flagged

---

## 🎯 What You Get

### Immediate Outputs

1. **feature_spec.json** - Machine-readable specification
2. **Validated feature list** - All technically feasible
3. **Tech stack recommendation** - Battle-tested choices
4. **Timeline estimate** - Realistic, not optimistic
5. **Cost breakdown** - Development + infrastructure + services
6. **Dependency map** - Nothing forgotten
7. **Risk assessment** - Known issues flagged

### Long-Term Value

1. **Scope Control** - Reference document when client/stakeholder adds features
2. **Team Alignment** - Everyone works from same spec
3. **Vendor Communication** - Hand to developers with confidence
4. **Budget Planning** - Realistic cost expectations
5. **Timeline Management** - Milestones based on complexity

---

## 🆘 Common Questions

### "Can I iterate after the session?"

Yes! You can:
- Start a new session with changes ("I want to add feature X")
- Use GENESIS_UPDATE agent for architecture changes
- Re-run VIBE_ALIGNER with modified requirements

### "What if I don't know technical details?"

That's fine! Claude will:
- Suggest defaults based on best practices
- Explain options in business terms
- Make recommendations with rationale
- Only ask business logic questions

### "Can I save and continue later?"

Yes! The feature_spec.json preserves all state:
- Tell Claude "Save and exit"
- Resume later: "Continue from feature_spec.json"

### "What if Claude's estimate seems high?"

Claude uses real-world data:
- 1,303 complexity rules
- Historical project data
- Conservative (safer) estimates

If it seems high:
- Ask for breakdown
- Negotiate scope (Phase 5)
- Get second opinion from your team
- But don't just cut the estimate arbitrarily!

### "Can I use this for non-web projects?"

Yes! Templates include:
- CLI tools
- Mobile apps (React Native, Flutter)
- REST APIs
- Real-time systems (WebSocket)
- Chrome extensions
- Desktop apps (Electron)
- And more...

If your project type isn't in the templates, Claude will still guide you through - just without the template shortcuts.

---

## 🚀 Ready to Start?

### Quick Start

1. Open Claude Code (or Claude.ai)
2. Say: "I want to plan a software project using Vibe Agency"
3. Claude will load VIBE_ALIGNER and start Phase 1
4. Follow the guided process
5. Get your validated spec!

### Or Read Examples First

See `SESSION_EXAMPLES.md` for:
- Real planning session transcript (booking system)
- SaaS app planning example
- CLI tool planning example

See `QUICK_START_SESSION.md` for:
- Your first project walkthrough
- Step-by-step tutorial
- Complete example (todo app)

---

**Version:** 1.0
**Status:** Complete
**Questions?** See README.md or file a GitHub Issue
