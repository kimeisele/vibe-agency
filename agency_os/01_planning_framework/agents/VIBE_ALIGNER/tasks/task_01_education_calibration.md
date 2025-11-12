# Task: Education & Calibration

## Objective
Set correct user expectations about project scope (PROTOTYPE vs MVP vs v1.0) BEFORE feature extraction begins.

---

## Goal
Calibrate the user's mental model to ensure they understand what v1.0 means and the necessary tradeoffs.

---

## Input Artifacts
None (first task in workflow)

---

## Critical Rule
**NEVER start with "What do you want to build?"**

Always start with education to calibrate the user's mental model.

---

## Process

### Step 1: Opening Dialog

Present the user with three options:

```
Welcome! I'm here to help you plan your software project professionally.

Before we dive into features, let's align on our goal. Are we building:

📦 **A PROTOTYPE?**
   Goal: A quick visual mockup to test a design or user flow
   Timeline: Days to 1-2 weeks
   Scope: Non-functional, design validation only

🚀 **An MVP (Minimum Viable Product)?**
   Goal: A product with minimal features to validate a core hypothesis and learn
   Timeline: 4-8 weeks
   Scope: Bare minimum to test ONE core assumption

✅ **A v1.0 (Version 1.0)?**
   Goal: A complete, stable, lovable core product for early customers
   Timeline: 8-16 weeks
   Scope: Full solution to ONE core problem, production-ready

Please choose the goal that matches your needs: [PROTOTYPE / MVP / v1.0]
```

---

### Step 2: Educate Based on User's Choice

#### If User Chooses v1.0:

```
Excellent choice. A v1.0 means we're building a complete solution to your core problem.

Here's what v1.0 means:
✅ It's COMPLETE for its core use case (not half-baked)
✅ It's STABLE (production-ready, not buggy)
✅ It's LOVABLE (early customers will pay for it)
✅ It's FOCUSED (solves ONE problem perfectly, not ten problems poorly)

Here's what v1.0 is NOT:
❌ "All the features I can imagine" (that's v5.0)
❌ "Everything competitors have" (that's feature parity, not v1.0)
❌ "Perfect and polished" (that's v2.0+ refinement)

To build a successful v1.0, we must make tradeoffs between:
- Features (what to build)
- Time (how fast to launch)
- Complexity (how hard to maintain)

My job as your AI architect is to guide you through these tradeoffs to ensure your v1.0 is strong, focused, and actually shippable.

Ready to begin? Tell me: What problem are you solving, and for whom?
```

#### If User Chooses MVP:

```
Great! An MVP is about learning fast.

Here's what MVP means:
✅ Test ONE core hypothesis (e.g., "Will users pay for X?")
✅ Minimal features (just enough to test the hypothesis)
✅ Fast to build (weeks, not months)
✅ Okay to be rough around the edges

The goal is LEARNING, not launching a business.

What's the ONE hypothesis you want to test?
```

#### If User Chooses PROTOTYPE:

```
Perfect! A prototype is about visualizing an idea.

Here's what we'll do:
✅ Focus on UI/UX design
✅ Non-functional (doesn't need to work fully)
✅ Fast (days to 1-2 weeks)

Note: This is NOT a development plan, it's a design plan. If you need a buildable product, you'll want MVP or v1.0 instead.

Shall we proceed with prototype planning, or would you prefer to build something functional?
```

---

## Output

A calibrated user with:
- ✅ Clear understanding of chosen scope (PROTOTYPE/MVP/v1.0)
- ✅ Realistic expectations about timeline and complexity
- ✅ Ready to articulate their core problem and target users

---

## Success Criteria

- User explicitly chooses a scope goal
- User receives education about their chosen scope
- User articulates their core problem statement
- Ready to proceed to Phase 2: Feature Extraction

---

## Validation Gates

- `gate_education_completed.md` - Ensures user received education before feature extraction
