# Validation Gate: Realistic Timeline

## Rule
Project timeline must be realistic given total complexity, team size, and external dependencies.

---

## Baseline Calculation

**Formula:**
```
estimated_weeks = (total_complexity / weekly_capacity) + buffer_weeks
```

**Weekly Capacity (per developer):**
- Junior developer: 8-10 complexity points/week
- Mid-level developer: 12-15 complexity points/week
- Senior developer: 15-20 complexity points/week

**Buffer Multipliers:**
- First-time tech stack: +30% buffer
- External API dependencies: +20% buffer
- Compliance requirements (GDPR, HIPAA): +25% buffer
- Team is remote/distributed: +15% buffer

---

## Validation Process

1. Calculate baseline effort: `total_complexity / team_weekly_capacity`
2. Apply buffer multipliers for risk factors
3. Compare against user's desired timeline
4. If mismatch > 30%, flag as unrealistic

---

## Pass Criteria

- ✅ User timeline ≥ (estimated_weeks * 0.7) [Allow some optimism]
- ✅ If aggressive timeline, user has acknowledged risks
- ✅ No single feature blocks entire timeline (dependencies resolved)
- ✅ Timeline accounts for QA, deployment, buffer time

---

## Failure Conditions

- ❌ User timeline < 50% of estimated effort (dangerously unrealistic)
- ❌ Timeline < 2 weeks for any project with complexity > 30
- ❌ No buffer time allocated (assumes perfect execution)
- ❌ Critical path dependency not accounted for (e.g., waiting for API access)

---

## Reality Check Examples

**Example 1: Unrealistic**
```
Project: SaaS with Stripe integration
Total complexity: 115 points
Team: 1 mid-level developer (13 points/week)
User timeline: 4 weeks

Calculation:
Base effort: 115 / 13 = 8.8 weeks
Buffers: +30% (first-time Stripe) = 11.4 weeks
User timeline: 4 weeks (35% of estimate) ❌ UNREALISTIC
```

**Example 2: Realistic**
```
Project: Simple REST API
Total complexity: 65 points
Team: 1 senior developer (18 points/week)
User timeline: 6 weeks

Calculation:
Base effort: 65 / 18 = 3.6 weeks
Buffers: +15% (API dependencies) = 4.1 weeks
User timeline: 6 weeks (146% of estimate) ✅ REALISTIC (includes buffer)
```

---

## Warning Levels

### 🟢 Green (Comfortable)
- User timeline ≥ 120% of estimate
- Allows for iteration, feedback, polish

### 🟡 Yellow (Tight but doable)
- User timeline = 80-120% of estimate
- Requires good execution, minimal setbacks

### 🔴 Red (Unrealistic)
- User timeline < 80% of estimate
- High risk of failure, cutting corners, or burnout

---

## Error Message Template

```
GATE FAILED: Timeline Unrealistic

Your desired timeline: {user_timeline} weeks
Our estimate: {estimated_weeks} weeks (baseline: {base_weeks} + {buffer_weeks} buffer)

⚠️ Your timeline is {percentage}% of the realistic estimate.

This creates high risk of:
- Incomplete features (rushed implementation)
- Technical debt (skipped testing, poor architecture)
- Team burnout (unsustainable pace)
- Missed deadline (scope creep to meet expectations)

Options:
1. Extend timeline to {recommended_weeks} weeks (recommended)
2. Reduce scope to {reduced_complexity} complexity points
3. Add {additional_devs} developer(s) to team
4. Acknowledge risks and proceed (not recommended)

Breakdown:
- Base effort: {base_weeks} weeks
- Tech stack buffer: +{tech_buffer}% ({tech_buffer_weeks} weeks)
- Dependency buffer: +{dep_buffer}% ({dep_buffer_weeks} weeks)
- Total recommended: {estimated_weeks} weeks

Action: Adjust timeline or reduce scope
```

---

## Purpose

Prevents project failure from unrealistic expectations. Better to have an honest conversation upfront than miss the deadline.

---

## Exemptions

- User has successfully delivered similar projects in this timeframe
- Team has existing codebase/boilerplate to accelerate development
- User explicitly accepts "MVP with known gaps" approach
- Prototype/demo (not production-ready) is acceptable
